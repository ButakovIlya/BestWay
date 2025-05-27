from typing import Any, Optional

import httpx

from application.events import EventType
from infrastructure.notifications.base import AbstractNotifier


class CentrifugoNotifier(AbstractNotifier):
    PERSONAL_PREFIX = "personal:"
    GENERAL_PREFIX = "general:"

    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.api_key = api_key

    async def send(self, channel: str, data: Optional[dict[str, Any]] = None) -> Any:
        payload = {"method": "publish", "params": {"channel": channel, "data": data}}
        headers = {"Authorization": f"apikey {self.api_key}"}
        async with httpx.AsyncClient() as client:
            response = await client.post(self.api_url, json=payload, headers=headers)
            response.raise_for_status()
            return {"status": response.status_code}

    async def notify_user(
        self, user_id: int, event_type: EventType, data: Optional[dict[str, Any]] = None
    ) -> Any:
        channel = f"{self.PERSONAL_PREFIX}{user_id}"
        print(f"channel_name:{channel}")
        return await self.send(channel, {"type": event_type.value, "data": data})

    async def notify_general(self, event_type: EventType, data: Optional[dict[str, Any]] = None) -> Any:
        channel = f"{self.GENERAL_PREFIX}broadcast"
        return await self.send(channel, {"type": event_type.value, "data": data})
