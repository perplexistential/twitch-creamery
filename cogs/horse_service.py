# Copyright Alex Morais (thatsamorais@gmail.com) for perplexistential

"""horse_service is a cog example."""

from twitchio.ext import commands


class Cog(commands.Cog):
    """Cog."""

    def __init__(self, bot, data={}):
        """init."""
        self.bot = bot

    @commands.command()
    async def horse(self, ctx: commands.Context):
        """horse."""
        await ctx.send(f"{ctx.author.name}.horse")

    @commands.Cog.event("event_ready")
    async def is_ready(self):
        """is_ready."""
        print("horse_service cog is ready!")


def prepare(bot: commands.Bot, data={}):
    """Load our cog with this module."""
    bot.add_cog(Cog(bot, data=data))
