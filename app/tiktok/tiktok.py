
from config import Config
from TikTokLive import TikTokLiveClient
from ntfy import Notify

from .callback import *
from TikTokLive.events import ConnectEvent, DisconnectEvent, CommentEvent, LiveEndEvent


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
