from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
from uuid import uuid4

class ParameterType(str, Enum):
    TEXT = "text"
    PASSWORD = "password"
    CHOICE = "choice"
    BOOLEAN = "boolean"

class ErrorAction(str, Enum):
    STOP = "stop"
    SKIP = "skip"
    RETRY = "retry"
    CONTINUE = "continue"

class Parameter(BaseModel):
    name: str
    type: ParameterType = ParameterType.TEXT
    description: Optional[str] = None
    default_value: Optional[str] = None
    required: bool = True
    choices: Optional[List[str]] = None

class Command(BaseModel):
    command: str
    description: Optional[str] = None
    timeout: int = 30
    on_error: ErrorAction = ErrorAction.STOP
    working_directory: Optional[str] = None
    environment_vars: Optional[Dict[str, str]] = None

class ExecutionResult(BaseModel):
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    execution_time: float
    command: str

class Automation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4))
    name: str
    description: Optional[str] = None
    commands: List[Command]
    parameters: List[Parameter] = []
    tags: List[str] = []
    created_at: datetime = Field(default_factory=datetime.now)
    last_run: Optional[datetime] = None
    run_count: int = 0

    def substitute_parameters(self, param_values: Dict[str, str]) -> "Automation":
        substituted_commands = []
        for cmd in self.commands:
            substituted_command = cmd.command
            for param_name, param_value in param_values.items():
                substituted_command = substituted_command.replace(f"{{{{{param_name}}}}}", param_value)
                substituted_commands.append(Command(substituted_command, cmd.description, cmd.timeout, cmd.on_error, cmd.working_directory, cmd.environment_vars))

        return self.model_copy({"commands": substituted_commands})