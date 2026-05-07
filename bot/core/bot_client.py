from __future__ import annotations

import logging

import discord
from discord.ext import commands

from bot import config
from bot.features.admin.views.admin_panel_view import AdminPanelView
from bot.features.music.services.player import MusicPlayerService
from bot.features.music.views.panel_view import MusicPanelView
from bot.features.ticket.views.channel_view import TicketChannelView
from bot.features.ticket.views.panel_view import TicketPanelView
from bot.services.settings_service import SettingsService


class LambdaBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.guilds = True
        intents.members = True
        intents.messages = True
        intents.message_content = True

        super().__init__(command_prefix="!", intents=intents)
        self.settings_service = SettingsService(config.SETTINGS_FILE)
        self.music_service = MusicPlayerService(self)
        self._guild_cleanup_done = False

    async def setup_hook(self) -> None:
        await self.load_extension("bot.features.admin.cogs.panel_register")
        await self.load_extension("bot.features.ticket.cogs.management")
        await self.load_extension("bot.features.music.cogs.management")

        self.add_view(AdminPanelView())
        self.add_view(TicketPanelView())
        self.add_view(TicketChannelView())
        self.add_view(MusicPanelView())

        if config.TEST_GUILD_ID:
            guild = discord.Object(id=int(config.TEST_GUILD_ID))
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            logging.info("Synced commands to test guild: %s", config.TEST_GUILD_ID)
        else:
            await self.tree.sync()
            logging.info("Synced global commands")

    async def on_ready(self) -> None:
        if self.user is not None:
            logging.info("Logged in as %s (%s)", self.user, self.user.id)

        if not config.TEST_GUILD_ID and not self._guild_cleanup_done:
            cleared_count = 0
            for guild in self.guilds:
                try:
                    self.tree.clear_commands(guild=guild)
                    await self.tree.sync(guild=guild)
                    cleared_count += 1
                except discord.HTTPException:
                    logging.exception("Guild command cleanup failed: %s", guild.id)
            self._guild_cleanup_done = True
            logging.info("Cleared guild-level commands in %s guild(s) on ready", cleared_count)
