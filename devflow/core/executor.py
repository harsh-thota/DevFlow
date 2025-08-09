import asyncio
import subprocess
import time
import sys
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from devflow.core.models import Automation, Command, ExecutionResult, ErrorAction

class AutomationExecutor:
    def __init__(self):
        self.is_running = False
        self.current_automation: Optional[Automation] = None
        self.current_command_index = 0
        self.observers: List[Callable] = []

    def add_observer(self, observer: Callable) -> None:
        self.observers.append(observer)

    def _notify_observers(self, event: str, **kwargs) -> None:
        for observer in self.observers:
            try:
                getattr(observer, event)(**kwargs)
            except AttributeError:
                pass
            except Exception as e:
                print(f"Observer error: {e}")

    async def execute_command(self, command: Command, working_dir: Optional[str] = None, env_vars: Optional[Dict[str, str]] = None) -> ExecutionResult:
        start_time = time.time()
        import os
        env = dict(os.environ)
        if command.environment_vars:
            env.update(command.environment_vars)
        if env_vars:
            env.update(env_vars)
        
        cwd = command.working_directory or working_dir or None
        if cwd:
            cwd = Path(cwd).expanduser().resolve()

        self._notify_observers("on_command_start", command.command)

        try:
            process = await asyncio.create_subprocess_shell(command.command, asyncio.subprocess.PIPE, asyncio.subprocess.PIPE, cwd, env)

            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), command.timeout)
            except asyncio.TimeoutError:
                process.terminate()
                await process.wait()

                result = ExecutionResult(False, -1, "", f"Command timed out after {command.timeout} seconds", time.time() - start_time, command.command)
                self._notify_observers("on_command_complete", command.command, result)
                return result
            
            execution_time = time.time() - start_time
            stdout_str = stdout.decode('utf-8', 'replace') if stdout else ""
            stderr_str = stderr.decode('utf-8', 'replace') if stderr else ""

            result = ExecutionResult(process.returncode == 0, process.returncode or 0, stdout_str, stderr_str, execution_time, command.command)

            self._notify_observers("on_command_complete", command.command, result)
            return result
        except Exception as e:
            result = ExecutionResult(False, -1, "", f"Execution error: {str(e)}", time.time() - start_time, command.command)
            self._notify_observers("on_command_complete", command.command, result)
            return result
        
    async def execute_automation(self, automation: Automation, param_values: Optional[Dict[str, str]] = None) -> List[ExecutionResult]:
        if self.is_running:
            raise RuntimeError("Another automation is already running")
        
        self.is_running = True
        self.current_automation = automation
        self.current_command_index = 0

        if param_values:
            automation = automation.substitute_parameters(param_values)

        results = []
        try:
            self._notify_observers("on_automation_start", automation)

            for i, command in enumerate(automation.commands):
                self.current_command_index = i

                result = await self.execute_command(command)
                results.append(result)

                if not result.succes:
                    if command.on_error == ErrorAction.STOP:
                        self._notify_observers("on_automation_start", automation, "Command failed")
                        break
                    elif command.on_error == ErrorAction.SKIP:
                        continue
                    elif command.on_error == ErrorAction.RETRY:
                        retry_result = await self.execute_command(command)
                        results.append(retry_result)
                        if not retry_result.success and command.on_error == ErrorAction.STOP:
                            break
            
            self._notify_observers("on_automation_complete", automation, results)

        finally:
            self.is_running = False
            self.current_automation = None
            self.current_command_index = 0

        return results
    def stop_execution(self) -> None:
        self.is_running = False
