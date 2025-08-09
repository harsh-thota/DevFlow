import typer
import asyncio
import os
from typing import Optional

from devflow.storage.json_storage import JsonStorageRepository
from devflow.core.executor import AutomationExecutor
from devflow.core.models import Automation, Command, Parameter, ParameterType

app = typer.Typer("devflow", "DevFlow - Automate your dev workflow")

@app.command()
def run(automation_name: str = typer.Argument(..., "Name of automation to run"), params: Optional[str] = typer.Option(None, "--params", "-p", "Parameters as key=value, key2=value2")) -> None:
    asyncio.run(_run_automation(automation_name, params))

@app.command()
def list() -> None:
    asyncio.run(_list_automations())

@app.command()
def tui() -> None:
    typer.Echo("TUI Coming Soon")

@app.command()
def create_example() -> None:
    asyncio.run(_create_example_automation())

async def _run_automation(automation_name: str, params_str: Optional[str]) -> None:
    storage = JsonStorageRepository()
    executor = AutomationExecutor()

    automations = await storage.get_all_automations()
    automation = None
    for auto in automations:
        if auto.name.lower() == automation_name.lower():
            automation = auto
            break

    if not automation:
        typer.echo(f"Automation '{automation_name}' not found")
        return
    
    param_values = {}
    if params_str:
            for param_pair in params_str.split(","):
                if "=" in param_pair:
                    key, value = param_pair.split("=", 1)
                    param_values[key.strip()] = value.strip()

    typer.echo(f"Running automation: {automation_name}")
    results = await executor.execute_command(automation, param_values)

    for i, result in enumerate(results):
        cmd = automation.commands[i]
        status = "✅" if result.success else "❌"
        typer.echo(f"{status} {cmd.command} (exit code: {result.exit_code})")
        if result.stdout:
            typer.echo(f" Output: {result.stdout.strip()}")
        if result.stderr:
            typer.echo(f" Error: {results.stderr.strip()}")

async def _list_automations() -> None:
    storage = JsonStorageRepository()
    automations = await storage.get_all_automations()

    if not automations:
        typer.echo("No automations found. Use 'devflow create-example' to create one.")
        return
    typer.echo("Available automations:")
    for automation in automations:
        typer.echo(f"  • {automation.name} - {automation.description or 'No description'}")
        typer.echo(f"    Commands: {len(automation.commands)}, Parameters: {len(automation.parameters)}")

async def _create_example_automation() -> None:
    storage = JsonStorageRepository()
    example = Automation("hello-world", [Command("echo Hello, {{name}}!"), Command("echo 'Current Directory:'"), Command("pwd" if os.name != "nt" else "cd")], Parameter("name"), ["example", "demo"])

    await storage.save_automation(example)
    typer.echo(f"Created example automation: {example.name}")
    typer.echo("Try running it with: devflow run hello-world --params name=YourName")


if __name__ == "__main__":
    app()