# -*- coding: utf-8 -*-

import logging
import discord


logger = logging.getLogger()


def __get_status(option):
    if option == "idle":
        return discord.Status.idle
    elif option == "dnd":
        return discord.Status.dnd
    elif option == "online":
        return discord.Status.online
    elif option == "offline":
        return discord.Status.offline
    else:
        return discord.Status.online


async def set_status(bot, language, status):
    await bot.change_presence(status=__get_status(status),
                              activity=discord.Activity(type=discord.ActivityType.listening,
                                                        name=language['title']['music'])
                              )


def invite_me(bot, owner):
    logger.info("-" * 50)
    logger.info(f"BOT Login -> {bot.user}")
    logger.info(f"BOT Owner -> {owner}")
    logger.info("-" * 50)
    logger.info(f"invite bot: https://discordapp.com/api/oauth2/authorize?client_id={bot.user.id}"
                f"&permissions=52224&scope=bot")
    logger.info("-" * 50)
