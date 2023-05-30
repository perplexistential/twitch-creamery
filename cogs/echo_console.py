# Copyright Alex Morais (thatsamorais@gmail.com) for perplexistential
"""This echo_console Cog is a simple bot."""

from bots.bot import Bot
from twitchio.ext import commands
from .base import BaseCog
import logging

logger = logging.getLogger(__name__)

class Cog(BaseCog):

    def __init__(self, bot: Bot, data={}):
        super().__init__(bot, 'echo_console', **data)

    @commands.command()
    async def hello(self, ctx: commands.Context):
        """hello."""
        await ctx.send(f"Hello from {self.bot.name}, {ctx.author.name}!")

    @commands.Cog.event()
    async def event_message(self, message):
        """Event inside a cog."""
        logger.info(message.content)

    @commands.Cog.event("event_ready")
    async def is_ready(self):
        """is_ready."""
        logger.info("echo_console cog is ready!")
