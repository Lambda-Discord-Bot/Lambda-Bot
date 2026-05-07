from __future__ import annotations

import discord

from bot.features.music.helpers.formatters import repeat_mode_label
from bot.features.music.modals.play_modal import MusicPlayModal
from bot.services.music_player_service import MusicServiceError
from bot.shared.branding.embed_brand import make_embed_with_brand_image


class MusicPanelView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(label="재생", style=discord.ButtonStyle.success, custom_id="lambda:music:play")
    async def play_button(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        await interaction.response.send_modal(MusicPlayModal())

    @discord.ui.button(label="일시정지", style=discord.ButtonStyle.secondary, custom_id="lambda:music:pause")
    async def pause_button(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        if interaction.guild is None:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return

        try:
            await interaction.client.music_service.pause(interaction.guild)
            await interaction.response.send_message("일시정지했습니다.", ephemeral=True)
        except MusicServiceError as exc:
            await interaction.response.send_message(str(exc), ephemeral=True)

    @discord.ui.button(label="다시재생", style=discord.ButtonStyle.secondary, custom_id="lambda:music:resume")
    async def resume_button(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        if interaction.guild is None:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return

        try:
            await interaction.client.music_service.resume(interaction.guild)
            await interaction.response.send_message("다시 재생합니다.", ephemeral=True)
        except MusicServiceError as exc:
            await interaction.response.send_message(str(exc), ephemeral=True)

    @discord.ui.button(label="스킵", style=discord.ButtonStyle.primary, custom_id="lambda:music:skip")
    async def skip_button(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        if interaction.guild is None:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return

        try:
            await interaction.client.music_service.skip(interaction.guild)
            await interaction.response.send_message("현재 곡을 스킵했습니다.", ephemeral=True)
        except MusicServiceError as exc:
            await interaction.response.send_message(str(exc), ephemeral=True)

    @discord.ui.button(label="정지", style=discord.ButtonStyle.danger, custom_id="lambda:music:stop")
    async def stop_button(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        if interaction.guild is None:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return

        await interaction.client.music_service.stop(interaction.guild)
        await interaction.response.send_message("재생을 정지하고 대기열을 비웠습니다.", ephemeral=True)

    @discord.ui.button(label="대기열", style=discord.ButtonStyle.secondary, custom_id="lambda:music:queue")
    async def queue_button(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        if interaction.guild is None:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return

        current, queued, repeat_mode = interaction.client.music_service.get_queue_snapshot(interaction.guild.id)

        embed = discord.Embed(title="현재 대기열", color=0x3498DB)
        embed.add_field(name="반복 모드", value=repeat_mode_label(repeat_mode), inline=False)

        if current is not None:
            embed.add_field(name="지금 재생 중", value=f"[{current.title}]({current.webpage_url})", inline=False)
        else:
            embed.add_field(name="지금 재생 중", value="없음", inline=False)

        if queued:
            lines = [f"{index}. [{track.title}]({track.webpage_url})" for index, track in enumerate(queued[:15], start=1)]
            if len(queued) > 15:
                lines.append(f"... 외 {len(queued) - 15}곡")
            embed.add_field(name=f"대기 중 ({len(queued)}곡)", value="\n".join(lines), inline=False)
        else:
            embed.add_field(name="대기 중", value="없음", inline=False)

        embed, image_file = make_embed_with_brand_image(embed)
        send_kwargs = {"embed": embed, "ephemeral": True}
        if image_file is not None:
            send_kwargs["file"] = image_file
        await interaction.response.send_message(**send_kwargs)

    @discord.ui.button(label="반복", style=discord.ButtonStyle.primary, custom_id="lambda:music:repeat")
    async def repeat_button(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        if interaction.guild is None:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return

        mode = interaction.client.music_service.cycle_repeat_mode(interaction.guild.id)
        await interaction.response.send_message(f"반복 모드: {repeat_mode_label(mode)}", ephemeral=True)

    @discord.ui.button(label="셔플", style=discord.ButtonStyle.primary, custom_id="lambda:music:shuffle")
    async def shuffle_button(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        if interaction.guild is None:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return

        size = interaction.client.music_service.shuffle_queue(interaction.guild.id)
        await interaction.response.send_message(f"대기열을 셔플했습니다. (현재 {size}곡)", ephemeral=True)

    @discord.ui.button(label="나가기", style=discord.ButtonStyle.danger, custom_id="lambda:music:leave")
    async def leave_button(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        if interaction.guild is None:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return

        await interaction.client.music_service.disconnect(interaction.guild)
        await interaction.response.send_message("음성 채널에서 나갔습니다.", ephemeral=True)
