# -*- coding: utf-8 -*-

import os
import sys
import json
import logging
import importlib
import subprocess

try:
    import discord
    from discord.ext import commands
except ModuleNotFoundError:
    print("===< Installing Module >===")
    try:
        subprocess.run(['pip', 'install', '-r', 'requirements.txt'])
    except OSError:
        subprocess.run(['pip3', 'install', '-r', 'requirements.txt'])
    except Exception as e:
        print(f"Unexpected Error {e.__class__.__name__}!")
        print("Try to user install...")

        try:
            subprocess.run(['pip', 'install', '-r', 'requirements.txt', '--user'])
        except OSError:
            subprocess.run(['pip3', 'install', '-r', 'requirements.txt', '--user'])
    print("===========================")

    import discord
    from discord.ext import commands

try:
    import option
except ModuleNotFoundError:
    print("RadioBOT Option File is Missing!")
    print(" - Download: https://github.com/chick0/RadioBOT/blob/master/option.py")
    sys.exit(-2)


from data.lib import guild, log, start_page, token, cache
from data.lib import language, playlist

##################################################################################
# Setting
log.create_logger()

language.get_data()
playlist.get_playlist()

# required variable

logger = logging.getLogger()

bot = commands.Bot(command_prefix=option.prefix)

token_worker = token.Token(file_name="token.json",
                           service="Discord")
bot_token = token_worker.get_token()
del token_worker


##################################################################################
# Command Loader

command_files = os.listdir("data/command/")
for module_file in command_files:
    module = importlib.import_module(f"data.command.{module_file.split('.')[0]}")

    for mod in dir(module):
        if not mod.startswith("__"):
            if "Cog" in getattr(module, mod).__class__.__name__:
                logger.info(f"Command Detected from '{module.__name__}' name '{mod}'")
                try:
                    bot.add_cog(getattr(module, mod)(bot))
                    logger.info("OK! - Cogs Registered")
                except Exception as e:
                    logger.critical(f"FAIL! - {e.__class__.__name__}: {e}")
del command_files


##################################################################################
# BOT Event
@bot.event
async def on_command(ctx):
    try:
        logger.info(f"[{ctx.author.id}]{ctx.author} use [{ctx.message.content}] command at [{ctx.guild.id}]")
    except AttributeError:
        logger.critical("Logging fail...")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandOnCooldown):
        await ctx.send(error)
        return

    try:
        logger.error(f"[{ctx.author.id}]{ctx.author} meet the [{error}] at [{ctx.guild.id}]")
    except AttributeError:
        logger.critical("Logging fail")


@bot.event
async def on_ready():
    lang = json.load(open("data/cache__language.json", "r"))
    await start_page.set_status(bot, "idle", "listening", lang['title']['music'])
    del lang

    start_page.bot_info(bot=bot)
    guild.dump_guild(bot=bot)


##################################################################################
# BOT Start
try:
    logger.info("RadioBOT Starting...")
    bot.run(bot_token)
except discord.errors.LoginFailure:
    logger.critical("**Invalid token loaded!!**")

    token_worker = token.Token(file_name="token.json",
                               service="Discord")
    token_worker.reset_token()
    del token_worker
except Exception as e:
    logger.critical("=" * 30)
    logger.critical("<< Bot is dead >>")
    logger.critical(e)
    logger.critical("=" * 30)

logger.info("Try to remove cache file...")
cache.run()
