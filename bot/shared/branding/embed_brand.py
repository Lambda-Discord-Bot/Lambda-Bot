from __future__ import annotations

from pathlib import Path

import discord

from bot import config


BRAND_IMAGE_FILENAME = "Lambda.png"
BRAND_IMAGE_PATH = Path(config.ROOT_DIR) / "assets" / BRAND_IMAGE_FILENAME


def make_embed_with_brand_image(embed: discord.Embed) -> tuple[discord.Embed, discord.File | None]:
    copied = embed.copy()
    if not BRAND_IMAGE_PATH.exists():
        return copied, None

    copied.set_thumbnail(url=f"attachment://{BRAND_IMAGE_FILENAME}")
    file = discord.File(str(BRAND_IMAGE_PATH), filename=BRAND_IMAGE_FILENAME)
    return copied, file
