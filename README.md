# twitch-creamery
a twitch-bot for the homies and I to entertain and amuse

## setup

1. Make an account on Twitch for your bot. Its more common than using your actual account.
1. If you prefer, request an oauth code from: https://twitchtokengenerator.com/ using your bot account. You'll need to login and give the app permissions to generate it for you. This app will give you the access token and the client ID of your bot's account. You can also choose your own way of getting these credentials if you wish!
1. Register an app with Twitch dev under your bot account, https://dev.twitch.tv/console/apps/create , and request a client-id so you can interface with Twitch's API. This Client ID is different from the one collected in the previous step; it is specifically for the API only. 

TODO: Figure out if we need a different Twitch API client ID
TODO: Build the token generation into this app so that giving permissions to a 3rd party application is not necessary.

## code

1. Python 3.x(3.6+): https://www.python.org/downloads/
1. Open a shell on your system: bash, iterm, cmd.exe
1. run `pip install pipenv`
1. change directory to where this project resides: cd ~/your/project/path, or even cd C:\your\project\path
1. now execute `pipenv sync` to sync your local env with the dependencies of this project

## env file

Create a file next to bot.py called ".env" and populate it with your credentials.

See .env.example for reference on what is required and available.


For bot `CLIENT_ID` and `CLIENT_SECRET` the naming convention is:

```shell
YOUR_BOT_NAME_CLIENT_ID= ...
YOUR_BOT_NAME_CLIENT_SECRET= ...
```

## run

```shell
 > cd path\to\code\directory
 path\to\code\directory\> pipenv run python bot.py
```

### default values

The code contains several default values when retrieving environment variables.

Note for coders: this file is in the .gitignore so that nobody accidentally pushes their secrets to the remote repository.

## yaml

Bots are configured with Cogs and other details through a YAML file, default being `bots.yaml`.

An example has been generated for you, called `bots.example.yaml`

```
bot_name:
	prefix: !      # how the bot recognizes commands
	channels:      # list of twitch channels the bot will join
	-   channel_1
	cogs:          # cogs is a list of the cogs the bot will use
	-   cog_name_1 # the name of the cog matching their filenames in the cogs/ directory
	scopes:
	-   all_scopes # if you want to request all possible scopes (default if not specified)
	-   chat:read  # an example of a single scope one could list. See AuthScopes in oauth/user.py
```

cogs are to be placed in the "cogs" directory to be found when parsing the above YAML.

## pubsub how-to

Pubsub is analogous to channel point redemptions, moderator actions, and bit events. At some point, whispers and subscriptions, too.

These features have been implemented as a Cog to be integrated into a bot, like any other, except it requires a unique setup. You are probably now familiar with your API Client credentials being used to generate access and refresh tokens via the OAuth2 Authorization Code Flow, whereby the bot requests permission to act on behalf of your bot's Twitch account. Channel points, bits, and other pubsub events require another user token; that of the owner of the channel to which your bot is "subscribing" to the "publications" (i.e. pubsub).

To make a bot that captures pubsub for a channel one needs to do the following:

* A channel's owner must generate a user access token and provide it. not a bot account; the actual channel where the streams will happen. It might authorize the following permissions:

```
bits:read
channel:read:redemptions
moderator:read:automod_settings
moderator:manage:automod_settings
moderator:manage:banned_users
moderator:read:blocked_terms
moderator:manage:blocked_terms
moderator:read:chat_settings
moderator:manage:chat_settings
```

* Add a bot configuration to bots.yaml like this

```yaml
pubsub:
   cogs:
   -   pubsub
   channels:
   -   thatsamorais
   scopes:
   -   all_scopes
```

* Add the channel name to the `channels` list in the bot's yaml config
* Add an environment variable composed of the channel's name in all caps followed by `_PUBSUB_TOKEN` containing this token, into `.env`, i.e. `CHANNEL_NAME_PUBSUB_TOKEN=user's token`

If you see BADAUTH error codes being emitted, ensure that the token has

## documentation

github: https://github.com/perplexistential/twitch-creamery

TwitchIO:
1. twitchio: https://twitchio.readthedocs.io/en/latest/index.html
2. github: https://github.com/TwitchIO/TwitchIO

Pub Sub:
1. twitch pubsub API docs: https://dev.twitch.tv/docs/pubsub#topics
1. twitchio: https://twitchio.readthedocs.io/en/latest/exts/pubsub.html

