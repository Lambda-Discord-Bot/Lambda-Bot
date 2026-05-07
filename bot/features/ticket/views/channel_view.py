from __future__ import annotations

import io

import discord

from bot.services.ticket_log_service import TicketLogService
from bot.shared.branding.embed_brand import make_embed_with_brand_image


class TicketChannelView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(label="문의 닫기", style=discord.ButtonStyle.danger, custom_id="lambda:ticket:close")
    async def close_ticket(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        if interaction.guild is None or not isinstance(interaction.channel, discord.TextChannel):
            await interaction.response.send_message("문의 채널에서만 사용할 수 있습니다.", ephemeral=True)
            return

        bot = interaction.client
        settings = await bot.settings_service.get_guild_settings(interaction.guild.id)
        log_channel_id = settings.get("ticket_log_channel_id")
        log_channel = interaction.guild.get_channel(log_channel_id) if log_channel_id else None

        await interaction.response.defer(ephemeral=True, thinking=True)

        data, filename = await TicketLogService.channel_to_json_bytes(interaction.channel)
        log_file = discord.File(fp=io.BytesIO(data), filename=filename)

        if isinstance(log_channel, discord.TextChannel):
            close_embed = discord.Embed(
                title="문의 로그 저장",
                description=f"채널: {interaction.channel.name}\n닫은 관리자: {interaction.user.mention}",
                color=0xE67E22,
            )
            close_embed, image_file = make_embed_with_brand_image(close_embed)
            files = [log_file]
            if image_file is not None:
                files.append(image_file)
            await log_channel.send(embed=close_embed, files=files)

        await bot.settings_service.increment_ticket_closed_count(interaction.guild.id)
        await interaction.followup.send("문의를 종료하고 채널을 삭제합니다.", ephemeral=True)
        await interaction.channel.delete(reason=f"문의 종료 by {interaction.user}")
