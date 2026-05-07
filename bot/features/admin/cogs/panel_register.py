from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from bot.features.admin.helpers.embeds import build_admin_panel_embed
from bot.features.admin.views.admin_panel_view import AdminPanelView
from bot.shared.branding.embed_brand import make_embed_with_brand_image
from bot.shared.permissions.admin import admin_only


class AdminPanelRegisterCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="람다패널등록", description="지정한 채널에 관리자 패널을 게시합니다.")
    @app_commands.describe(channel="관리자 패널을 게시할 텍스트 채널")
    @admin_only()
    async def register_admin_panel(self, interaction: discord.Interaction, channel: discord.TextChannel) -> None:
        if interaction.guild is None:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return

        settings = await self.bot.settings_service.get_guild_settings(interaction.guild.id)

        old_channel_id = settings.get("admin_panel_channel_id")
        old_message_id = settings.get("admin_panel_message_id")
        if old_channel_id and old_message_id:
            old_channel = interaction.guild.get_channel(old_channel_id)
            if isinstance(old_channel, discord.TextChannel):
                try:
                    old_message = await old_channel.fetch_message(old_message_id)
                    await old_message.delete()
                except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                    pass

        async for message in channel.history(limit=50):
            if message.author.id != self.bot.user.id:
                continue
            if not message.embeds:
                continue
            if message.embeds[0].title == "람다 관리자 패널":
                try:
                    await message.delete()
                except (discord.Forbidden, discord.HTTPException):
                    pass

        panel_embed, panel_file = make_embed_with_brand_image(build_admin_panel_embed())
        send_kwargs = {"embed": panel_embed, "view": AdminPanelView()}
        if panel_file is not None:
            send_kwargs["file"] = panel_file
        panel_message = await channel.send(**send_kwargs)

        await self.bot.settings_service.update_guild_settings(
            interaction.guild.id,
            {"admin_panel_channel_id": channel.id, "admin_panel_message_id": panel_message.id},
        )

        await interaction.response.send_message(f"관리자 패널을 {channel.mention} 채널에 등록했습니다.", ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AdminPanelRegisterCog(bot))
