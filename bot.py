import os  # for importing env vars for the bot to use
from twitchio.ext import commands, pubsub
import twitchio
import asyncio
import time
import threading
import yaml


client = twitchio.Client(token=os.environ["USER_TOKEN"])
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
    def __init__(self, interval=1):
        self.interval = interval
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        time.sleep(self.interval)
        client.loop.run_until_complete(main())


class Bot(commands.Bot):
    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        # prefix can be a callable, which returns a list of strings or a string...
        # initial_channels can also be a callable which returns a list of strings...
        super().__init__(
            token=os.environ["USER_TOKEN"],
            prefix=os.environ["BOT_PREFIX"],
            initial_channels=[os.environ["CHANNEL"]],
        )

    async def event_ready(self):
        # Notify us when everything is ready!
        # We are logged in and ready to chat and use commands...
        print(f"Logged in as | {self.nick}")

    async def event_message(self, message):
        # Messages with echo set to True are messages sent by the bot...
        # For now we just want to ignore them...
        if message.echo:
            return

        if not str(message.content).startswith(os.environ["BOT_PREFIX"]):
            # Print the contents of our message to console...
            print(message.content)
            pass

        # Since we have commands and are overriding the default `event_message`
        # We must let the bot know we want to handle and invoke our commands...
        await self.handle_commands(message)

    @commands.command()
    async def hello(self, ctx: commands.Context):
        # Here we have a command hello, we can invoke our command with our prefix and command name
        # e.g ?hello
        # We can also give our commands aliases (different names) to invoke with.

        # Send a hello back!
        # Sending a reply back to the channel is easy... Below is an example.
        await ctx.send(f"Hello {ctx.author.name}!")


if __name__ == "__main__":
    bot = Bot()
    # pubsub_listener = PubSubListener()
    bot.run()  # the application will block on this call
    print("bot shut down")
