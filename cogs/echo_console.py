# Copyright Alex Morais (thatsamorais@gmail.com) for perplexistential
"""This echo_console Cog is a simple bot."""

from twitchio.ext import commands


class Cog(commands.Cog):
    """Cog."""

    def __init__(self, bot, data={}):
        """init."""
        self.bot = bot

    @commands.command()
    async def hello(self, ctx: commands.Context):
        """hello."""
        await ctx.send(f"Hello from {self.bot.name}, {ctx.author.name}!")

    @commands.Cog.event()
    async def event_message(self, message):
        """Event inside a cog."""
        print(message.content)

    @commands.Cog.event("event_ready")
    async def is_ready(self):
        """is_ready."""
        print("echo_console cog is ready!")


def prepare(bot: commands.Bot, data={}):
    """Load our cog with this module."""
    bot.add_cog(Cog(bot, data=data))
