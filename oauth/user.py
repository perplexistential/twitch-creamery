#  Copyright (c) 2020. Lena "Teekeks" During <info@teawork.de>

# Copied here and adapted for the purposes of adding authorization flow to the bots.
# All of the following code is essentially the same or code was copied from files it imported for
# brevity. See: https://github.com/Teekeks/pyTwitchAPI

"""
User OAuth Authenticator and helper functions
---------------------------------------------

This tool is an alternative to various online services that give you a user auth token.
It provides non-server and server options.

***************************************
Requirements for non-server environment
***************************************

Since this tool opens a browser tab for the Twitch authentication, you can only use this tool on enviroments that can
open a browser window and render the `<twitch.tv>`__ website.

For my authenticator you have to add the following URL as a "OAuth Redirect URL": :code:`http://localhost:17563`
You can set that `here in your twitch dev dashboard <https://dev.twitch.tv/console>`__.

***********************************
Requirements for server environment
***********************************

You need the user code provided by Twitch when the user logs-in at the url returned by :code:`return_auth_url`.

Create the UserAuthenticator with the URL of your webserver that will handle the redirect, and add it as a "OAuth Redirect URL"
You can set that `here in your twitch dev dashboard <https://dev.twitch.tv/console>`__.

************
Code example
************

.. code-block:: python

    from twitchAPI.twitch import Twitch
    from twitchAPI.oauth import UserAuthenticator
    from twitchAPI.types import AuthScope

    twitch = Twitch('my_app_id', 'my_app_secret')

    target_scope = [AuthScope.BITS_READ]
    auth = UserAuthenticator(twitch, target_scope, force_verify=False)
    # this will open your default browser and prompt you with the twitch verification website
    token, refresh_token = auth.authenticate()
    # add User authentication
    twitch.set_user_authentication(token, target_scope, refresh_token)

********************
Class Documentation:
********************
"""
import uuid
from typing import List, Union
from enum import Enum
import webbrowser
from aiohttp import web
import asyncio
from threading import Thread
from time import sleep
import requests
from concurrent.futures._base import CancelledError
from logging import getLogger, Logger
import urllib.parse


TWITCH_AUTH_BASE_URL = "https://id.twitch.tv/"


class TwitchAPIException(Exception):
    """Base Twitch API Exception"""

    pass


class InvalidRefreshTokenException(TwitchAPIException):
    """used User Refresh Token is invalid"""

    pass


class TwitchAuthorizationException(TwitchAPIException):
    """Exception in the Twitch Authorization"""

    pass


class UnauthorizedException(TwitchAuthorizationException):
    """Not authorized to use this"""

    pass


def build_url(
    url: str, params: dict, remove_none=False, split_lists=False, enum_value=True
) -> str:
    """Build a valid url string

    :param url: base URL
    :param params: dictionary of URL parameter
    :param bool remove_none: if set all params that have a None value get removed |default| :code:`False`
    :param bool split_lists: if set all params that are a list will be split over multiple url
            parameter with the same name |default| :code:`False`
    :param bool enum_value: if true, automatically get value string from Enum values |default| :code:`True`
    :return: URL
    :rtype: str
    """

    def get_val(val):
        if not enum_value:
            return str(val)
        if isinstance(val, Enum):
            return str(val.value)
        return str(val)

    def add_param(res, k, v):
        if len(res) > 0:
            res += "&"
        res += str(k)
        if v is not None:
            res += "=" + urllib.parse.quote(get_val(v))
        return res

    result = ""
    for key, value in params.items():
        if value is None and remove_none:
            continue
        if split_lists and isinstance(value, list):
            for va in value:
                result = add_param(result, key, va)
        else:
            result = add_param(result, key, value)
    return url + (("?" + result) if len(result) > 0 else "")


def build_scope(scopes: List[str]) -> str:
    """Builds a valid scope string from list

    :param list[~twitchAPI.types.AuthScope] scopes: list of :class:`~twitchAPI.types.AuthScope`
    :rtype: str
    :returns: the valid auth scope string
    """
    return " ".join(scopes)


def get_uuid():
    """Returns a random UUID

    :rtype: :class:`~uuid.UUID`"""
    return uuid.uuid4()


def refresh_access_token(refresh_token: str, app_id: str, app_secret: str):
    """Simple helper function for refreshing a user access token.

    :param str refresh_token: the current refresh_token
    :param str app_id: the id of your app
    :param str app_secret: the secret key of your app
    :return: access_token, refresh_token
    :raises ~twitchAPI.types.InvalidRefreshTokenException: if refresh token is invalid
    :raises ~twitchAPI.types.UnauthorizedException: if both refresh and access token are invalid (eg if the user changes
                their password of the app gets disconnected)
    :rtype: (str, str)
    """
    param = {
        "refresh_token": refresh_token,
        "client_id": app_id,
        "grant_type": "refresh_token",
        "client_secret": app_secret,
    }
    url = build_url(TWITCH_AUTH_BASE_URL + "oauth2/token", {})
    result = requests.post(url, data=param)
    data = result.json()
    if data.get("status", 200) == 400:
        raise InvalidRefreshTokenException(data.get("message", ""))
    if data.get("status", 200) == 401:
        raise UnauthorizedException(data.get("message", ""))
    return data["access_token"], data["refresh_token"]


def validate_token(access_token: str) -> dict:
    """Helper function for validating a user or app access token.

    https://dev.twitch.tv/docs/authentication#validating-requests

    :param str access_token: either a user or app OAuth access token
    :return: response from the api
    :rtype: dict
    """
    header = {"Authorization": f"OAuth {access_token}"}
    url = build_url(TWITCH_AUTH_BASE_URL + "oauth2/validate", {})
    result = requests.get(url, headers=header)
    return result.json()


def revoke_token(client_id: str, access_token: str) -> bool:
    """Helper function for revoking a user or app OAuth access token.

    https://dev.twitch.tv/docs/authentication#revoking-access-tokens

    :param str client_id: client id belonging to the access token
    :param str access_token: user or app OAuth access token
    :rtype: bool
    :return: :code:`True` if revoking succeeded, otherwise :code:`False`
    """
    url = build_url(
        TWITCH_AUTH_BASE_URL + "oauth2/revoke",
        {"client_id": client_id, "token": access_token},
    )
    result = requests.post(url)
    return result.status_code == 200


class UserAuthenticator:
    """Simple to use client for the Twitch User authentication flow.

    :param ~twitchAPI.twitch.Twitch twitch: A twitch instance
    :param list[~twitchAPI.types.AuthScope] scopes: List of the desired Auth scopes
    :param bool force_verify: If this is true, the user will always be prompted for authorization by twitch,
                |default| :code:`False`
    :param str url: The reachable URL that will be opened in the browser.
                |default| :code:`http://localhost:17563`

    :var int port: The port that will be used. |default| :code:`17653`
    :var str host: the host the webserver will bind to. |default| :code:`0.0.0.0`
    """

    __document: str = """<!DOCTYPE html>
 <html lang="en">
 <head>
     <meta charset="UTF-8">
     <title>Twitch-Creamery OAuth</title>
 </head>
 <body>
     <h1>Thanks for Authenticating!</h1>
 You may now close this page.
 </body>
 </html>"""

    port: int = 17563
    url: str = "http://localhost:17563"
    host: str = "0.0.0.0"
    scopes: List[str] = []
    force_verify: bool = False
    __state: str = str(get_uuid())
    __logger: Logger = None

    __client_id: str = None

    __callback_func = None

    __server_running: bool = False
    __loop: Union["asyncio.AbstractEventLoop", None] = None
    __runner: Union["web.AppRunner", None] = None
    __thread: Union["threading.Thread", None] = None

    __user_token: Union[str, None] = None

    __can_close: bool = False

    def __init__(
        self,
        app_id: str,
        app_secret: str,
        scopes: List[str],
        force_verify: bool = False,
        url: str = "http://localhost:18951",
        port: str = "18951",
    ):
        self.__client_id = app_id
        self.__client_secret = app_secret
        self.scopes = scopes
        self.force_verify = force_verify
        self.__logger = getLogger("twitchAPI.oauth")
        self.url = url
        self.port = port

    def __build_auth_url(self):
        params = {
            "client_id": self.__client_id,
            "redirect_uri": self.url,
            "response_type": "code",
            "scope": build_scope(self.scopes),
            "force_verify": str(self.force_verify).lower(),
            "state": self.__state,
        }
        return build_url(TWITCH_AUTH_BASE_URL + "oauth2/authorize", params)

    def __build_runner(self):
        app = web.Application()
        app.add_routes([web.get("/", self.__handle_callback)])
        return web.AppRunner(app)

    async def __run_check(self):
        while not self.__can_close:
            try:
                await asyncio.sleep(1)
            except (CancelledError, asyncio.CancelledError):
                pass
        for task in asyncio.all_tasks(self.__loop):
            task.cancel()

    def __run(self, runner: "web.AppRunner"):
        self.__runner = runner
        self.__loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.__loop)
        self.__loop.run_until_complete(runner.setup())
        site = web.TCPSite(runner, self.host, self.port)
        self.__loop.run_until_complete(site.start())
        self.__server_running = True
        self.__logger.info("running oauth Webserver")
        try:
            self.__loop.run_until_complete(self.__run_check())
        except (CancelledError, asyncio.CancelledError):
            pass

    def __start(self):
        self.__thread = Thread(target=self.__run, args=(self.__build_runner(),))
        self.__thread.start()

    def stop(self):
        """Manually stop the flow

        :rtype: None
        """
        self.__can_close = True

    async def __handle_callback(self, request: "web.Request"):
        val = request.rel_url.query.get("state")
        self.__logger.debug(f"got callback with state {val}")
        # invalid state!
        if val != self.__state:
            return web.Response(status=401)
        self.__user_token = request.rel_url.query.get("code")
        if self.__user_token is None:
            # must provide code
            return web.Response(status=400)
        if self.__callback_func is not None:
            self.__callback_func(self.__user_token)
        return web.Response(text=self.__document, content_type="text/html")

    def return_auth_url(self):
        return self.__build_auth_url()

    def authenticate(self, callback_func=None, user_token=None):
        """Start the user authentication flow\n
        If callback_func is not set, authenticate will wait till the authentication process finished and then return
        the access_token and the refresh_token
        If user_token is set, it will be used instead of launching the webserver and opening the browser

        :param callback_func: Function to call once the authentication finished.
        :param str user_token: Code obtained from twitch to request the access and refresh token.
        :return: None if callback_func is set, otherwise access_token and refresh_token
        :raises ~twitchAPI.types.TwitchAPIException: if authentication fails
        :rtype: None or (str, str)
        """
        self.__callback_func = callback_func

        if user_token is None:
            self.__start()
            # wait for the server to start up
            while not self.__server_running:
                sleep(0.01)
            # open in browser
            webbrowser.open(self.__build_auth_url(), new=2)
            while self.__user_token is None:
                sleep(0.01)
            # now we need to actually get the correct token
        else:
            self.__user_token = user_token

        param = {
            "client_id": self.__client_id,
            "client_secret": self.__client_secret,
            "code": self.__user_token,
            "grant_type": "authorization_code",
            "redirect_uri": self.url,
        }
        url = build_url(TWITCH_AUTH_BASE_URL + "oauth2/token", param)
        response = requests.post(url)
        data: dict = response.json()
        if callback_func is None:
            self.stop()
            if data.get("access_token") is None:
                raise Exception(f"Authentication failed:\n{str(data)}")
            return data["access_token"], data["refresh_token"]
        elif user_token is not None:
            self.__callback_func(self.__user_token)


# This is more for reference than usage
class AuthScope(Enum):
    """Enum of Authentication scopes"""

    ANALYTICS_READ_EXTENSION = "analytics:read:extensions"
    ANALYTICS_READ_GAMES = "analytics:read:games"
    BITS_READ = "bits:read"
    CHANNEL_READ_SUBSCRIPTIONS = "channel:read:subscriptions"
    CHANNEL_READ_STREAM_KEY = "channel:read:stream_key"
    CHANNEL_EDIT_COMMERCIAL = "channel:edit:commercial"
    CHANNEL_READ_HYPE_TRAIN = "channel:read:hype_train"
    CHANNEL_MANAGE_BROADCAST = "channel:manage:broadcast"
    CHANNEL_READ_REDEMPTIONS = "channel:read:redemptions"
    CHANNEL_MANAGE_REDEMPTIONS = "channel:manage:redemptions"
    CLIPS_EDIT = "clips:edit"
    USER_EDIT = "user:edit"
    USER_EDIT_BROADCAST = "user:edit:broadcast"
    USER_READ_BROADCAST = "user:read:broadcast"
    USER_READ_EMAIL = "user:read:email"
    USER_EDIT_FOLLOWS = "user:edit:follows"
    CHANNEL_MODERATE = "channel:moderate"
    CHAT_EDIT = "chat:edit"
    CHAT_READ = "chat:read"
    WHISPERS_READ = "whispers:read"
    WHISPERS_EDIT = "whispers:edit"
    MODERATION_READ = "moderation:read"
    CHANNEL_SUBSCRIPTIONS = "channel_subscriptions"
    CHANNEL_READ_EDITORS = "channel:read:editors"
    CHANNEL_MANAGE_VIDEOS = "channel:manage:videos"
    USER_READ_BLOCKED_USERS = "user:read:blocked_users"
    USER_MANAGE_BLOCKED_USERS = "user:manage:blocked_users"
    USER_READ_SUBSCRIPTIONS = "user:read:subscriptions"
    USER_READ_FOLLOWS = "user:read:follows"
    CHANNEL_READ_GOALS = "channel:read:goals"
    CHANNEL_READ_POLLS = "channel:read:polls"
    CHANNEL_MANAGE_POLLS = "channel:manage:polls"
    CHANNEL_READ_PREDICTIONS = "channel:read:predictions"
    CHANNEL_MANAGE_PREDICTIONS = "channel:manage:predictions"
    MODERATOR_MANAGE_AUTOMOD = "moderator:manage:automod"
    # CHANNEL_MANAGE_SCHEDULE = 'channel:manage:channel'

    @staticmethod
    def all_scopes():
        return [s.value for s in AuthScope]
