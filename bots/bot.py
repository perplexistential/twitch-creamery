import os
import asyncio
import time
import threading
import yaml
import base64, requests, sys
import importlib

from twitchio.ext import commands
import twitchio

from oauth import user

DEFAULT_PREFIX = "!"


class Bot(commands.Bot):
    def __init__(self, name, **kwargs):
        self.name = name
        self.cogs_config = kwargs.pop("cogs", {})
        self._app_token = None

        target_scope = []
        for s in kwargs.get("scopes", []):
            if s == "all_scopes":
                target_scope.extend(user.all_scopes())
            else:
                target_scope.append(s)
        if not target_scope:
            target_scope = user.all_scopes()

        self.client_id = os.environ.get(f"{name.upper()}_CLIENT_ID", "")
        self.client_secret = os.environ.get(f"{name.upper()}_CLIENT_SECRET", "")
        self.auth = user.UserAuthenticator(
            self.client_id,
            self.client_secret,
            target_scope,
            force_verify=False,
            port=kwargs.get("auth_port", None),
        )

        # this will open your default browser and prompt you with the twitch verification website
        self.access_token, self.refresh_token = self.auth.authenticate()
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        # prefix can be a callable, which returns a list of strings or a string...
        # initial_channels can also be a callable which returns a list of strings...
        super().__init__(
            token=self.access_token,
            prefix=kwargs.get("prefix", os.environ.get("DEFAULT_PREFIX", "!")),
            initial_channels=kwargs.get("channels", []),
            nick=name,
        )

        for cog in self.cogs_config:
            cog_module = importlib.import_module(f"cogs.{cog}")
            cog_module.prepare(self)

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()
        # self.run()

    async def event_ready(self):
        # Notify us when everything is ready!
        # We are logged in and ready to chat and use commands...
        print(f"Logged in as | {self.nick}")

    async def event_token_expired(self):
        return user.refresh_access_token(self.access_token)

    def start(self):
        pass
