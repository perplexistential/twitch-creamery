# Copyright Alex Morais (thatsamorais@gmail.com) for perplexistential

"""The PubSub cog example."""

import os
import logging
from twitchio.ext import commands, pubsub
from .base import Cog

logger = logging.getLogger(__name__)


class Cog(BaseCog):

    def __init__(self, bot: Bot, data={}):
        super().__init__(bot, 'pubsub', **data)
        self.bot.pubsub = pubsub.PubSubPool(self.bot)

    @commands.Cog.event("event_ready")
    async def is_ready(self):
        logging.info("pubsub cog is ready!")
        bot = self.bot

        @bot.event()
        async def event_pubsub_bits(event: pubsub.PubSubBitsMessage):
            logging.info(
                f"{event.user.name} donated {event.bits_used} bits - "
                f'"{event.message}" and received {event.badge_entitlement}'
            )

        @bot.event()
        async def event_pubsub_bits_badge(event: pubsub.PubSubBitsBadgeMessage):
            logging.info(
                f"{event.user.name} received badge level - "
                f"{event.badge_tier} in {event.channel.name}"
            )

        @bot.event()
        async def event_pubsub_channel_points(event: pubsub.PubSubChannelPointsMessage):
            logging.info(
                f"{event.user.name} redeemed {event.reward.title}"
                f"args({event.input}) "
                f"in {event.channel_id} using channel points"
                f"(id:{event.id})"
            )

        @bot.event()
        async def event_pubsub_moderation_user_action(event):
            if type(event) == pubsub.PubSubModerationActionBanRequest:
                logging.info(
                    f"{event.created_by.name} targeted {event.target.name} "
                    f"with {event.action}({event.args})"
                )
            elif type(event) == pubsub.PubSubModerationActionChannelTerms:
                logging.info(
                    f"{event.requester.name} requested channel terms update of"
                    f" type {event.type} to {event.id}:{event.text} "
                    f"in {event.channel_id}"
                )
            elif type(event) == pubsub.PubSubModerationActionModeratorAdd:
                logging.info(
                    f"{event.created_by.name} targeted {event.target.name} "
                    f"with {event.moderation_action} in {event.channel_id}"
                )
            elif type(event) == pubsub.PubSubModerationAction:
                logging.info(
                    f"{event.created_by.name} targeted {event.target.name} "
                    f"with {event.action}({event.args}): "
                    f"message({event.message_id}), "
                    f"automod({event.from_automod})"
                )

        # The following two events are mentioned in docs but not supported
        @bot.event()
        async def event_pubsub_channel_subscriptions(event):
            logging.info("channel subscription: {event}")

        @bot.event()
        async def event_pubsub_whispers(event):
            logging.info("whispers: {event}")

        for channel in self.bot.channels:
            token = os.environ.get(f"{channel.upper()}_PUBSUB_TOKEN", "")
            channel_details = await self.bot.fetch_channel(channel)
            channel_id = channel_details.user.id
            topics = []
            for topic in self.data.get("topics", []):
                if topic == "channel_points":
                    topics.append(pubsub.channel_points(token)[channel_id])
                elif topic == "bits":
                    topics.append(pubsub.bits(token)[channel_id])
                elif topic == "bits_badge":
                    topics.append(pubsub.bits_badge(token)[channel_id])
                # This support is not yet ready in twitchio. maybe soon?
                elif topic == "channel_subscriptions":
                    topics.append(
                        pubsub.channel_subscriptions(self.bot.access_token)[channel_id]
                    )
                elif topic == "whispers":
                    topics.append(pubsub.whispers(self.bot.access_token))
                for mod_id in os.environ.get("MODERATORS", "").strip().split(","):
                    if mod_id:
                        topics.append(
                            pubsub.moderation_user_action(token)[channel_id][mod_id]
                        )
        self.bot.loop.create_task(self.bot.pubsub.subscribe_topics(topics))
