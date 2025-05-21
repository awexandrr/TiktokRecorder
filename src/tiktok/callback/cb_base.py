
from TikTokLive import TikTokLiveClient
from config import Config
from ntfy import Notify


class BaseCallback:
    def __init__(
        self,
        ntfy: Notify,
        client: TikTokLiveClient,
        config: Config,
        **kwargs
    ):
        self._config: Config = config
        self._ntfy: Notify = ntfy
        self._client: TikTokLiveClient = client
