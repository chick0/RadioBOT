# -*- coding: utf-8 -*-

import json
import logging
import getpass

logger = logging.getLogger()


def get_token():
    logger.info("Loading Token...")
    bot_token = "#"

    try:
        logger.info("OK! - File exists")
        bot_token = json.load(open("token.json"))['token']
        logger.info("Token length check...")
        if len(bot_token) == 59:
            logger.info("OK! - Token is Ready!")
        else:
            logger.critical("FAIL - Invalid token detected")
            bot_token = "#"
    except FileNotFoundError:
        logger.critical("Token File Not Found")
        bot_token = "#"

    if bot_token == "#":
        logger.info("READY - Get Token from console input")
        bot_token = getpass.getpass("What is **Your** Token: ")
        logger.info("Token length check...")
        if len(bot_token) == 59:
            logger.info("OK! - Token is Ready!")
            update_token(bot_token)
        else:
            logger.critical("FAIL - Invalid token detected")
            bot_token = "#"

    return bot_token


def update_token(token):
    try:
        logger.info("Updating Token...")
        with open("token.json", "w", encoding="utf8") as f:
            f.write(json.dumps({"token": token}, indent=4))
        logger.info("OK! - Token is Updated!")
    except Exception as e:
        logger.critical(f"FAIL - {e}")


def reset_token():
    try:
        logger.info("Reset Token...")
        with open("token.json", "w", encoding="utf8") as f:
            f.write(json.dumps({"token": "#"}, indent=4))
        logger.info("OK! - Token is now the default value")
    except Exception as e:
        logger.critical(f"FAIL - {e}")