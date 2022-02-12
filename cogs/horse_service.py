from twitchio.ext import commands


class Cog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def horse(self, ctx: commands.Context):
        await ctx.send(f"{ctx.author.name}.horse")

    @commands.Cog.event()
    async def event_message(self, message):
        # An event inside a cog!
        print(message.content)

    @commands.Cog.event("event_ready")
    async def is_ready(self):
        print("horse_service cog is ready!")


def prepare(bot: commands.Bot, channels: List[str]):
    # Load our cog with this module...
    bot.add_cog(Cog(bot))
