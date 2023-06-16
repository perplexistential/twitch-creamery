# Copyright Alex Morais (thatsamorais@gmail.com) for perplexistential

"""Bot application main."""

import sys
import os
import logging
import yaml
import asyncio
from dotenv import dotenv_values
import argparse

from bots.bot import Bot

logging.basicConfig(level=logging.INFO)

PUBSUB_BOT_NAME = os.getenv("PUBSUB_BOT_NAME", "pubsub")


def setup_bots(env_config, bots_config):
    bot_list = []
    for bot_name, bot_config in (bots_config or {}).items():
        print(f"Bot config for {bot_name}: {bot_config}")
        bot = Bot(bot_name, env_config, bot_config)
        bot_list.append(bot)
    return bot_list


async def run_bots(bots):
    tasks = []
    for bot in bots:
        tasks.append(bot.run())
        await asyncio.sleep(1)  # Sleep for 1 second between starting each bot
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="The path to bots.yaml configuration file", default="bots.yaml")
    args = parser.parse_args()

    # Load environment configuration
    env_config = dotenv_values(".env")

    try:
        # Load bots configuration
        with open(args.config, "r") as file:
            bots_config = yaml.safe_load(file)["bots"]
    except FileNotFoundError:
        print(f"Configuration file not found: {args.config}")
        sys.exit(1)

    # Setup bots using the loaded configurations
    bots = setup_bots(env_config, bots_config)
    asyncio.run(run_bots(bots))
