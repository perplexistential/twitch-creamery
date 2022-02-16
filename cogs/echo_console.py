from twitchio.ext import commands


class Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hello(self, ctx: commands.Context):
        await ctx.send(f"Hello from {self.bot.name}, {ctx.author.name}!")

    @commands.Cog.event()
    async def event_message(self, message):
        # An event inside a cog!
        print(message.content)

    @commands.Cog.event("event_ready")
    async def is_ready(self):
        print("echo_console cog is ready!")


def prepare(bot: commands.Bot):
    # Load our cog with this module...
    bot.add_cog(Cog(bot))
