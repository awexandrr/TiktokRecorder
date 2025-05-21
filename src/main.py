
import os
import sys
import httpx
import asyncio
from asyncio import CancelledError, Task

from ntfy import Notify
from config import Config
from TikTokLive import TikTokLiveClient
from TikTokLive.client.logger import LogLevel
from TikTokLive.events import DisconnectEvent
from ffmpy import FFRuntimeError
from utils import cancel_task
from tiktok import app, recording

VideoQualityOrder = ["ld", "sd", "hd", "uhd", "origin"]
_config_file = os.environ.get("CONFIG_FILE") or "config.toml"
config = Config(_config_file)

async def main():
    """ main entry """
    username = config.tiktok.unique_id
    proxy = httpx.Proxy(config.gluetun.proxy)
    ntfy = Notify()

    client = None
    status = True
    client_tasks: Task = None
    recorder_tasks: Task = None

    while True:
        if not client or not client.web:
            client = TikTokLiveClient(
                unique_id=f"@{username}", web_proxy=proxy)
            client.logger.setLevel(LogLevel.INFO.value)
            client = app(client, ntfy, config)

        while not await client.is_live():
            if status:
                client.logger.info("CLIENT IDLE")

            status = False
            await asyncio.sleep(60)

        try:
            status = True
            client_tasks = await client.start(fetch_room_info=True)
            recorder_tasks = asyncio.get_event_loop().create_task(
                recording(client, client_tasks))

            await asyncio.gather(client_tasks, recorder_tasks)

        except CancelledError as e:
            client.logger.error(F"{e}")

        except FFRuntimeError as e:
            client.logger.error(F"{e}")

        except Exception as e:
            client.logger.error(F"{e}")

        finally:
            client.logger.error("client stopped")
            await cancel_task(client_tasks)
            await cancel_task(recorder_tasks)

if __name__ == '__main__':
    asyncio.run(main())
