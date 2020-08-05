# -*- coding: utf-8 -*-

import json
import logging

logger = logging.getLogger()


def dump_guild(bot):
    logger.info(f"Connected to {len(bot.guilds)} servers")
    result = list()
    for temp_guild in bot.guilds:
        result.append(
            dict(
                id=temp_guild.id,
                name=temp_guild.name,
                region=str(temp_guild.region),
                owner_id=temp_guild.owner_id,
                member=len(temp_guild.members)
            )
        )
    logger.info("-" * 50)

    logger.info("Saving Guild Data...")
    try:
        with open("./data/guild.json", "w", encoding="utf8") as guild_f:
            guild_f.write(json.dumps(result, sort_keys=True, indent=4))
        logger.info("Saved Guild Data at [data/guild.json]")
    except Exception as e:
        logger.warning(f"FAIL - {e.__class__.__name__}: {e}")

    logger.info("-" * 50)
