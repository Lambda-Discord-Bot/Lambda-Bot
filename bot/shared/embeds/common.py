from __future__ import annotations

import discord


def channel_text(guild: discord.Guild, channel_id: int | None) -> str:
    if not channel_id:
        return "미설정"
    channel = guild.get_channel(channel_id)
    return channel.mention if channel else f"알 수 없음 ({channel_id})"


def category_text(guild: discord.Guild, category_id: int | None) -> str:
    if not category_id:
        return "미설정"
    category = guild.get_channel(category_id)
    return category.mention if category else f"알 수 없음 ({category_id})"


def mention_roles_text(guild: discord.Guild, role_ids: list[int]) -> str:
    if not role_ids:
        return "없음"

    mentions: list[str] = []
    for role_id in role_ids:
        role = guild.get_role(role_id)
        mentions.append(role.mention if role else f"알 수 없음 ({role_id})")
    return ", ".join(mentions)


def open_ticket_count(guild: discord.Guild, category_id: int | None) -> int:
    if not category_id:
        return 0

    category = guild.get_channel(category_id)
    if not isinstance(category, discord.CategoryChannel):
        return 0
    return len(category.text_channels)


def on_off_text(value: bool) -> str:
    return "ON" if value else "OFF"


def allow_block_text(value: bool) -> str:
    return "허용" if value else "차단"
