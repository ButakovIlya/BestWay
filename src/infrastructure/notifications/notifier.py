from typing import Any

import pusher

from infrastructure.notifications.base import AbstractNotifier


class PusherNotifier(AbstractNotifier):
    PERSONAL_PREFIX = "personal-"
    GENERAL_PREFIX = "general-"

    def __init__(self, app_id: str, key: str, secret: str, cluster: str, ssl: bool = True):
        self.pusher_client = pusher.Pusher(app_id=app_id, key=key, secret=secret, cluster=cluster, ssl=ssl)

    async def send(self, channel: str, data: dict[str, Any]) -> Any:
        return self.pusher_client.trigger(channel, "event", data)

    async def notify_user(
        self, user_id: int, event_type: str, data: dict[str, Any] = {}, error: str | None = None
    ) -> Any:
        channel = f"{self.PERSONAL_PREFIX}{user_id}"
        payload = {"type": event_type, "data": data}
        if error:
            payload["error"] = error

        return await self.send(channel, payload)

    async def notify_general(self, event_type: str, data: dict[str, Any], error: str | None = None) -> Any:
        channel = f"{self.GENERAL_PREFIX}broadcast"
        payload = {"type": event_type, "data": data}
        if error:
            payload["error"] = error
        return await self.send(channel, payload)
