from bot.features.admin.helpers.embeds import build_admin_panel_embed
from bot.features.music.helpers.embeds import build_music_manage_embed, build_music_panel_embed
from bot.features.ticket.helpers.embeds import (
    build_ticket_created_embed,
    build_ticket_manage_embed,
    build_ticket_panel_embed,
)
from bot.shared.embeds.constants import (
    ADMIN_PANEL_COLOR,
    DEFAULT_MUSIC_PANEL_EMBED,
    DEFAULT_TICKET_PANEL_EMBED,
    MUSIC_DETAIL_COLOR,
    MUSIC_PANEL_COLOR,
    TICKET_DETAIL_COLOR,
    TICKET_PANEL_COLOR,
)

__all__ = [
    "ADMIN_PANEL_COLOR",
    "TICKET_PANEL_COLOR",
    "TICKET_DETAIL_COLOR",
    "MUSIC_PANEL_COLOR",
    "MUSIC_DETAIL_COLOR",
    "DEFAULT_TICKET_PANEL_EMBED",
    "DEFAULT_MUSIC_PANEL_EMBED",
    "build_admin_panel_embed",
    "build_ticket_manage_embed",
    "build_ticket_panel_embed",
    "build_ticket_created_embed",
    "build_music_manage_embed",
    "build_music_panel_embed",
]
