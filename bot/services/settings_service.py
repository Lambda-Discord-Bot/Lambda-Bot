from __future__ import annotations

import asyncio
import copy
import json
from pathlib import Path

from bot.shared.embeds.constants import DEFAULT_MUSIC_PANEL_EMBED, DEFAULT_TICKET_PANEL_EMBED


class SettingsService:
    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        self._lock = asyncio.Lock()
        self._ensure_file()

    def _ensure_file(self) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self.file_path.write_text("{}", encoding="utf-8")

    def _load(self) -> dict:
        try:
            return json.loads(self.file_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}

    def _save(self, data: dict) -> None:
        self.file_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _default_settings(self) -> dict:
        return {
            "admin_panel_channel_id": None,
            "admin_panel_message_id": None,
            "ticket_panel_channel_id": None,
            "ticket_category_id": None,
            "ticket_log_channel_id": None,
            "ticket_closed_count": 0,
            "mention_role_ids": [],
            "ticket_panel_embed": copy.deepcopy(DEFAULT_TICKET_PANEL_EMBED),
            "music_enabled": True,
            "music_panel_channel_id": None,
            "music_default_volume": 50,
            "music_allow_youtube_url": True,
            "music_allow_search": True,
            "music_auto_disconnect_minutes": 10,
            "music_panel_embed": copy.deepcopy(DEFAULT_MUSIC_PANEL_EMBED),
        }

    async def get_guild_settings(self, guild_id: int) -> dict:
        async with self._lock:
            raw = self._load()
            key = str(guild_id)
            current = raw.get(key)
            if not isinstance(current, dict):
                current = self._default_settings()
                raw[key] = current
                self._save(raw)

            merged = self._default_settings()
            merged.update(current)
            return merged

    async def update_guild_settings(self, guild_id: int, updates: dict) -> dict:
        async with self._lock:
            raw = self._load()
            key = str(guild_id)
            current = raw.get(key)
            if not isinstance(current, dict):
                current = self._default_settings()

            current.update(updates)
            raw[key] = current
            self._save(raw)

            merged = self._default_settings()
            merged.update(current)
            return merged

    async def add_mention_role(self, guild_id: int, role_id: int) -> tuple[dict, bool]:
        settings = await self.get_guild_settings(guild_id)
        role_ids = list(settings.get("mention_role_ids", []))
        if role_id in role_ids:
            return settings, False

        role_ids.append(role_id)
        settings = await self.update_guild_settings(guild_id, {"mention_role_ids": role_ids})
        return settings, True

    async def remove_mention_role(self, guild_id: int, role_id: int) -> tuple[dict, bool]:
        settings = await self.get_guild_settings(guild_id)
        role_ids = list(settings.get("mention_role_ids", []))
        if role_id not in role_ids:
            return settings, False

        role_ids.remove(role_id)
        settings = await self.update_guild_settings(guild_id, {"mention_role_ids": role_ids})
        return settings, True

    async def clear_mention_roles(self, guild_id: int) -> dict:
        return await self.update_guild_settings(guild_id, {"mention_role_ids": []})

    async def reset_ticket_settings(self, guild_id: int) -> dict:
        reset = {
            "ticket_panel_channel_id": None,
            "ticket_category_id": None,
            "ticket_log_channel_id": None,
            "ticket_closed_count": 0,
            "mention_role_ids": [],
            "ticket_panel_embed": copy.deepcopy(DEFAULT_TICKET_PANEL_EMBED),
        }
        return await self.update_guild_settings(guild_id, reset)

    async def reset_music_settings(self, guild_id: int) -> dict:
        reset = {
            "music_enabled": True,
            "music_panel_channel_id": None,
            "music_default_volume": 50,
            "music_allow_youtube_url": True,
            "music_allow_search": True,
            "music_auto_disconnect_minutes": 10,
            "music_panel_embed": copy.deepcopy(DEFAULT_MUSIC_PANEL_EMBED),
        }
        return await self.update_guild_settings(guild_id, reset)

    async def increment_ticket_closed_count(self, guild_id: int) -> int:
        async with self._lock:
            raw = self._load()
            key = str(guild_id)
            current = raw.get(key)
            if not isinstance(current, dict):
                current = self._default_settings()

            closed_count = int(current.get("ticket_closed_count", 0)) + 1
            current["ticket_closed_count"] = closed_count
            raw[key] = current
            self._save(raw)
            return closed_count
