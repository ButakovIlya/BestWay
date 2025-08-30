import logging
from typing import Any

import pusher
from requests import ReadTimeout, RequestException

from infrastructure.notifications.base import AbstractNotifier

logger = logging.getLogger(__name__)


class PusherNotifier(AbstractNotifier):
    PERSONAL_PREFIX = "personal-"
    GENERAL_PREFIX = "general-"

    def __init__(
        self, app_id: str, key: str, secret: str, cluster: str, ssl: bool = True, timeout: int = 5
    ):
        self.pusher_client = pusher.Pusher(
            app_id=app_id,
            key=key,
            secret=secret,
            cluster=cluster,
            ssl=ssl,
            timeout=timeout,
        )

    async def send(self, channel: str, data: dict[str, Any]) -> Any:
        try:
            return self.pusher_client.trigger(channel, "event", data)
        except ReadTimeout as e:
            logger.warning(f"Pusher timeout when sending to {channel}: {e}")
            return None
        except RequestException as e:
            logger.error(f"Pusher request error when sending to {channel}: {e}")
            return None
        except Exception as e:
            logger.exception(f"Unexpected Pusher error: {e}")
            return None

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
