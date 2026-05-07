from __future__ import annotations

import discord

from bot.shared.embeds.common import category_text, channel_text, mention_roles_text, open_ticket_count
from bot.shared.embeds.constants import DEFAULT_TICKET_PANEL_EMBED, TICKET_DETAIL_COLOR, TICKET_PANEL_COLOR


def build_ticket_manage_embed(guild: discord.Guild, settings: dict) -> discord.Embed:
    embed = discord.Embed(
        title="문의 시스템 관리",
        description="현재 설정 상태입니다.",
        color=TICKET_DETAIL_COLOR,
    )
    embed.add_field(name="문의 패널 채널", value=channel_text(guild, settings.get("ticket_panel_channel_id")), inline=False)
    embed.add_field(name="문의 생성 카테고리", value=category_text(guild, settings.get("ticket_category_id")), inline=False)
    embed.add_field(name="로그 채널", value=channel_text(guild, settings.get("ticket_log_channel_id")), inline=False)
    embed.add_field(name="멘션 역할 목록", value=mention_roles_text(guild, settings.get("mention_role_ids", [])), inline=False)
    embed.add_field(name="현재 열린 문의 수", value=str(open_ticket_count(guild, settings.get("ticket_category_id"))), inline=True)
    embed.add_field(name="처리된 문의 수", value=str(int(settings.get("ticket_closed_count", 0))), inline=True)
    return embed


def build_ticket_panel_embed(settings: dict) -> discord.Embed:
    panel = settings.get("ticket_panel_embed", DEFAULT_TICKET_PANEL_EMBED)
    title = str(panel.get("title", DEFAULT_TICKET_PANEL_EMBED["title"]))
    description = str(panel.get("description", DEFAULT_TICKET_PANEL_EMBED["description"]))
    color = int(panel.get("color", DEFAULT_TICKET_PANEL_EMBED["color"]))

    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text="문의 버튼을 누르면 관리자에게 티켓이 생성됩니다.")
    return embed


def build_ticket_created_embed(author: discord.Member, title: str, content: str) -> discord.Embed:
    embed = discord.Embed(title="새 문의가 생성되었습니다", color=TICKET_PANEL_COLOR)
    embed.add_field(name="작성자", value=author.mention, inline=False)
    embed.add_field(name="문의 제목", value=title, inline=False)
    embed.add_field(name="문의 내용", value=content, inline=False)
    return embed
