from __future__ import annotations

import discord

from bot.shared.embeds.common import channel_text, on_off_text
from bot.shared.embeds.constants import DEFAULT_MUSIC_PANEL_EMBED, MUSIC_DETAIL_COLOR, MUSIC_PANEL_COLOR


def build_music_manage_embed(guild: discord.Guild, settings: dict) -> discord.Embed:
    embed = discord.Embed(
        title="음악 시스템 관리",
        description="현재 음악 설정 상태입니다.",
        color=MUSIC_DETAIL_COLOR,
    )
    embed.add_field(name="음악 기능 ON/OFF", value=on_off_text(bool(settings.get("music_enabled", True))), inline=False)
    embed.add_field(name="음악 패널 채널", value=channel_text(guild, settings.get("music_panel_channel_id")), inline=False)
    embed.add_field(name="기본 볼륨", value=str(int(settings.get("music_default_volume", 50))), inline=False)
    embed.add_field(name="유튜브 URL 허용 여부", value="항상 허용", inline=False)
    embed.add_field(name="검색어 재생 허용 여부", value="항상 허용", inline=False)
    embed.add_field(name="자동퇴장 시간", value=f"{int(settings.get('music_auto_disconnect_minutes', 10))}분", inline=False)
    return embed


def build_music_panel_embed(settings: dict) -> discord.Embed:
    panel = settings.get("music_panel_embed", DEFAULT_MUSIC_PANEL_EMBED)
    title = str(panel.get("title", DEFAULT_MUSIC_PANEL_EMBED["title"]))
    description = str(panel.get("description", DEFAULT_MUSIC_PANEL_EMBED["description"]))
    color = int(panel.get("color", DEFAULT_MUSIC_PANEL_EMBED["color"]))

    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text="음성 채널에 입장한 뒤 버튼을 사용하세요.")
    return embed
