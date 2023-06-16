from twitchio.ext import commands

from token_manager import TokenManager, SecureTokenStorage

import logging

logger = logging.getLogger(__name__)

DEFAULT_PREFIX = "!"

class Bot(commands.Bot):
    def __init__(self, name, env_config, bot_config):
        self.name = name
        self.client_id = env_config[f'{name.upper()}_CLIENT_ID']
        self.client_secret = env_config[f'{name.upper()}_CLIENT_SECRET']
        self.prefix = bot_config.get('prefix', '!')
        self.auth_port = bot_config['auth_port']
        self.channels = bot_config['channels']
        self.scopes = bot_config['scopes']

        # Initialize the TokenManager and get the access and refresh tokens
        self.token_manager = TokenManager(
            self.client_id,
            self.client_secret,
            self.auth_port,
            self.scopes,
            SecureTokenStorage(f"{self.name}_tokens"),
        )

        # Initialize the Bot with the generated token
        self._app_token, self._refresh_token = self.loop.run_until_complete(self.token_manager.generate_token())
        super().__init__(
            command_prefix=self.prefix,
            initial_channels=self.channels,
            loop=bot_config.get("loop"),
        )

        for cog_name, cog_config in bot_config.get('cogs', {}).items():
            self.load_cog(cog_name, cog_config)

    def load_cog(self, cog_name, cog_config):
        """Loads a cog dynamically."""
        try:
            module = __import__(f"cogs.{cog_name}", fromlist=[''])
            cog_class = getattr(module, 'Cog')
            self.add_cog(cog_class(self, cog_config))
        except ImportError:
            logger.info(f"Couldn't load cog {cog_name}")

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def event_ready(self):
        """event_ready."""
        # Notify us when everything is ready!
        # We are logged in and ready to chat and use commands...
        logger.info(f"Logged in as | {self.nick}")

    async def event_token_expired(self):
        """event_token_expired."""
        self._app_token, self._refresh_token = await self.token_manager.refresh_tokens()

    async def run(self):
        async with self:
            await asyncio.Future()  # Run forever

    async def refresh_token_task(self):
        while True:
            await asyncio.sleep(3600)  # Wait for 1 hour
            try:
                self._app_token, self._refresh_token = await self.token_manager.refresh_tokens()
            except Exception as e:
                print(f"Failed to refresh token: {e}")
