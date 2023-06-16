"""token helpers."""

import threading
import os
import logging

logger = logging.getLogger(__name__)

from oauth import user

__token_cache = dict()


def generate_token(client_id, client_secret, port=None, scopes=None):
    """generate_token."""
    global __token_cache
    token_override = os.environ.get("AUTH_TOKEN", None)
    if token_override:
        return token_override
    target_scope = []
    for s in scopes or []:
        if s == "all_scopes":
            target_scope.extend(all_scopes())
        else:
            target_scope.append(s)
    if not target_scope:
        target_scope = all_scopes()

    access_token = __token_cache.get(client_id, {}).get("access_token", None)
    if not access_token:
        port = port or os.environ.get("DEFAULT_AUTH_PORT", "18951")
        auth = user.UserAuthenticator(
            client_id,
            client_secret,
            target_scope,
            force_verify=False,
            url=f"http://localhost:{port}",
            port=port,
        )

        # this will open your default browser and prompt you with the twitch verification website
        access_token, refresh_token = auth.authenticate()
        __token_cache[client_id] = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "lock": threading.Lock(),
        }
        auth.stop()
    return access_token


def refresh_token(client_id, client_secret):
    """refresh_token."""
    global __token_cache
    if not client_id or not client_secret:
        if os.environ.get("AUTH_TOKEN", None):
            logging.info(
                "Your manual auth token may have expired. "
                "Providing a client id/secret and acquiring a token from the "
                "OAuth2 Authorization flow with a user would enable automatic "
                "token refresh."
            )
            return None
        else:
            raise Exception("the client and secret are invalid")
        at, rt = user.refresh_access_token(
            __token_cache[client_id]["refresh_token"], client_id, client_secret
        )
        __token_cache[client_id] = {"access_token": at, "refresh_token": rt}
        return at
    return __token_cache[client_id]["access_token"]


def all_scopes():
    """all_scopes."""
    return user.AuthScope.all_scopes()
