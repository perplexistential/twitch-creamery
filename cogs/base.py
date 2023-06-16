from twitchio.ext import commands

class BaseCog(commands.Cog):
    def __init__(self, bot, name, **kwargs):
        self.bot = bot
        self.name = name
        # Initialize cog with specific kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
        # Load cog-specific configuration parameters
        self.load_config()

    def load_config(self):
        pass # to be overridden by each cog as necessary
