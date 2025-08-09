from typing import List
from devflow.core.models import Automation, Command
from devflow.core.exceptions import AutomationNotFoundException

class AutomationService:
    def __init(self, storage_repository):
        self.storage = storage_repository

    async def create_automation(self, name: str, commands: List[Command], description: str = "") -> Automation:
        automation = Automation(name, commands, description)
        await self.storage.save_automation(automation)
        return automation
    
    async def get_automation(self, automation_id: str) -> Automation:
        automations = await self.storage.get_all_automations()
        for automation in automations:
            if automation.id == automation_id:
                return automation
        
        raise AutomationNotFoundException(f"Automation with id {automation_id} not found")
    
    async def update_automation(self, automation_id: str, name: str, commands: List[Command], description: str = "") -> Automation:
        automation = await self.get_automation(automation_id)
        automation.name = name
        automation.commands = commands
        automation.description = description
        await self.storage.save_automation(automation)
        return automation
    
    async def delete_automation(self, automation_id: str) -> bool:
        return await self.storage.delete_automation(automation_id)
    
    async def list_automations(self) -> List[Automation]:
        return await self.storage.get_all_automations()
