from abc import ABC, abstractmethod
from typing import List, Optional
from devflow.core.models import Automation

class StorageRepository(ABC):
    @abstractmethod
    async def get_all_automations(self) -> List[Automation]:
        pass

    @abstractmethod
    async def get_automation(self, automation_id: str) -> Optional[Automation]:
        pass

    @abstractmethod
    async def save_automation(self, automation: Automation) -> None:
        pass

    @abstractmethod
    async def delete_automation(self, automation_id: str) -> bool:
        pass

    @abstractmethod
    async def search_automation(self, automation_id: str) -> List[Automation]:
        pass