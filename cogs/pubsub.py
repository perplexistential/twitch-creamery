import os
from bots.bot import Bot
from twitchio.ext import commands, pubsub
from tokengen.utils import generate_token


class Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.pubsub = pubsub.PubSubPool(self.bot)

    @commands.Cog.event("event_ready")
    async def is_ready(self):
        print("pubsub cog is ready!")
        bot = self.bot

        @bot.event()
        async def event_pubsub_bits(event: pubsub.PubSubBitsMessage):
            print(
                f'{event.user.name} donated {event.bits_used} bits - "{event.message}" and received {event.badge_entitlement}'
            )

        @bot.event()
        async def event_pubsub_bits_badge(event: pubsub.PubSubBitsBadgeMessage):
            print(
                f"{event.user.name} received badge level - {event.badge_tier} in {event.channel.name}"
            )

        @bot.event()
        async def event_pubsub_channel_points(event: pubsub.PubSubChannelPointsMessage):
            print(
                f"{event.user.name} redeemed {event.reward.title} args({event.input}) in {event.channel_id} using channel points (id:{event.id})"
            )

        @bot.event()
        async def event_pubsub_moderation_user_action(event):
            if type(event) == pubsub.PubSubModerationActionBanRequest:
                print(
                    f"{event.created_by.name} targeted {event.target.name} with {event.action}({event.args})"
                )
            elif type(event) == pubsub.PubSubModerationActionChannelTerms:
                print(
                    f"{event.requester.name} requested channel terms update of type {event.type} to {event.id}:{event.text} in {event.channel_id}"
                )
            elif type(event) == pubsub.PubSubModerationActionModeratorAdd:
                print(
                    f"{event.created_by.name} targeted {event.target.name} with {event.moderation_action} in {event.channel_id}"
                )
            elif type(event) == pubsub.PubSubModerationAction:
                print(
                    f"{event.created_by.name} targeted {event.target.name} with {event.action}({event.args}): message({event.message_id}), automod({event.from_automod})"
                )

        # The following two events are not yet supported in twitchio, but are mentioned in the docs
        @bot.event()
        async def event_pubsub_channel_subscriptions(event):
            print("channel subscription: {event}")

        @bot.event()
        async def event_pubsub_whispers(event):
            print("whispers: {event}")

        topics = []
        for channel in self.bot.channels:
            token = os.environ.get(f"{channel.upper()}_PUBSUB_TOKEN", "")
            channel_details = await self.bot.fetch_channel(channel)
            channel_id = channel_details.user.id
            topics.extend(
                [
                    pubsub.channel_points(token)[channel_id],
                    pubsub.bits(token)[channel_id],
                    pubsub.bits_badge(token)[channel_id],
                    # This support is not yet ready in twitchio. maybe soon?
                    # pubsub.channel_subscriptions(self.bot.access_token)[channel_id],
                    # pubsub.whispers(self.bot.access_token)
                ]
            )
            for mod_id in os.environ.get("MODERATORS", "").strip().split(","):
                if mod_id:
                    topics.append(
                        pubsub.moderation_user_action(token)[channel_id][mod_id]
                    )

        self.bot.loop.create_task(self.bot.pubsub.subscribe_topics(topics))


def prepare(bot: commands.Bot):
    # Load our cog with this module...
    bot.add_cog(Cog(bot))
