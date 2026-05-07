from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from bot.features.ticket.helpers.embeds import build_ticket_manage_embed, build_ticket_panel_embed
from bot.features.ticket.views.panel_view import TicketPanelView
from bot.shared.branding.embed_brand import make_embed_with_brand_image
from bot.shared.permissions.admin import admin_only


class TicketManagementCog(commands.Cog):
    lambda_ticket_group = app_commands.Group(name="람다문의관리", description="문의 시스템 설정 명령어")
    mention_group = app_commands.Group(name="멘션역할", description="문의 생성 시 멘션할 역할 관리", parent=lambda_ticket_group)

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @lambda_ticket_group.command(name="패널", description="문의 패널을 게시할 채널을 설정합니다.")
    @app_commands.describe(channel="문의 패널 채널")
    @admin_only()
    async def set_panel_channel(self, interaction: discord.Interaction, channel: discord.TextChannel) -> None:
        if interaction.guild is None:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return
        await self.bot.settings_service.update_guild_settings(interaction.guild.id, {"ticket_panel_channel_id": channel.id})
        await interaction.response.send_message(f"문의 패널 채널을 {channel.mention} 으로 설정했습니다.", ephemeral=True)

    @lambda_ticket_group.command(name="카테고리", description="문의 채널이 생성될 카테고리를 설정합니다.")
    @app_commands.describe(category="문의 생성 카테고리")
    @admin_only()
    async def set_category(self, interaction: discord.Interaction, category: discord.CategoryChannel) -> None:
        if interaction.guild is None:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return
        await self.bot.settings_service.update_guild_settings(interaction.guild.id, {"ticket_category_id": category.id})
        await interaction.response.send_message(f"문의 카테고리를 {category.mention} 으로 설정했습니다.", ephemeral=True)

    @lambda_ticket_group.command(name="로그", description="문의 로그 JSON 파일을 받을 채널을 설정합니다.")
    @app_commands.describe(channel="로그 채널")
    @admin_only()
    async def set_log_channel(self, interaction: discord.Interaction, channel: discord.TextChannel) -> None:
        if interaction.guild is None:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return
        await self.bot.settings_service.update_guild_settings(interaction.guild.id, {"ticket_log_channel_id": channel.id})
        await interaction.response.send_message(f"로그 채널을 {channel.mention} 으로 설정했습니다.", ephemeral=True)

    @mention_group.command(name="추가", description="문의 생성 시 멘션할 역할을 추가합니다.")
    @app_commands.describe(role="추가할 역할")
    @admin_only()
    async def add_mention_role(self, interaction: discord.Interaction, role: discord.Role) -> None:
        if interaction.guild is None:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return
        _, added = await self.bot.settings_service.add_mention_role(interaction.guild.id, role.id)
        if not added:
            await interaction.response.send_message(f"{role.mention} 역할은 이미 등록되어 있습니다.", ephemeral=True)
            return
        await interaction.response.send_message(f"{role.mention} 역할을 멘션 목록에 추가했습니다.", ephemeral=True)

    @mention_group.command(name="제거", description="등록된 멘션 역할을 제거합니다.")
    @app_commands.describe(role="제거할 역할")
    @admin_only()
    async def remove_mention_role(self, interaction: discord.Interaction, role: discord.Role) -> None:
        if interaction.guild is None:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return
        _, removed = await self.bot.settings_service.remove_mention_role(interaction.guild.id, role.id)
        if not removed:
            await interaction.response.send_message(f"{role.mention} 역할은 목록에 없습니다.", ephemeral=True)
            return
        await interaction.response.send_message(f"{role.mention} 역할을 멘션 목록에서 제거했습니다.", ephemeral=True)

    @mention_group.command(name="목록", description="현재 등록된 멘션 역할 목록을 보여줍니다.")
    @admin_only()
    async def list_mention_roles(self, interaction: discord.Interaction) -> None:
        if interaction.guild is None:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return
        settings = await self.bot.settings_service.get_guild_settings(interaction.guild.id)
        role_ids = settings.get("mention_role_ids", [])
        if not role_ids:
            await interaction.response.send_message("등록된 멘션 역할이 없습니다.", ephemeral=True)
            return
        mentions = [role.mention if (role := interaction.guild.get_role(role_id)) else f"알 수 없음 ({role_id})" for role_id in role_ids]
        await interaction.response.send_message("현재 멘션 역할: " + ", ".join(mentions), ephemeral=True)

    @mention_group.command(name="초기화", description="멘션 역할 목록을 모두 삭제합니다.")
    @admin_only()
    async def clear_mention_roles(self, interaction: discord.Interaction) -> None:
        if interaction.guild is None:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return
        await self.bot.settings_service.clear_mention_roles(interaction.guild.id)
        await interaction.response.send_message("멘션 역할 목록을 초기화했습니다.", ephemeral=True)

    @lambda_ticket_group.command(name="초기화", description="문의 관련 설정을 모두 초기화합니다.")
    @admin_only()
    async def reset_ticket_settings(self, interaction: discord.Interaction) -> None:
        if interaction.guild is None:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return
        await self.bot.settings_service.reset_ticket_settings(interaction.guild.id)
        await interaction.response.send_message("문의 시스템 설정을 모두 초기화했습니다.", ephemeral=True)

    @lambda_ticket_group.command(name="상태", description="문의 시스템 현재 설정 상태를 확인합니다.")
    @admin_only()
    async def view_status(self, interaction: discord.Interaction) -> None:
        if interaction.guild is None:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return
        settings = await self.bot.settings_service.get_guild_settings(interaction.guild.id)
        embed = build_ticket_manage_embed(interaction.guild, settings)
        embed, image_file = make_embed_with_brand_image(embed)
        send_kwargs = {"embed": embed, "ephemeral": True}
        if image_file is not None:
            send_kwargs["file"] = image_file
        await interaction.response.send_message(**send_kwargs)

    @lambda_ticket_group.command(name="패널게시", description="설정된 문의 패널 채널에 패널을 즉시 게시합니다.")
    @admin_only()
    async def post_ticket_panel(self, interaction: discord.Interaction) -> None:
        if interaction.guild is None:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return
        settings = await self.bot.settings_service.get_guild_settings(interaction.guild.id)
        channel_id = settings.get("ticket_panel_channel_id")
        if not channel_id:
            await interaction.response.send_message("문의 패널 채널이 설정되지 않았습니다.", ephemeral=True)
            return
        channel = interaction.guild.get_channel(channel_id)
        if not isinstance(channel, discord.TextChannel):
            await interaction.response.send_message("설정된 문의 패널 채널을 찾을 수 없습니다.", ephemeral=True)
            return

        button_label = settings.get("ticket_panel_embed", {}).get("button_label")
        panel_embed = build_ticket_panel_embed(settings)
        panel_embed, panel_file = make_embed_with_brand_image(panel_embed)
        send_kwargs = {"embed": panel_embed, "view": TicketPanelView(button_label)}
        if panel_file is not None:
            send_kwargs["file"] = panel_file
        await channel.send(**send_kwargs)
        await interaction.response.send_message(f"문의 패널을 {channel.mention} 채널에 게시했습니다.", ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(TicketManagementCog(bot))
