from __future__ import annotations

import discord

from bot.features.ticket.modals.create_ticket_modal import TicketCreateModal
from bot.shared.embeds.constants import DEFAULT_TICKET_PANEL_EMBED


class TicketPanelView(discord.ui.View):
    def __init__(self, button_label: str | None = None) -> None:
        super().__init__(timeout=None)
        resolved = (button_label or "").strip() or str(DEFAULT_TICKET_PANEL_EMBED["button_label"])
        self.create_ticket.label = resolved[:80]

    @discord.ui.button(label="문의하기", style=discord.ButtonStyle.primary, custom_id="lambda:ticket:create")
    async def create_ticket(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        await interaction.response.send_modal(TicketCreateModal())
