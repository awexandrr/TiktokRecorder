from TikTokLive.events import DisconnectEvent
from .cb_base import BaseCallback
from ntfy import Opcode


class onDisconnectCallback(BaseCallback):
    async def __call__(self):
        super().__init__(self)

    async def handler(self, event: DisconnectEvent):
        self._client.logger.info("Disconnected")
        await self._ntfy.opcode(Opcode.CLIENT_DISCONNECTED)

        if self._client.web.fetch_video_data.is_recording:
            self._client.web.fetch_video_data.stop()
