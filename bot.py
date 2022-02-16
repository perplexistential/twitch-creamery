import os
import yaml
import time
import asyncio

from bots.bot import Bot
from bots.pubsub import PubSubListener

PUBSUB_BOT_NAME = os.environ.get("PUBSUB_BOT_NAME", "pubsub")


if __name__ == "__main__":
    # See bots.example.yaml for ideas on how to write your own bots.yaml
    with open(os.environ.get("CONFIG_FILENAME", "bots.yaml"), "r") as file:
        bots = yaml.safe_load(file)
    threads = []
    loop = asyncio.get_event_loop()
    bot_list = []
    for bot_name, v in bots.items():
        time.sleep(1)
        bot_list.append(Bot(bot_name, loop=loop, **v))
    try:
        for bot in bot_list:
            loop.create_task(bot.connect())
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        for bot in bot_list:
            loop.run_until_complete(bot.close())
        loop.close()
    print("bot shut down")
