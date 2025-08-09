import json
import asyncio
import sys
from pathlib import Path
from typing import List, Optional
from platformdirs import user_data_dir
from concurrent.futures import ThreadPoolExecutor

from devflow.storage.base import StorageRepository
from devflow.core.models import Automation

if sys.version_info >= (3.9):
    async def run_in_thread(func, *args):
        return await asyncio.to_thread(func, *args)
else:
    async def run_in_thread(func, *args):
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(executor, func, *args)
        
class JsonStorageRepository(StorageRepository):
    def __init__(self, storage_path: Optional[str] = None):
        if storage_path is None:
            self.storage_path = Path(user_data_dir("devflow", "devflow")) / "automations.json"
        else:
            self.storage_path = Path(storage_path)

        self.storage_path.parent.mkdir(True, True)
        if not self.storage_path.exists():
            self._write_data([])

    def _read_data(self) -> List[dict]:
        try:
            with open(self.storage_path, 'r', 'utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
        
    def _write_data(self, data: List[dict]) -> None:
        with open(self.storage_path, 'w', 'utf-8') as f:
            json.dump(data, f, 2, str, False)

    async def get_all_automations(self) -> List[Automation]:
        data = await run_in_thread(self._read_data)
        return [Automation.model_validate(item) for item in data]
    
    async def get_automation(self, automation_id: str) -> Optional[Automation]:
        automations = await self.get_all_automations()
        for automation in automations:
            if automation.id == automation_id:
                return automation
        
        return None
    
    async def save_automation(self, automation: Automation) -> None:
        data = await run_in_thread(self._read_data)

        updated = False
        for i, item in enumerate(data):
            if item.get('id') == automation.id:
                data[i] = automation.model_dump()
                updated = True
                break

        if not updated:
            data.append(automation.model_dump())

        await run_in_thread(self._write_data, data)
    
    async def delete_automation(self, automation_id: str) -> bool:
        data = await run_in_thread(self._read_data)

        for i, item in enumerate(data):
            if item.get('id') == automation_id:
                del data[i]
                await run_in_thread(self._write_data, data)
                return True
            
        return False
    
    async def search_automation(self, query: str) -> List[Automation]:
        automations = await self.get_all_automations()
        query_lower = query.lower()

        results = []
        for automation in automations:
            if (query_lower in automation.name.lower() or any(query_lower in tag.lower() for tag in automation.tags) or (automation.description and query_lower in automation.description.lower())):
                results.append(automation)

        return results