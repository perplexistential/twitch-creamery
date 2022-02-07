# twitch-creamery
a twitch-bot for the homies and I to entertain and amuse

## Setup

1. Make an account on Twitch for your bot. Its more common than using your actual account.
1. If you prefer, request an oauth code from: https://twitchapps.com/tmi using your bot account. You'll need to login and give the app permissions to generate it for you. You can also choose your own way of getting a token.
1. Register your app with Twitch dev, https://dev.twitch.tv/console/apps/create , and request a client-id so you can interface with Twitch's API

You'll need these later.

TODO: Build the token generation into this app so that giving permissions to a 3rd party application is not necessary.

### Install

1. Python 3.6 is sufficient, but Python 3.9 is the latest and is preferred:
Windows: https://www.python.org/downloads/release/python-375/
Linux: https://www.python.org/downloads/release/python-375/
OS X: https://www.python.org/downloads/release/python-375/
1. Open a shell on your system: bash, iterm, cmd.exe
1. run `pip install pipenv`
1. change directory to where this project resides: cd ~/your/project/path, or even cd C:\your\project\path
1. now execute `pipenv sync` to sync your local env with the dependencies of this project

