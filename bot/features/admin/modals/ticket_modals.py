from __future__ import annotations

import discord

from bot.features.ticket.helpers.embeds import build_ticket_manage_embed, build_ticket_panel_embed
from bot.shared.branding.embed_brand import make_embed_with_brand_image
from bot.shared.embeds.constants import DEFAULT_TICKET_PANEL_EMBED
from bot.shared.permissions.admin import ensure_admin


class TicketEmbedSettingsModal(discord.ui.Modal, title="문의 임베드 설정"):
    panel_title = discord.ui.TextInput(
        label="임베드 제목",
        placeholder="예: 문의 센터",
        required=False,
        max_length=100,
    )
    panel_description = discord.ui.TextInput(
        label="임베드 설명",
        placeholder="예: 아래 버튼을 눌러 문의를 생성해주세요.",
        required=False,
        style=discord.TextStyle.paragraph,
        max_length=1500,
    )
    panel_button_label = discord.ui.TextInput(
        label="버튼 텍스트",
        placeholder="예: 문의하기",
        required=False,
        max_length=80,
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        if not await ensure_admin(interaction):
            await interaction.response.send_message("관리자만 사용할 수 있습니다.", ephemeral=True)
            return
        if interaction.guild is None:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return

        bot = interaction.client
        settings = await bot.settings_service.get_guild_settings(interaction.guild.id)
        current = dict(DEFAULT_TICKET_PANEL_EMBED)
        current.update(settings.get("ticket_panel_embed", {}))

        title = self.panel_title.value.strip()
        description = self.panel_description.value.strip()
        button_label = self.panel_button_label.value.strip()

        if title:
            current["title"] = title
        if description:
            current["description"] = description
        if button_label:
            current["button_label"] = button_label

        updated = await bot.settings_service.update_guild_settings(interaction.guild.id, {"ticket_panel_embed": current})
        preview = build_ticket_panel_embed(updated)
        preview_embed, preview_file = make_embed_with_brand_image(preview)
        send_kwargs = {"content": "문의 임베드 설정을 저장했습니다.", "embed": preview_embed, "ephemeral": True}
        if preview_file is not None:
            send_kwargs["file"] = preview_file
        await interaction.response.send_message(**send_kwargs)


class TicketSystemSettingsModal(discord.ui.Modal, title="문의 패널 설정"):
    ticket_panel_channel_id = discord.ui.TextInput(
        label="문의 패널 채널 ID",
        placeholder="예: 1501990278918045806",
        required=False,
        max_length=30,
    )
    ticket_category_id = discord.ui.TextInput(
        label="문의 생성 카테고리 ID",
        placeholder="예: 1501990316474105907",
        required=False,
        max_length=30,
    )
    ticket_log_channel_id = discord.ui.TextInput(
        label="로그 채널 ID",
        placeholder="예: 1501999951146647704",
        required=False,
        max_length=30,
    )
    mention_role_ids = discord.ui.TextInput(
        label="멘션 역할 ID (쉼표로 여러 개)",
        placeholder="예: 1251235, 213525, 99887766",
        required=False,
        style=discord.TextStyle.paragraph,
        max_length=500,
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        if not await ensure_admin(interaction):
            await interaction.response.send_message("관리자만 사용할 수 있습니다.", ephemeral=True)
            return
        if interaction.guild is None:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return

        updates: dict[str, int | list[int]] = {}

        panel_raw = self.ticket_panel_channel_id.value.strip()
        if panel_raw:
            if not panel_raw.isdigit():
                await interaction.response.send_message("문의 패널 채널 ID는 숫자로 입력해주세요.", ephemeral=True)
                return
            panel_channel = interaction.guild.get_channel(int(panel_raw))
            if not isinstance(panel_channel, discord.TextChannel):
                await interaction.response.send_message("문의 패널 채널 ID에 해당하는 텍스트 채널을 찾지 못했습니다.", ephemeral=True)
                return
            updates["ticket_panel_channel_id"] = panel_channel.id

        category_raw = self.ticket_category_id.value.strip()
        if category_raw:
            if not category_raw.isdigit():
                await interaction.response.send_message("문의 생성 카테고리 ID는 숫자로 입력해주세요.", ephemeral=True)
                return
            category = interaction.guild.get_channel(int(category_raw))
            if not isinstance(category, discord.CategoryChannel):
                await interaction.response.send_message("문의 생성 카테고리 ID에 해당하는 카테고리를 찾지 못했습니다.", ephemeral=True)
                return
            updates["ticket_category_id"] = category.id

        log_raw = self.ticket_log_channel_id.value.strip()
        if log_raw:
            if not log_raw.isdigit():
                await interaction.response.send_message("로그 채널 ID는 숫자로 입력해주세요.", ephemeral=True)
                return
            log_channel = interaction.guild.get_channel(int(log_raw))
            if not isinstance(log_channel, discord.TextChannel):
                await interaction.response.send_message("로그 채널 ID에 해당하는 텍스트 채널을 찾지 못했습니다.", ephemeral=True)
                return
            updates["ticket_log_channel_id"] = log_channel.id

        roles_raw = self.mention_role_ids.value.strip()
        if roles_raw:
            role_ids: list[int] = []
            normalized = roles_raw.replace("\n", ",").replace(" ", "")
            tokens = [token for token in normalized.split(",") if token]
            for token in tokens:
                if not token.isdigit():
                    await interaction.response.send_message(
                        "멘션 역할 ID는 숫자만 입력해주세요. 여러 개는 `,`로 구분하세요.",
                        ephemeral=True,
                    )
                    return
                role_id = int(token)
                role = interaction.guild.get_role(role_id)
                if role is None:
                    await interaction.response.send_message(
                        f"멘션 역할 ID `{role_id}` 에 해당하는 역할을 찾지 못했습니다.",
                        ephemeral=True,
                    )
                    return
                role_ids.append(role_id)
            updates["mention_role_ids"] = role_ids

        if not updates:
            await interaction.response.send_message("변경할 값을 하나 이상 입력해주세요.", ephemeral=True)
            return

        updated = await interaction.client.settings_service.update_guild_settings(interaction.guild.id, updates)
        embed = build_ticket_manage_embed(interaction.guild, updated)
        embed, image_file = make_embed_with_brand_image(embed)
        send_kwargs = {"content": "문의 패널 설정을 저장했습니다.", "embed": embed, "ephemeral": True}
        if image_file is not None:
            send_kwargs["file"] = image_file
        await interaction.response.send_message(**send_kwargs)
