# Copyright Alex Morais (thatsamorais@gmail.com) for perplexistential

"""horse_service is a cog example."""

from bots.bot import Bot
from twitchio.ext import commands
from .base import BaseCog
import logging

logger = logging.getLogger(__name__)

class Cog(BaseCog):

    def __init__(self, bot: Bot, data={}):
        super().__init__(bot, 'horse_service', **data)

    @commands.command()
    async def horse(self, ctx: commands.Context):
        """horse."""
        await ctx.send(f"{ctx.author.name}.horse")

    @commands.Cog.event("event_ready")
    async def is_ready(self):
        """is_ready."""
        logger.info("horse_service cog is ready!")
