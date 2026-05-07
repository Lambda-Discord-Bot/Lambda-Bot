from __future__ import annotations

import discord

from bot.shared.embeds.constants import ADMIN_PANEL_COLOR


def build_admin_panel_embed() -> discord.Embed:
    embed = discord.Embed(
        title="람다 관리자 패널",
        description="버튼으로 시스템을 관리하세요.",
        color=ADMIN_PANEL_COLOR,
    )
    embed.add_field(name="문의 시스템", value="`문의관리` 버튼으로 설정/패널 게시", inline=False)
    embed.add_field(name="음악 시스템", value="`음악관리` 버튼으로 설정/패널 게시", inline=False)
    return embed
