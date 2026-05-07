from __future__ import annotations

import discord

from bot.features.ticket.helpers.channel_name import safe_ticket_channel_name
from bot.features.ticket.helpers.embeds import build_ticket_created_embed
from bot.shared.branding.embed_brand import make_embed_with_brand_image


class TicketCreateModal(discord.ui.Modal, title="문의 작성"):
    ticket_title = discord.ui.TextInput(
        label="문의 제목",
        placeholder="문의 제목을 작성해주세요.",
        max_length=100,
    )
    ticket_content = discord.ui.TextInput(
        label="문의 내용",
        style=discord.TextStyle.paragraph,
        placeholder="문의 내용을 자세히 작성해주세요.",
        max_length=1800,
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        if interaction.guild is None or not isinstance(interaction.user, discord.Member):
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return

        bot = interaction.client
        settings = await bot.settings_service.get_guild_settings(interaction.guild.id)

        category_id = settings.get("ticket_category_id")
        if not category_id:
            await interaction.response.send_message(
                "문의 카테고리가 설정되지 않았습니다. 관리자에게 문의해주세요.",
                ephemeral=True,
            )
            return

        category = interaction.guild.get_channel(category_id)
        if not isinstance(category, discord.CategoryChannel):
            await interaction.response.send_message("설정된 문의 카테고리를 찾을 수 없습니다.", ephemeral=True)
            return

        channel_name = safe_ticket_channel_name(
            f"문의-{interaction.user.display_name}-{self.ticket_title.value}",
            fallback=f"문의-{interaction.user.id}",
        )

        bot_member = interaction.guild.me or interaction.guild.get_member(bot.user.id)

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                attach_files=True,
                embed_links=True,
            ),
        }
        if bot_member is not None:
            overwrites[bot_member] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                manage_channels=True,
                read_message_history=True,
            )

        ticket_channel = await interaction.guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites,
            topic=f"ticket_owner:{interaction.user.id}",
            reason="새 문의 생성",
        )

        mention_role_ids = settings.get("mention_role_ids", [])
        mentions = [role.mention for role_id in mention_role_ids if (role := interaction.guild.get_role(role_id))]
        if mentions:
            await ticket_channel.send(" ".join(mentions))

        from bot.features.ticket.views.channel_view import TicketChannelView

        created_embed = build_ticket_created_embed(
            author=interaction.user,
            title=self.ticket_title.value,
            content=self.ticket_content.value,
        )
        created_embed, image_file = make_embed_with_brand_image(created_embed)
        send_kwargs = {"embed": created_embed, "view": TicketChannelView()}
        if image_file is not None:
            send_kwargs["file"] = image_file
        await ticket_channel.send(**send_kwargs)

        await interaction.response.send_message(
            f"문의 채널이 생성되었습니다: {ticket_channel.mention}",
            ephemeral=True,
        )
