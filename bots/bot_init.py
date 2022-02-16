"""
The MIT License (MIT)
Copyright (c) 2017-2021 TwitchIO
Copyright (c) 2022 thatsamorais@gmail.com
Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

# In the interest of modifying how a Client is initialized by this project's Bot sub-class
# the entire init has been duplicated from twitchio and then modified to suit the purpose
# of specifying the client's loop instance. twitchio.ext.command.Bot does NOT pass the
# asyncio.loop to the Client.

import asyncio
import inspect
import warnings
import logging
import traceback
import sys
from typing import Union, Callable, List, Optional, Tuple, Any, Coroutine

from twitchio.errors import HTTPException
from twitchio import models
from twitchio.websocket import WSConnection
from twitchio.http import TwitchHTTP
from twitchio.channel import Channel
from twitchio.message import Message
from twitchio.user import User, PartialUser, SearchUser
from twitchio.cache import user_cache, id_cache


def init(
    bot,
    token: str,
    *,
    prefix: Union[str, list, tuple, set, Callable, Coroutine],
    client_secret: str = None,
    initial_channels: Union[list, tuple, Callable] = None,
    loop: asyncio.AbstractEventLoop = None,
    heartbeat: Optional[float] = 30.0,
    **kwargs
):
    bot.loop: asyncio.AbstractEventLoop = loop or asyncio.get_event_loop()
    bot._heartbeat = heartbeat

    token = token.replace("oauth:", "")

    bot._http = TwitchHTTP(bot, api_token=token, client_secret=client_secret)
    bot._connection = WSConnection(
        client=bot,
        token=token,
        loop=loop,
        initial_channels=initial_channels,
        heartbeat=heartbeat,
    )

    bot._events = {}
    bot._waiting: List[Tuple[str, Callable[[...], bool], asyncio.Future]] = []

    bot._prefix = prefix

    if kwargs.get("case_insensitive", False):
        bot._commands: Union[dict, _CaseInsensitiveDict] = _CaseInsensitiveDict()
        bot._command_aliases: Union[dict, _CaseInsensitiveDict] = _CaseInsensitiveDict()
    else:
        bot._commands = {}
        bot._command_aliases = {}

    bot._modules: Dict[str, types.ModuleType] = {}
    bot._cogs: Dict[str, Cog] = {}
    bot._checks: List[Callable[[Context], Union[bool, Awaitable[bool]]]] = []

    bot.__init__commands__()
