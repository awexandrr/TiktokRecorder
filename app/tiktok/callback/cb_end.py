from TikTokLive.events import LiveEndEvent
from .cb_base import BaseCallback
from ntfy import Opcode
import signal
import asyncio


class onLiveEndCallback(BaseCallback):
    async def __call__(self):
        super().__init__(self)

    async def handler(self, event: LiveEndEvent):
        self._client.logger.info("Livestream has ended")
        if self._client.web.fetch_video_data.is_recording:
            self._client.web.fetch_video_data.stop()

        # wait until ffmpeg done
        while self._client.web.fetch_video_data.ffmpeg:
            await asyncio.sleep(1)

        await self._ntfy.opcode(Opcode.CLIENT_ENDED)
