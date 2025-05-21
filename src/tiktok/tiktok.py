
import asyncio
import signal
from config import Config
from TikTokLive import TikTokLiveClient
from ntfy import Notify

from .callback import *
from TikTokLive.events import ConnectEvent, DisconnectEvent, CommentEvent, LiveEndEvent
from utils import cancel_task

def app(client: TikTokLiveClient, ntfy: Notify, config: Config, **kwargs) -> TikTokLiveClient:
    on_connect = onConnectCallback(
        client=client, ntfy=ntfy, config=config)
    on_disconnect = onDisconnectCallback(
        client=client, ntfy=ntfy, config=config)
    on_comment = onCommentCallback(
        client=client, ntfy=ntfy, config=config)
    on_end = onLiveEndCallback(
        client=client, ntfy=ntfy, config=config)

    client.on(event=ConnectEvent)(on_connect.handler)
    client.on(event=DisconnectEvent)(on_disconnect.handler)
    client.on(event=CommentEvent)(on_comment.handler)
    client.on(event=LiveEndEvent)(on_end.handler)

    return client

async def recording(client: TikTokLiveClient, task: asyncio.Task):
    is_recording = False
    while True:
        await asyncio.sleep(10)
        if not await client.is_live():
            continue

        if not is_recording and client.web.fetch_video_data.is_recording:
            is_recording = True

        if not is_recording:
            continue

        if client.web.fetch_video_data.is_recording:
            continue

        is_recording = False
        client.logger.info("recorder is offline")
        client.web.fetch_video_data.ffmpeg.process.send_signal(
            signal.SIGTERM)

        await cancel_task(task)