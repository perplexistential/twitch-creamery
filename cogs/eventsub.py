# Copyright Alex Morais (thatsamorais@gmail.com) for perplexistential.

# Important notice about using this cog
# The EventSub ext is made to receive eventsub webhook notifications from twitch. For those not familiar with eventsub, it allows you to subscribe to certain events, and when these events happen, Twitch will send you an HTTP request containing information on the event. This ext abstracts away the complex portions of this, integrating seamlessly into the twitchio Client event dispatching system.

# Warning:
# This ext requires you to have a public facing ip, and to be able to receive inbound requests.

# Note:
# Twitch requires EventSub targets to have TLS/SSL enabled (https). TwitchIO does not support this, as such you should use a reverse proxy such as nginx to handle TLS/SSL.

"""Cog composes bot features."""

import logging
from bots.bot import Bot
from twitchio.ext import commands, eventsub
from .base_cog import BaseCog

logger = logging.getLogger(__name__)

class Cog(BaseCog):

    def __init__(self, bot: Bot, data={}):
        super().__init__(bot, 'eventsub', **data)
        self.eventsub_client = eventsub.EventSubClient(
            self.bot,
            self.EVENTSUB_SECRET_WORD,
            self.EVENTSUB_CALLBACK,
        )

    def load_config(self):
        self.EVENTSUB_SECRET_WORD = self.data.get('EVENTSUB_SECRET_WORD', 'some_secret_string')
        self.EVENTSUB_CALLBACK = self.data.get('EVENTSUB_CALLBACK', '/callback')

    @commands.Cog.event("event_ready")
    async def is_ready(self):
        logging.info("eventsub cog is ready!")
        bot = self.bot
        for channel in bot.channels:
            for event in self.data.get("events", []):
                # for user in self.data.get("user_updated_users", []):
                #    await self.eventsub_client.subscribe_user_updated(user)
                if event == "channel_raid":
                    await self.eventsub_client.subscribe_channel_raid(channel)
                elif event == "channel_ban":
                    await self.eventsub_client.subscribe_channel_bans(channel)
                elif event == "channel_unban":
                    await self.eventsub_client.subscribe_channel_unbans(channel)
                elif event == "channel_subscription":
                    await self.eventsub_client.subscribe_channel_subscriptions(channel)
                elif event == "channel_cheers":
                    await self.eventsub_client.subscribe_channel_cheers(channel)
                elif event == "channel_update":
                    await self.eventsub_client.subscribe_channel_update(channel)
                elif event == "channel_follow":
                    await self.eventsub_client.subscribe_channel_follows(channel)
                elif event == "channel_moderators_add":
                    await self.eventsub_client.subscribe_channel_moderators_add(channel)
                elif event == "channel_moderators_remove":
                    await self.eventsub_client.subscribe_channel_moderators_remove(
                        channel
                    )
                elif event == "channel_hypetrain_begin":
                    await self.eventsub_client.subscribe_channel_hypetrain_begin(
                        channel
                    )
                elif event == "channel_hypetrain_progress":
                    await self.eventsub_client.subscribe_channel_hypetrain_progress(
                        channel
                    )
                elif event == "channel_hypetrain_end":
                    await self.eventsub_client.subscribe_channel_hypetrain_end(channel)
                elif event == "channel_stream_start":
                    await self.eventsub_client.subscribe_channel_stream_start(channel)
                elif event == "channel_stream_end":
                    await self.eventsub_client.subscribe_channel_stream_end(channel)
                elif event == "channel_points_reward_added":
                    await self.eventsub_client.subscribe_channel_points_reward_added(
                        channel
                    )
                elif event == "channel_points_reward_updated":
                    await self.eventsub_client.subscribe_channel_points_reward_updated(
                        channel
                    )
                elif event == "channel_points_reward_removed":
                    await self.eventsub_client.subscribe_channel_points_reward_removed(
                        channel
                    )
                elif event == "channel_points_redeemed":
                    await self.eventsub_client.subscribe_channel_points_redeemed(
                        channel
                    )
                elif event == "channel_points_redeem_updated":
                    await self.eventsub_client.subscribe_channel_points_redeem_updated(
                        channel
                    )
        port = self.data.get("port", "15543")
        logging.info(f"eventsub listening on port {port}")
        self.bot.loop.create_task(self.eventsub_client.listen(port=port))

        @bot.event()
        async def eventsub_notification_user_update(payload: eventsub.UserUpdateData):
            pass

        @bot.event()
        async def eventsub_notification_raid(payload: eventsub.ChannelRaidData):
            pass

        @bot.event()
        async def eventsub_notification_bans(payload: eventsub.ChannelBanData):
            pass

        @bot.event()
        async def eventsub_notification_unbans(payload: eventsub.ChannelUnbanData):
            pass

        @bot.event()
        async def eventsub_notification_subscription(
            payload: eventsub.ChannelSubscribeData,
        ):
            pass

        @bot.event()
        async def eventsub_notification_cheer(payload: eventsub.ChannelCheerData):
            pass

        @bot.event()
        async def eventsub_notification_update(payload: eventsub.ChannelUpdateData):
            pass

        @bot.event()
        async def eventsub_notification_follow(payload: eventsub.ChannelFollowData):
            pass

        @bot.event()
        async def eventsub_notification_moderator_add(
            payload: eventsub.ChannelModeratorAddRemoveData,
        ):
            pass

        @bot.event()
        async def eventsub_notification_moderator_remove(
            payload: eventsub.ChannelModeratorAddRemoveData,
        ):
            pass

        @bot.event()
        async def eventsub_notification_hypetrain_begin(
            payload: eventsub.HypeTrainBeginProgressData,
        ):
            pass

        @bot.event()
        async def eventsub_notification_hypetrain_progress(
            payload: eventsub.HypeTrainBeginProgressData,
        ):
            pass

        @bot.event()
        async def eventsub_notification_hypetrain_end(
            payload: eventsub.HypeTrainEndData,
        ):
            pass

        @bot.event()
        async def eventsub_notification_stream_start(
            payload: eventsub.StreamOnlineData,
        ):
            pass

        @bot.event()
        async def eventsub_notification_stream_end(payload: eventsub.StreamOfflineData):
            pass

        @bot.event()
        async def eventsub_notification_channel_reward_add(
            payload: eventsub.CustomRewardAddUpdateRemoveData,
        ):
            pass

        @bot.event()
        async def eventsub_notification_channel_reward_update(
            payload: eventsub.CustomRewardAddUpdateRemoveData,
        ):
            pass

        @bot.event()
        async def eventsub_notification_channel_reward_remove(
            payload: eventsub.CustomRewardAddUpdateRemoveData,
        ):
            pass

        @bot.event()
        async def eventsub_notification_channel_reward_redeem(
            payload: eventsub.CustomRewardRedemptionAddUpdateData,
        ):
            pass

        @bot.event()
        async def eventsub_notification_channel_reward_redeem_updated(
            payload: eventsub.CustomRewardRedemptionAddUpdateData,
        ):
            pass
