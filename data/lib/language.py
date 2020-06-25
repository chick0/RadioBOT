# -*- coding: utf-8 -*-

import sys
import json
import logging

import data.lib.option as option_manager

logger = logging.getLogger()


def get_data():
    option = option_manager.get_option()
    logger.info(f"Language File -> {option['lang']}.json")
    language_file = f"./data/i18n/{option['lang']}.json"

    logger.info("Loading Language data...")
    try:
        with open(language_file, "r", encoding="utf-8") as lang_f:
            lang_dat = json.load(lang_f)
        logger.info(f"OK! - [{option['lang']}] is loaded")
    except FileNotFoundError:
        logger.critical("FAIL - Fail to load Language data")
        logger.info("Try to load default Language data...")
        try:
            with open("./data/i18n/default.json", "r", encoding="utf-8") as lang_f:
                lang_dat = json.load(lang_f)
            logger.info(f"OK! - default data is loaded")
        except FileNotFoundError as e:
            logger.critical("FAIL - Fail to load Default Language data")
            logger.critical("=" * 30)
            logger.critical("<< Bot is dead >>")
            logger.critical(e)
            logger.critical("=" * 30)
            sys.exit(-1)

    return lang_dat
