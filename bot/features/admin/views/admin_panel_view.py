from __future__ import annotations

import discord

from bot.features.admin.views.music_management_view import send_music_management_panel
from bot.features.admin.views.ticket_management_view import send_ticket_management_panel
from bot.shared.permissions.admin import ensure_admin


class AdminPanelView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(label="문의관리", style=discord.ButtonStyle.primary, custom_id="lambda:admin:manage_tickets")
    async def manage_tickets(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        if not await ensure_admin(interaction):
            await interaction.response.send_message("관리자만 사용할 수 있습니다.", ephemeral=True)
            return
        await send_ticket_management_panel(interaction)

    @discord.ui.button(label="음악관리", style=discord.ButtonStyle.success, custom_id="lambda:admin:manage_music")
    async def manage_music(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        if not await ensure_admin(interaction):
            await interaction.response.send_message("관리자만 사용할 수 있습니다.", ephemeral=True)
            return
        await send_music_management_panel(interaction)
