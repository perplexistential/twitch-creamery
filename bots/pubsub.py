import os  # for importing env vars for the bot to use
from twitchio.ext import commands, pubsub
import twitchio
import asyncio
import time
import threading
import yaml

from tokengen.utils import generate_token

from bots.bot import Bot


async def main(token):

    client = twitchio.Client(token=os.environ.get("PUBSUB_TOKEN", "pubsub"))
    client.pubsub = pubsub.PubSubPool(client)

    @client.event()
    async def event_pubsub_bits(event: pubsub.PubSubBitsMessage):
        pass  # do stuff on bit redemptions

    @client.event()
    async def event_pubsub_channel_points(event: pubsub.PubSubChannelPointsMessage):
        pass  # do stuff on channel point redemptions

    @client.event()
    async def event_pubsub_bits_badge(event: pubsub.PubSubBitsBadgeMessage):
        pass

    @client.event()
    async def event_pubsub_channel_points(event: pubsub.PubSubChannelPointsMessage):
        print(
            f"{event.user} redeemed {event.reward} {event.input} in {event.channel_id} using channel points"
        )

    @client.event()
    async def event_pubsub_moderation_user_action(event):
        if type(event) == pubsub.PubSubModerationActionBanRequest:
            pass
        elif type(event) == pubsub.PubSubModerationActionChannelTerms:
            pass
        elif type(event) == pubsub.PubSubModerationActionModeratorAdd:
            pass
        elif type(event) == pubsub.PubSubModerationAction:
            pass

    # The following two events are not yet supported in twitchio, but are mentioned in the docs
    @client.event()
    async def event_pubsub_channel_subscriptions(event):
        pass

    @client.event()
    async def event_pubsub_whispers(event):
        pass

    channel_id = int(os.environ["CHANNEL_ID"])
    topics = [
        pubsub.channel_points(token)[channel_id],
        pubsub.bits(token)[channel_id],
        pubsub.bits_badge(token)[channel_id],
        # This support is not yet ready in twitchio. maybe soon?
        # pubsub.channel_subscriptions(os.environ['USER_TOKEN'])[channel_id],
        # pubsub.whispers(os.environ['USER_TOKEN'])
    ]

    for mod_id in os.environ.get("MODERATORS", "").strip().split(","):
        if mod_id:
            topics.append(pubsub.moderation_user_action(token)[channel_id][mod_id])

    await client.pubsub.subscribe_topics(topics)
    await client.start()
    await client.close()


DEFAULT_PUBSUB_BOT_NAME = "pubsub"


class PubSubListener(Bot):
    def __init__(self, **kwargs):
        self.name = os.environ.get("PUBSUB_BOT_NAME", DEFAULT_PUBSUB_BOT_NAME)
        self.client_id = os.environ.get(f"{self.name.upper()}_CLIENT_ID", None)
        self.client_secret = os.environ.get(f"{self.name.upper()}_CLIENT_SECRET", None)
        self.access_token = generate_token(
            self.client_id,
            self.client_secret,
            port=kwargs.get("auth_port"),
            scopes=kwargs.get("scopes"),
        )

    def run(self):
        asyncio.create_task(main(self.access_token))
        client.loop.run_until_complete(async_run(self.access_token))

    def start(self):
        thread = threading.Thread(target=asyncio.run, args=(main(self.access_token),))
        thread.daemon = True
        thread.start()
        return thread
