# Copyright Alex Morais (thatsamorais@gmail.com) for perplexistential

"""The Bot class based on TwitchIO.commands.Bot."""

import os
import importlib

from twitchio.ext import commands

from tokengen.utils import generate_token, refresh_token
from bots.bot_init import init

DEFAULT_PREFIX = "!"


class Bot(commands.Bot):
    """Bot."""

    def __init__(self, name, **kwargs):
        """init."""
        self.name = name
        self.cogs_config = kwargs.pop("cogs", {})
        self._app_token = None

        self.client_id = os.environ.get(f"{name.upper()}_CLIENT_ID", "")
        self.client_secret = os.environ.get(f"{name.upper()}_CLIENT_SECRET", "")
        access_token = generate_token(
            self.client_id,
            self.client_secret,
            port=kwargs.get("auth_port"),
            scopes=kwargs.get("scopes"),
        )
        self.channels = kwargs.get("channels", [])

        # Initialise our Bot with our access token, prefix and a list of
        # channels to join on boot prefix can be a callable, which returns a
        # list of strings or a string. initial_channels can also be a
        # callable which returns a list of strings...
        init(
            self,
            token=access_token,
            client_secret=self.client_secret,  # will refresh tokens automatically???
            prefix=kwargs.get("prefix", os.environ.get("DEFAULT_PREFIX", "!")),
            initial_channels=self.channels,
            nick=name,
            loop=kwargs.get("loop"),
        )

        for cog in self.cogs_config:
            cog_module = importlib.import_module(f"cogs.{cog}")
            cog_module.prepare(self, kwargs.get("data", {}))

    async def event_ready(self):
        """event_ready."""
        # Notify us when everything is ready!
        # We are logged in and ready to chat and use commands...
        print(f"Logged in as | {self.nick}")

    async def event_token_expired(self):
        """event_token_expired."""
        return refresh_token(self.client_id, self.client_secret)
