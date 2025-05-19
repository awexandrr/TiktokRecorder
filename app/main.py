
import os
import sys
import httpx
import asyncio

from tiktok import app
from config import Config
from TikTokLive import TikTokLiveClient
from TikTokLive.client.logger import LogLevel
from TikTokLive.events import DisconnectEvent
from ffmpy import FFRuntimeError
from ntfy import Notify, Opcode

VideoQualityOrder = ["ld", "sd", "hd", "uhd", "origin"]
_config_file = os.environ.get("CONFIG_FILE") or "config.toml"
config = Config(_config_file)


async def wait_task(tasks: asyncio.Task = None) -> None:
    if not tasks:
        return

    try:
        await asyncio.wait_for(tasks, timeout=10)
    except asyncio.TimeoutError:
        tasks.cancel()
        await tasks


async def main():
    """ main entry """
    username = config.tiktok.unique_id
    proxy = httpx.Proxy(config.gluetun.proxy)
    ntfy = Notify()

    client = None
    status = False
    tasks: asyncio.Task = None

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
            tasks = await client.connect(fetch_room_info=True)

        except Exception as e:
            client.logger.info(F"{e}")

        finally:
            await wait_task(tasks)
            await client.disconnect(close_client=False)

if __name__ == '__main__':
    asyncio.run(main())
