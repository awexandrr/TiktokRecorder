import asyncio
import utils
import os
import json

from ntfy import Opcode
from .cb_base import BaseCallback
from TikTokLive.events import ConnectEvent
from TikTokLive.client.web.routes.fetch_video_data import VideoFetchFormat
from utils import Downloader


class onConnectCallback(BaseCallback):
    async def __call__(self):
        super().__init__(self)

    async def handler(self, event: ConnectEvent):
        self._client.logger.info(f"Connected to: {event.unique_id}")
        record_data: dict = json.loads(
            self._client.room_info['stream_url']['live_core_sdk_data']['pull_data']['stream_data'])
        self._client.logger.info(
            f"video quality available: {record_data['data'].keys()}")

        # get highest quality if available
        quality = utils.get_highest_quality(record_data['data'])
        self._client.logger.info(f"video quality to download: {quality.value}")

        # Start a recording
        download_file = os.path.join(
            self._config.download.dir,
            self._config.download.get_output_filename(
                room_id=self._client.room_id,
                ext=self._config.download.output_ext
            ),
        )

        if not await self._client.is_live():
            return

        f = download_file
        while os.path.exists(f):
            chat_file, _ = os.path.splitext(download_file)
            f = chat_file + \
                f".{Downloader.c:03}.{self._config.download.output_ext}"

            Downloader.c += 1

        download_file = f
        await self._ntfy.send_notification(title=self._client.room_title)
        self._client.logger.info(f"Room title: { self._client.room_title}")
        self._client.logger.info(f"File name : {download_file}")

        self._client.web.fetch_video_data.start(
            output_fp=download_file,
            room_info=self._client.room_info,
            output_format=self._config.download.output_ext,
            quality=quality,
            record_format=VideoFetchFormat.FLV,
        )

        await self._ntfy.opcode(Opcode.CLIENT_CONNECTED)
