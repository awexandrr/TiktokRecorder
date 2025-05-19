
import re
from typing import Any
from TikTokLive.client.web.routes.fetch_video_data import VideoFetchQuality
from dataclasses import dataclass


@dataclass
class Downloader:
    c: int = 0
    is_finished: bool = False
    is_disconnected: bool = False


def get_highest_quality(resp: dict[str, Any]) -> VideoFetchQuality:
    for i in reversed(VideoFetchQuality):
        if i.value in [k.split("_")[0] for k in resp.keys()]:
            return i

    return VideoFetchQuality.LD


def get_timestamp(s: int) -> str:
    ms = int(s % 1000)
    seconds = int(s % 60)
    minutes = int((s % 3600) // 60)
    hours = int(s // 3600)

    return f"{hours:02}:{minutes:02}:{seconds:02}.{ms:03}"


def get_clean_title(s: str) -> str:
    s = str(s)  # room id
    s = re.sub(r'[^A-Za-z0-9._]+', '_', s)
    s = re.sub(r'[_]+', '_', s)
    s = re.sub(r'[.]+', '.', s)
    s = s.strip('_.')
    if s and s[0].isdigit():
        s = f"t_{s}"

    return s
