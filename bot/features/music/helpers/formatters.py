from __future__ import annotations

from bot.services.music_player_service import RepeatMode


def repeat_mode_label(mode: RepeatMode) -> str:
    if mode == RepeatMode.ONE:
        return "현재 곡 반복"
    if mode == RepeatMode.ALL:
        return "전체 반복"
    return "반복 없음"


def format_duration(seconds: int | None) -> str:
    if seconds is None:
        return "알 수 없음"
    minutes, remain = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{remain:02d}"
    return f"{minutes}:{remain:02d}"
