from __future__ import annotations

import json
from datetime import datetime, timezone

import discord


class TicketLogService:
    @staticmethod
    async def channel_to_json_bytes(channel: discord.TextChannel) -> tuple[bytes, str]:
        records: list[dict] = []

        async for message in channel.history(limit=None, oldest_first=True):
            record = {
                "id": message.id,
                "author": {
                    "id": message.author.id,
                    "name": str(message.author),
                    "display_name": getattr(message.author, "display_name", str(message.author)),
                },
                "content": message.content,
                "created_at": message.created_at.isoformat(),
                "attachments": [
                    {
                        "filename": attachment.filename,
                        "url": attachment.url,
                        "size": attachment.size,
                    }
                    for attachment in message.attachments
                ],
                "embeds": [embed.to_dict() for embed in message.embeds],
            }
            records.append(record)

        payload = {
            "channel": {
                "id": channel.id,
                "name": channel.name,
                "guild_id": channel.guild.id,
                "guild_name": channel.guild.name,
            },
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "messages": records,
        }

        data = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        filename = f"ticket-log-{channel.id}.json"
        return data, filename
