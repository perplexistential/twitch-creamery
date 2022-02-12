import os  # for importing env vars for the bot to use
from twitchio.ext import commands, pubsub
import twitchio
import asyncio
import time
import threading
import yaml

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
    pass


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


async def main():
    topics = [
        pubsub.channel_points(os.environ["USER_TOKEN"])[os.environ["CHANNEL_ID"]],
        pubsub.bits(os.environ["USER_TOKEN"])[os.environ["CHANNEL_ID"]],
        pubsub.bits_badge(os.environ["USER_TOKEN"])[os.environ["CHANNEL_ID"]],
        # This support is not yet ready in twitchio. maybe soon?
        # pubsub.channel_subscriptions(os.environ['USER_TOKEN'])[os.environ['CHANNEL_ID']],
        # pubsub.whispers(os.environ['USER_TOKEN'])
    ]

    for mod_id in os.environ.get("MODERATORS", "").strip().split(","):
        topics.append(
            pubsub.bits_badge(os.environ["USER_TOKEN"])[os.environ["CHANNEL_ID"]][
                mod_id
            ]
        )

    await client.pubsub.subscribe_topics(topics)
    await client.start()


class PubSubListener(object):
    def __init__(self):
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True

    def run(self):
        client.loop.run_until_complete(main())

    def start(self):
        thread.start()
