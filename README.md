# twitch-creamery
a twitch-bot for the homies and I to entertain and amuse

## setup

1. Make an account on Twitch for your bot. Its more common than using your actual account.
1. If you prefer, request an oauth code from: https://twitchtokengenerator.com/ using your bot account. You'll need to login and give the app permissions to generate it for you. This app will give you the access token and the client ID of your bot's account. You can also choose your own way of getting these credentials if you wish!
1. Register an app with Twitch dev under your bot account, https://dev.twitch.tv/console/apps/create , and request a client-id so you can interface with Twitch's API. This Client ID is different from the one collected in the previous step; it is specifically for the API only. 

TODO: Figure out if we need a different Twitch API client ID
TODO: Build the token generation into this app so that giving permissions to a 3rd party application is not necessary.

## env file

Create a file next to bot.py called ".env" and populate it with these contents

```
API_CLIENT_ID=<your TwitchAPI app's client ID from Twitch>
USER_TOKEN=oauth:<your token>
USER_CLIENT_ID=<your bot's client ID>
BOT_NICK=<your bot's nickname>
BOT_PREFIX=!
CHANNEL=<your channel name>
```

Optionally, you can add support for listening to moderator activities by supplying the User IDs of the moderators whose actions in your channel you want to handle. If left empty or omitted then this pubsub action will not be registered.

```
MODERATORS=<moderator1_userid>,<moderator2_userid>,...
```



Note for coders: this file is in the .gitignore so that nobody accidentally pushes their secrets to the remote repository.

## code

1. Python 3.x(3.6+): https://www.python.org/downloads/ 
1. Open a shell on your system: bash, iterm, cmd.exe
1. run `pip install pipenv`
1. change directory to where this project resides: cd ~/your/project/path, or even cd C:\your\project\path
1. now execute `pipenv sync` to sync your local env with the dependencies of this project

## run 

```shell
 > cd path\to\code\directory
 path\to\code\directory\> pipenv run python bot.py
```

## documentation

Pub Sub:
1. twitch pubsub API docs: https://dev.twitch.tv/docs/pubsub#topics
1. twitchio: https://twitchio.readthedocs.io/en/latest/exts/pubsub.html

## troll bot

if you would like to have a bot that replaces a word in your chatters' messages from time to time, like buttsbot, then add the following to your .env file

```

```

