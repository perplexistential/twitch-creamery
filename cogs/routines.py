# Copyright Alex Morais (thatsamorais@gmail.com) for perplexistential

"""An example of routines."""

import datetime
import logging
from twitchio.ext import commands, routines
from .base import Cog

logger = logging.getLogger(__name__)

# This is intended as an example of how one could implement routines in a Cog.
# Let it serve as a repository of shared routines, important dates too.

# I do not recommend adding this cog directly, but making a copy and modifying
# it, or borrowing from it whatever routines you want.

class Cog(BaseCog):

    def __init__(self, bot, data={}):
        super().__init__(bot, 'routines', **data)
        self.hello.start()
        self.happy_birthday.start()

    @routines.routine(minutes=10)
    async def hello(arg: str):
        """hello."""
        logger.info("This is routines_bot!")
        raise RuntimeWarning("I enjoy attention")

    # This function will run prior to !hello
    @hello.before_routine
    async def hello_before(arg: str):
        """pre-hello."""
        logger.info("I am run before !hello")

    # This will only run following errors raised by !hello
    @hello.error
    async def hello_on_error(error: Exception):
        """on-error in hello."""
        logger.info(f"Hello routine raised: {error}.")

    # https://twitchio.readthedocs.io/en/latest/exts/routines.html
    # This routine will run at the same time everyday. If a naive datetime is
    # provided, your system local time is used.

    # The below example shows a routine which will first be ran on the 1st,
    # June 2021 at 9:30am system local time. It will then be ran every 24 hours
    # after the initial date, until stopped.

    # If the date has already passed, the routine will run at the next
    # specified time. For example: If today was the 2nd, June 2021 8:30am and
    # your datetime was scheduled to run on the 1st, June 2021 at 9:30am, you
    # routine will first run on 2nd, June 2021 at 9:30am.

    # In simpler terms, datetimes in the past only care about the time, not the
    # date. This can be useful when scheduling routines that don’t need to be
    # started on a specific date.
    @routines.routine(
        time=datetime.datetime(year=2021, month=5, day=5, hour=8, minute=30)
    )
    async def happy_birthday(arg: str):
        """happy_birthday."""
        logger.info(f"Hello {arg}!")

    # Shout out your discord or other social media
    # @routines.routine(hours=1)
