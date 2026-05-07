from __future__ import annotations

from typing import Final


ADMIN_PANEL_COLOR: Final[int] = 0x5865F2
TICKET_PANEL_COLOR: Final[int] = 0x57F287
TICKET_DETAIL_COLOR: Final[int] = 0xFEE75C
MUSIC_PANEL_COLOR: Final[int] = 0x1ABC9C
MUSIC_DETAIL_COLOR: Final[int] = 0x2ECC71

DEFAULT_TICKET_PANEL_EMBED: Final[dict[str, str | int]] = {
    "title": "문의 센터",
    "description": "아래 버튼을 눌러 문의를 생성해주세요.",
    "button_label": "문의하기",
    "color": TICKET_PANEL_COLOR,
}

DEFAULT_MUSIC_PANEL_EMBED: Final[dict[str, str | int]] = {
    "title": "람다 음악 패널",
    "description": "아래 버튼으로 음악을 재생/제어하세요.",
    "color": MUSIC_PANEL_COLOR,
}
