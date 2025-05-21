
from TikTokLive.events import CommentEvent
from .cb_base import BaseCallback
from datetime import datetime
import utils
import os
import json


class onCommentCallback(BaseCallback):
    async def __call__(self):
        super().__init__(self)

    async def handler(self, event: CommentEvent):
        # wait until ffmpeg start recording
        if not self._client.web.fetch_video_data.is_recording:
            return

        timestamp: int = float(datetime.utcnow().timestamp()) - \
            self._client.web.fetch_video_data.recording_started_at

        chats = {
            "timestamp": utils.get_timestamp(timestamp),
            "author": event.user.nickname,
            "comments": event.comment
        }

        # self._client.logger.info(chats)
        chat_file, _ = os.path.splitext(
            self._client.web.fetch_video_data.output_filename)

        chat_file += ".chat.json"
        chat_data = []
        if os.path.exists(chat_file):
            with open(chat_file, "r", encoding="utf-8") as f:
                try:
                    chat_data = json.load(f)
                except json.JSONDecodeError:
                    chat_data = []

        chat_data.append(chats)
        with open(chat_file, 'w', encoding="utf-8") as c:
            json.dump(chat_data, c, indent=2, ensure_ascii=False)
