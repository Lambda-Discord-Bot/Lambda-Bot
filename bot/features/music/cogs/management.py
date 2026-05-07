from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from bot.features.music.helpers.embeds import build_music_manage_embed, build_music_panel_embed
from bot.features.music.views.panel_view import MusicPanelView
from bot.shared.branding.embed_brand import make_embed_with_brand_image
from bot.shared.permissions.admin import admin_only


class MusicManagementCog(commands.Cog):
    lambda_music_group = app_commands.Group(name="람다음악관리", description="음악 시스템 설정 명령어")

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @lambda_music_group.command(name="패널", description="음악 패널을 게시할 채널을 설정합니다.")
    @app_commands.describe(channel="음악 패널 채널")
    @admin_only()
    async def set_music_panel_channel(self, interaction: discord.Interaction, channel: discord.TextChannel) -> None:
        if interaction.guild is None:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return
        await self.bot.settings_service.update_guild_settings(interaction.guild.id, {"music_panel_channel_id": channel.id})
        await interaction.response.send_message(f"음악 패널 채널을 {channel.mention} 으로 설정했습니다.", ephemeral=True)

    @lambda_music_group.command(name="볼륨", description="기본 볼륨을 설정합니다.")
    @app_commands.describe(volume="기본 볼륨 (1~100)")
    @admin_only()
    async def set_music_volume(self, interaction: discord.Interaction, volume: app_commands.Range[int, 1, 100]) -> None:
        if interaction.guild is None:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return
        await self.bot.settings_service.update_guild_settings(interaction.guild.id, {"music_default_volume": int(volume)})

        voice_client = interaction.guild.voice_client
        if voice_client is not None and voice_client.source is not None and hasattr(voice_client.source, "volume"):
            voice_client.source.volume = int(volume) / 100

        await interaction.response.send_message(f"기본 볼륨을 {volume}로 설정했습니다.", ephemeral=True)

    @lambda_music_group.command(name="초기화", description="음악 관련 설정을 모두 초기화합니다.")
    @admin_only()
    async def reset_music_settings(self, interaction: discord.Interaction) -> None:
        if interaction.guild is None:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return
        await self.bot.settings_service.reset_music_settings(interaction.guild.id)
        await interaction.response.send_message("음악 시스템 설정을 초기화했습니다.", ephemeral=True)

    @lambda_music_group.command(name="패널게시", description="설정된 음악 패널 채널에 패널을 즉시 게시합니다.")
    @admin_only()
    async def post_music_panel(self, interaction: discord.Interaction) -> None:
        if interaction.guild is None:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return

        settings = await self.bot.settings_service.get_guild_settings(interaction.guild.id)
        channel_id = settings.get("music_panel_channel_id")
        if not channel_id:
            await interaction.response.send_message("음악 패널 채널이 설정되지 않았습니다.", ephemeral=True)
            return

        channel = interaction.guild.get_channel(channel_id)
        if not isinstance(channel, discord.TextChannel):
            await interaction.response.send_message("설정된 음악 패널 채널을 찾을 수 없습니다.", ephemeral=True)
            return

        embed = build_music_panel_embed(settings)
        embed, image_file = make_embed_with_brand_image(embed)
        send_kwargs = {"embed": embed, "view": MusicPanelView()}
        if image_file is not None:
            send_kwargs["file"] = image_file
        await channel.send(**send_kwargs)
        await interaction.response.send_message(f"음악 패널을 {channel.mention} 채널에 게시했습니다.", ephemeral=True)

    @lambda_music_group.command(name="상태", description="음악 시스템 현재 설정 상태를 확인합니다.")
    @admin_only()
    async def music_status(self, interaction: discord.Interaction) -> None:
        if interaction.guild is None:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return

        settings = await self.bot.settings_service.get_guild_settings(interaction.guild.id)
        embed = build_music_manage_embed(interaction.guild, settings)
        embed, image_file = make_embed_with_brand_image(embed)

        send_kwargs = {"embed": embed, "ephemeral": True}
        if image_file is not None:
            send_kwargs["file"] = image_file
        await interaction.response.send_message(**send_kwargs)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MusicManagementCog(bot))
