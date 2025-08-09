from textual.app import App
from textual.widgets import Header, Footer, Placeholder
from devflow.core.automations import AutomationService

class DevFlowApp(App):
    def __init__(self, automation_service: AutomationService):
        super().__init__()
        self.automaton_service = automation_service
    
    async def on_mount(self) -> None:
        header = Header()
        footer = Footer()
        self.add(header)
        self.add(Placeholder(name="Main Content"))
        self.add(footer)

    async def action_quit(self) -> None:
        await self._shutdown()


if __name__ == "__main__":
    app = DevFlowApp(None)
    app.run()