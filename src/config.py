import os
import toml
from typing import Any
from datetime import datetime


class BaseConfig:
    _config: dict[str, Any] = {}
    _dir: str = os.path.join("", "config.toml")

    def __init__(self, **kwargs):
        if kwargs.get('dir'):
            self._dir = os.path.join("", kwargs.get('dir'))

        with open(self._dir, 'r') as cfg:
            self._config = toml.load(cfg)


class Tiktok:
    _cfg: dict[str, Any] = {}

    def __init__(self, *args):
        self.parent: BaseConfig = args[0]
        self._cfg = self.parent._config.get('tiktok')

    @property
    def unique_id(self) -> str:
        return self._cfg.get('unique_id')

    @property
    def ms_token(self) -> str:
        return self._cfg.get('ms_token')


class Ntfy:
    _cfg: dict[str, Any] = {}

    def __init__(self, *args):
        self.parent: BaseConfig = args[0]
        self._cfg = self.parent._config.get('ntfy')

    @property
    def host(self) -> str:
        return self._cfg.get('host')

    @property
    def topic(self) -> str:
        return self._cfg.get('topic')

    @property
    def message(self) -> str:
        return self._cfg.get('message')


class Download:
    _cfg: dict[str, Any] = {}

    def __init__(self, *args):
        self.parent: BaseConfig = args[0]
        self._cfg = self.parent._config.get('download')

    @property
    def dir(self) -> str:
        return self._cfg.get('dir')

    @property
    def output_ext(self) -> str:
        return self._cfg.get('output_ext')

    @property
    def output_regex(self) -> str:
        return self._cfg.get('output_regex')

    def get_output_filename(self, room_id: str, **kwargs) -> str:
        timestamp = kwargs.get('timestamp')
        username = kwargs.get('unique_id')

        if not timestamp:
            timestamp = datetime.now().strftime(self.timestamp_format)

        if not username:
            username = self.parent._config.get('tiktok').get('unique_id')

        return "{username}_{timestamp}_{room_id}.{ext}".format(
            timestamp=timestamp,
            username=username,
            room_id=room_id,
            ext=kwargs.get('ext') or ".mkv"
        )

    @property
    def timestamp_format(self) -> str:
        return self._cfg.get('timestamp_format')


class Gluetun:
    _cfg: dict[str, Any] = {}

    def __init__(self, *args):
        self.parent: BaseConfig = args[0]
        self._cfg = self.parent._config.get('gluetun')

    @property
    def proxy(self) -> str:
        return self._cfg.get('proxy')

    @property
    def api_key(self) -> str:
        return self._cfg.get('api_key')

    @property
    def http_server(self) -> str:
        return self._cfg.get('http_server')


class Config(BaseConfig):
    def __init__(self, dir: str):
        super().__init__(dir=dir)

        self.ntfy = Ntfy(self)
        self.tiktok = Tiktok(self)
        self.download = Download(self)
        self.gluetun = Gluetun(self)
