from __future__ import annotations

import asyncio
import logging

from bot import config
from bot.core.bot_client import LambdaBot
from bot.core.single_instance import SingleInstanceLock


async def start_bot() -> None:
    if not config.DISCORD_TOKEN:
        raise RuntimeError("DISCORD_TOKEN 이 설정되지 않았습니다. .env 파일을 확인하세요.")

    bot = LambdaBot()
    await bot.start(config.DISCORD_TOKEN)


def run_bot() -> None:
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s")
    SingleInstanceLock(config.DATA_DIR / ".bot.lock").acquire()
    asyncio.run(start_bot())
