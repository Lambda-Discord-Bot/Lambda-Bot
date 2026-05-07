from __future__ import annotations

import discord
from discord import app_commands


async def ensure_admin(interaction: discord.Interaction) -> bool:
    user = interaction.user
    if not isinstance(user, discord.Member):
        return False
    return user.guild_permissions.administrator


def admin_only() -> app_commands.Check:
    async def predicate(interaction: discord.Interaction) -> bool:
        if await ensure_admin(interaction):
            return True

        await interaction.response.send_message(
            "이 명령어는 서버 관리자만 사용할 수 있습니다.",
            ephemeral=True,
        )
        return False

    return app_commands.check(predicate)
