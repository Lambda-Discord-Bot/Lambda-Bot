from __future__ import annotations

import discord

from bot.features.admin.modals.music_settings_modal import MusicSettingsModal
from bot.features.music.helpers.embeds import build_music_manage_embed, build_music_panel_embed
from bot.shared.branding.embed_brand import make_embed_with_brand_image
from bot.shared.permissions.admin import ensure_admin


class MusicManagementQuickView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=120)

    @discord.ui.button(label="음악패널게시", style=discord.ButtonStyle.success, custom_id="lambda:admin:post_music_panel")
    async def post_music_panel(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        if not await ensure_admin(interaction):
            await interaction.response.send_message("관리자만 사용할 수 있습니다.", ephemeral=True)
            return
        if interaction.guild is None:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return

        settings = await interaction.client.settings_service.get_guild_settings(interaction.guild.id)
        channel_id = settings.get("music_panel_channel_id")
        if not channel_id:
            await interaction.response.send_message("음악 패널 채널이 설정되지 않았습니다. `/람다음악관리 패널` 명령어를 먼저 사용해주세요.", ephemeral=True)
            return

        channel = interaction.guild.get_channel(channel_id)
        if not isinstance(channel, discord.TextChannel):
            await interaction.response.send_message("설정된 음악 패널 채널을 찾을 수 없습니다.", ephemeral=True)
            return

        from bot.features.music.views.panel_view import MusicPanelView

        panel_embed = build_music_panel_embed(settings)
        panel_embed, panel_file = make_embed_with_brand_image(panel_embed)
        send_kwargs = {"embed": panel_embed, "view": MusicPanelView()}
        if panel_file is not None:
            send_kwargs["file"] = panel_file
        await channel.send(**send_kwargs)

        await interaction.response.send_message(f"음악 패널을 {channel.mention} 채널에 게시했습니다.", ephemeral=True)

    @discord.ui.button(label="음악패널설정", style=discord.ButtonStyle.primary, custom_id="lambda:admin:music_setting")
    async def music_panel_settings(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        if not await ensure_admin(interaction):
            await interaction.response.send_message("관리자만 사용할 수 있습니다.", ephemeral=True)
            return
        await interaction.response.send_modal(MusicSettingsModal())

    @discord.ui.button(label="음악기능 ON/OFF", style=discord.ButtonStyle.secondary, custom_id="lambda:admin:music_toggle")
    async def toggle_music(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        if not await ensure_admin(interaction):
            await interaction.response.send_message("관리자만 사용할 수 있습니다.", ephemeral=True)
            return
        if interaction.guild is None:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return

        current = await interaction.client.settings_service.get_guild_settings(interaction.guild.id)
        enabled = not bool(current.get("music_enabled", True))
        updated = await interaction.client.settings_service.update_guild_settings(interaction.guild.id, {"music_enabled": enabled})

        embed = build_music_manage_embed(interaction.guild, updated)
        embed, image_file = make_embed_with_brand_image(embed)
        send_kwargs = {
            "content": f"음악 기능을 {'ON' if enabled else 'OFF'}로 변경했습니다.",
            "embed": embed,
            "ephemeral": True,
        }
        if image_file is not None:
            send_kwargs["file"] = image_file
        await interaction.response.send_message(**send_kwargs)

    @discord.ui.button(label="초기화", style=discord.ButtonStyle.danger, custom_id="lambda:admin:music_reset")
    async def reset_music(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        if not await ensure_admin(interaction):
            await interaction.response.send_message("관리자만 사용할 수 있습니다.", ephemeral=True)
            return
        if interaction.guild is None:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return

        updated = await interaction.client.settings_service.reset_music_settings(interaction.guild.id)
        await interaction.client.music_service.stop(interaction.guild)

        embed = build_music_manage_embed(interaction.guild, updated)
        embed, image_file = make_embed_with_brand_image(embed)
        send_kwargs = {"content": "음악 관련 설정을 초기화했습니다.", "embed": embed, "ephemeral": True}
        if image_file is not None:
            send_kwargs["file"] = image_file
        await interaction.response.send_message(**send_kwargs)


async def send_music_management_panel(interaction: discord.Interaction) -> None:
    if interaction.guild is None:
        await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
        return

    settings = await interaction.client.settings_service.get_guild_settings(interaction.guild.id)
    embed = build_music_manage_embed(interaction.guild, settings)
    embed, image_file = make_embed_with_brand_image(embed)
    send_kwargs = {"embed": embed, "view": MusicManagementQuickView(), "ephemeral": True}
    if image_file is not None:
        send_kwargs["file"] = image_file
    await interaction.response.send_message(**send_kwargs)
