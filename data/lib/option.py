# -*- coding: utf-8 -*-

import json
import logging

logger = logging.getLogger()
option_file = "option.json"


def get_option():
    logger.info(f"Loading Option from [{option_file}]")
    try:
        option = json.load(open(option_file))
        if option['music_dir'][-1] != "/":
            option['music_dir'] = f"{option['music_dir']}/"
        logger.info("OK! - Option is loaded")
    except FileNotFoundError:
        logger.info(f"FAIL - [{option_file}] not found, load default settings")
        option = {
            "auto_owner": True,
            "owner_id": 0,
            "color": {
                "info": 16763981,
                "normal": 16579836,
                "warn": 13450043
            },
            "lang": "ko",
            "prefix": ";",
            "private_mode": False,
            "save_guild_data": False,
            "music_dir": "./data/music/"
        }

        logger.info("Creating Option File...")
        try:
            with open(option_file, "w", encoding="utf8") as option_f:
                option_f.write(json.dumps(option, indent=4))
            logger.info("OK! - Option File created")
        except Exception as e:
            logger.info(f"FAIL - Fail to create option file -> {e}")

    return option


def update_option(new_option):
    logger.info(f"Updating Option...")
    try:
        with open(option_file, "w", encoding="utf-8") as option_f:
            option_f.write(json.dumps(new_option))
        logger.info("OK! - Option is Updated")
        return True
    except Exception as e:
        logger.info(f"FAIL - {e}")
        return False
