# -*- coding: utf-8 -*-

import json
import logging
import discord

logger = logging.getLogger()


def __save_guild(guild_data):
    logger.info("Saving Guild Data...")
    try:
        with open("./data/guild.json", "w", encoding="utf8") as guild_f:
            guild_f.write(json.dumps(guild_data, sort_keys=True, indent=4))
        logger.info("Saved Guild Data at [./data/guild.json]")
    except Exception as e:
        logger.warning(f"FAIL - {e}")


def dump_guild(bot: discord.ext.commands.Bot, save):
    logger.info(f"Connected to {len(bot.guilds)} servers")
    result = list()
    for temp_guild in bot.guilds:
        logger.info(f" - Name: {temp_guild.name}")
        result.append({'id': temp_guild.id, 'name': temp_guild.name})
    logger.info("-" * 50)
    if save is True:
        __save_guild(result)
