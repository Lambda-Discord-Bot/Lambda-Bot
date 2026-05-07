from __future__ import annotations

import discord

from bot.features.admin.modals.ticket_modals import TicketEmbedSettingsModal, TicketSystemSettingsModal
from bot.features.ticket.helpers.embeds import build_ticket_manage_embed, build_ticket_panel_embed
from bot.shared.branding.embed_brand import make_embed_with_brand_image
from bot.shared.permissions.admin import ensure_admin


class TicketManagementQuickView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=120)

    @discord.ui.button(label="문의패널게시", style=discord.ButtonStyle.success, custom_id="lambda:admin:post_ticket_panel")
    async def post_ticket_panel(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        if not await ensure_admin(interaction):
            await interaction.response.send_message("관리자만 사용할 수 있습니다.", ephemeral=True)
            return
        if interaction.guild is None:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return

        settings = await interaction.client.settings_service.get_guild_settings(interaction.guild.id)
        channel_id = settings.get("ticket_panel_channel_id")
        if not channel_id:
            await interaction.response.send_message(
                "문의 패널 채널이 설정되지 않았습니다. `/람다문의관리 패널` 명령어로 먼저 설정해주세요.",
                ephemeral=True,
            )
            return

        channel = interaction.guild.get_channel(channel_id)
        if not isinstance(channel, discord.TextChannel):
            await interaction.response.send_message("설정된 문의 패널 채널을 찾을 수 없습니다.", ephemeral=True)
            return

        from bot.features.ticket.views.panel_view import TicketPanelView

        panel_embed = build_ticket_panel_embed(settings)
        panel_embed, panel_file = make_embed_with_brand_image(panel_embed)
        panel_view = TicketPanelView(settings.get("ticket_panel_embed", {}).get("button_label"))
        send_kwargs = {"embed": panel_embed, "view": panel_view}
        if panel_file is not None:
            send_kwargs["file"] = panel_file
        await channel.send(**send_kwargs)
        await interaction.response.send_message(f"문의 패널을 {channel.mention} 채널에 게시했습니다.", ephemeral=True)

    @discord.ui.button(label="문의패널설정", style=discord.ButtonStyle.primary, custom_id="lambda:admin:ticket_system_setting")
    async def open_ticket_settings(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        if not await ensure_admin(interaction):
            await interaction.response.send_message("관리자만 사용할 수 있습니다.", ephemeral=True)
            return
        await interaction.response.send_modal(TicketSystemSettingsModal())

    @discord.ui.button(label="문의임베드설정", style=discord.ButtonStyle.secondary, custom_id="lambda:admin:ticket_embed_setting")
    async def open_embed_settings(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        if not await ensure_admin(interaction):
            await interaction.response.send_message("관리자만 사용할 수 있습니다.", ephemeral=True)
            return
        await interaction.response.send_modal(TicketEmbedSettingsModal())


async def send_ticket_management_panel(interaction: discord.Interaction) -> None:
    if interaction.guild is None:
        await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
        return

    settings = await interaction.client.settings_service.get_guild_settings(interaction.guild.id)
    embed = build_ticket_manage_embed(interaction.guild, settings)
    embed, image_file = make_embed_with_brand_image(embed)
    send_kwargs = {"embed": embed, "view": TicketManagementQuickView(), "ephemeral": True}
    if image_file is not None:
        send_kwargs["file"] = image_file
    await interaction.response.send_message(**send_kwargs)
