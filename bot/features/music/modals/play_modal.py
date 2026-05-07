from __future__ import annotations

import logging

import discord

from bot.services.music_player_service import MusicServiceError
from bot.shared.branding.embed_brand import make_embed_with_brand_image
from bot.features.music.helpers.formatters import format_duration

logger = logging.getLogger(__name__)


class MusicPlayModal(discord.ui.Modal, title="음악 재생"):
    query = discord.ui.TextInput(
        label="노래 제목 또는 유튜브 URL",
        placeholder="예: NewJeans - Ditto / https://youtube.com/watch?v=...",
        max_length=300,
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        if interaction.guild is None or not isinstance(interaction.user, discord.Member):
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return

        settings = await interaction.client.settings_service.get_guild_settings(interaction.guild.id)
        if not bool(settings.get("music_enabled", True)):
            await interaction.response.send_message("현재 서버에서 음악 기능이 OFF 상태입니다.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True, thinking=True)

        try:
            await interaction.client.music_service.connect_to_member_voice(interaction.user)
            track, started_now, queue_size = await interaction.client.music_service.enqueue(
                interaction.guild,
                str(self.query.value),
                interaction.user,
                settings,
            )
        except MusicServiceError as exc:
            await interaction.followup.send(str(exc), ephemeral=True)
            return
        except Exception as exc:  # noqa: BLE001
            logger.exception("Unexpected error while handling music play request")
            await interaction.followup.send(
                f"재생 요청 처리 중 오류가 발생했습니다.\n`{exc.__class__.__name__}: {exc}`",
                ephemeral=True,
            )
            return

        status_text = "지금 바로 재생 시작" if started_now else "대기열에 추가 완료"
        status_emoji = "▶️" if started_now else "📥"

        embed = discord.Embed(
            title=f"{status_emoji} Lambda Music Request",
            description=f"**[{track.title}]({track.webpage_url})**",
            color=0x00D1B2 if started_now else 0x3498DB,
        )
        embed.add_field(name="요청자", value=interaction.user.mention, inline=True)
        embed.add_field(name="곡 길이", value=format_duration(track.duration), inline=True)
        embed.add_field(name="상태", value=status_text, inline=True)
        embed.add_field(name="대기열", value=f"`{queue_size}`곡", inline=True)
        embed.add_field(name="기본 볼륨", value=f"`{int(settings.get('music_default_volume', 50))}`", inline=True)
        embed.add_field(name="반복 모드", value="`반복 없음`", inline=True)
        if track.uploader:
            embed.add_field(name="채널/아티스트", value=track.uploader, inline=False)
        embed.add_field(name="바로가기", value=f"[유튜브에서 열기]({track.webpage_url})", inline=False)

        if track.thumbnail_url:
            embed.set_image(url=track.thumbnail_url)

        embed.set_footer(text="Lambda Music Panel")
        embed.timestamp = discord.utils.utcnow()
        embed, image_file = make_embed_with_brand_image(embed)

        send_kwargs = {"embed": embed, "ephemeral": True}
        if image_file is not None:
            send_kwargs["file"] = image_file
        await interaction.followup.send(**send_kwargs)
