

import os
import json
import httpx
import logging
import enum
import base64

from config import Config
from httpx import AsyncClient
from dataclasses import dataclass
from urllib.parse import urlencode
from TikTokLive.client.logger import TikTokLiveLogHandler

config = Config(os.getenv("CONFIG_FILE"))


@dataclass
class Opcode(enum.Enum):
    CLIENT_IDLE: int = 0
    CLIENT_CONNECTED: int = 200
    CLIENT_DISCONNECTED: int = 403
    CLIENT_ENDED: int = 501


class Notify:
    def __init__(self):
        """ Instantiate a route """
        self._logger: logging.Logger = TikTokLiveLogHandler.get_logger()
        self._host: str = config.ntfy.host
        self.message: str = config.ntfy.message

        # The HTTP client
        self._proxy: dict = config.gluetun.proxy
        self._httpx: AsyncClient = AsyncClient(proxy=self._proxy)

    async def send_notification(self, title: str = "") -> dict:
        self._logger.info(F"New livestream found: {title}")
        request = self._httpx.build_request(
            method="POST",
            url=f"{config.ntfy.host}",
            data=json.dumps({
                "message": config.ntfy.message.format(
                    username=config.tiktok.unique_id,
                    title=title
                ),
                "topic": config.ntfy.topic,
                "click": f"https://www.tiktok.com/@{config.tiktok.unique_id}/live",
                "title": "Tiktok notification",
                "actions": [
                    {
                        "action": "view",
                        "label": "Watch stream",
                        "url": f"https://www.tiktok.com/@{config.tiktok.unique_id}/live",
                        "clear": True
                    }
                ]
            })
        )

        return await self._httpx.send(request)

    async def send_error(self, msg: str) -> httpx.Response:
        request = self._httpx.build_request(
            method="POST",
            url=f"{config.ntfy.host}",
            data=json.dumps({
                "message": f"[ERROR] {msg}",
                "topic": config.ntfy.topic,
                "title": "Tiktok notification",
            })
        )

        return await self._httpx.send(request)

    async def send(self, method: str, data: {}) -> httpx.Response:
        request = self._httpx.build_request(
            method=method,
            url=config.ntfy.host,
            data=data
        )

        self._logger.info(F"request: {data}")
        return await self._httpx.send(request)

    async def opcode(self, opcode: Opcode) -> httpx.Response:
        topic = base64.b64encode(
            config.ntfy.topic.encode('utf-8')).decode()

        return await self.send(
            method="POST",
            data=json.dumps({
                "message": json.dumps({"code": opcode.value}),
                "topic": topic
            })
        )

    async def close(self):
        self._httpx.aclose()
