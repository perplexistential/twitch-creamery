import os
import yaml
import time

from bots.bot import Bot
from bots.pubsub import PubSubListener

PUBSUB_BOT_NAME = os.environ.get("PUBSUB_BOT_NAME", "pubsub")

if __name__ == "__main__":

    # See bots.example.yaml for ideas on how to write your own bots.yaml
    with open(os.environ.get("CONFIG_FILENAME", "bots.yaml"), "r") as file:
        bots = yaml.safe_load(file)

    for bot_name, v in bots.items():
        if bot_name == "pubsub":
            # pubsub_listener = PubSubListener()
            pass
        else:
            bot = Bot(bot_name, **v)
            time.sleep(5)
            bot.start()

    print("bot shut down")
