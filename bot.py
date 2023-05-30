# Copyright Alex Morais (thatsamorais@gmail.com) for perplexistential

"""Bot application main."""

import os
import logging
import yaml
import asyncio
from dotenv import dotenv_values

from bots.bot import Bot

logging.basicConfig(level=logging.INFO)

PUBSUB_BOT_NAME = os.getenv("PUBSUB_BOT_NAME", "pubsub")


def setup_bots(env_config, bots_config):
    bot_list = []
    for bot_name, bot_config in bots_config.items():
        print(f"Bot config for {bot_name}: {bot_config}")
        bot = Bot(bot_name, env_config, bot_config)
        bot_list.append(bot)
    return bot_list


async def run_bots(bot_list):
    tasks = [asyncio.create_task(bot.run()) for bot in bot_list]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    # Load environment configuration
    env_config = dotenv_values(".env")

    # Load bots configuration
    with open(env_config.get("CONFIG_FILENAME", "bots.yaml"), "r") as file:
        bots_config = yaml.safe_load(file)["bots"]

    # Setup bots using the loaded configurations
    bots = setup_bots(env_config, bots_config)
    asyncio.run(run_bots(bots))
