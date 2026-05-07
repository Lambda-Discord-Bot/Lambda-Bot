from __future__ import annotations

import discord

from bot.features.music.helpers.embeds import build_music_manage_embed
from bot.shared.branding.embed_brand import make_embed_with_brand_image
from bot.shared.permissions.admin import ensure_admin


class MusicSettingsModal(discord.ui.Modal, title="음악 패널 설정"):
    music_panel_channel_id = discord.ui.TextInput(
        label="음악 패널 채널 ID",
        placeholder="예: 1502013179314835536",
        required=False,
        max_length=30,
    )
    default_volume = discord.ui.TextInput(
        label="기본 볼륨 (1~100)",
        placeholder="예: 50",
        required=False,
        max_length=3,
    )
    auto_disconnect = discord.ui.TextInput(
        label="자동퇴장 시간(분)",
        placeholder="예: 10",
        required=False,
        max_length=4,
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        if not await ensure_admin(interaction):
            await interaction.response.send_message("관리자만 사용할 수 있습니다.", ephemeral=True)
            return
        if interaction.guild is None:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return

        updates: dict[str, int | bool] = {}

        panel_channel_raw = self.music_panel_channel_id.value.strip()
        if panel_channel_raw:
            if not panel_channel_raw.isdigit():
                await interaction.response.send_message("음악 패널 채널 ID는 숫자로 입력해주세요.", ephemeral=True)
                return
            panel_channel = interaction.guild.get_channel(int(panel_channel_raw))
            if not isinstance(panel_channel, discord.TextChannel):
                await interaction.response.send_message("음악 패널 채널 ID에 해당하는 텍스트 채널을 찾지 못했습니다.", ephemeral=True)
                return
            updates["music_panel_channel_id"] = panel_channel.id

        volume_raw = self.default_volume.value.strip()
        if volume_raw:
            if not volume_raw.isdigit():
                await interaction.response.send_message("기본 볼륨은 숫자로 입력해주세요.", ephemeral=True)
                return
            volume = int(volume_raw)
            if volume < 1 or volume > 100:
                await interaction.response.send_message("기본 볼륨은 1~100 사이로 입력해주세요.", ephemeral=True)
                return
            updates["music_default_volume"] = volume

        auto_disconnect_raw = self.auto_disconnect.value.strip()
        if auto_disconnect_raw:
            if not auto_disconnect_raw.isdigit():
                await interaction.response.send_message("자동퇴장 시간은 숫자로 입력해주세요.", ephemeral=True)
                return
            minutes = int(auto_disconnect_raw)
            if minutes < 1 or minutes > 180:
                await interaction.response.send_message("자동퇴장 시간은 1~180분 사이로 입력해주세요.", ephemeral=True)
                return
            updates["music_auto_disconnect_minutes"] = minutes

        if not updates:
            await interaction.response.send_message("변경할 값을 하나 이상 입력해주세요.", ephemeral=True)
            return

        # URL/검색어 재생은 정책상 항상 허용으로 고정
        updates["music_allow_youtube_url"] = True
        updates["music_allow_search"] = True

        settings = await interaction.client.settings_service.update_guild_settings(interaction.guild.id, updates)
        embed = build_music_manage_embed(interaction.guild, settings)
        embed, image_file = make_embed_with_brand_image(embed)
        send_kwargs = {"content": "음악 설정을 저장했습니다.", "embed": embed, "ephemeral": True}
        if image_file is not None:
            send_kwargs["file"] = image_file
        await interaction.response.send_message(**send_kwargs)
