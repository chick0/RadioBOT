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
        subprocess.run(['pip', '-r', 'install', 'requirements.txt'])
    except OSError:
        subprocess.run(['pip3', '-r', 'install', 'requirements.txt'])
    except Exception as e:
        print(f"Unexpected Error {e.__class__.__name__}!")
        print("Try to user install...")

        try:
            subprocess.run(['pip', '-r', 'install', 'requirements.txt', '--user'])
        except OSError:
            subprocess.run(['pip3', '-r', 'install', 'requirements.txt', '--user'])
    print("===========================")

    import discord
    from discord.ext import commands

try:
    import option
except ModuleNotFoundError:
    print("Option File is Missing!")
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
bot_token = token.get_token()


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

    start_page.invite_me(bot=bot, permission=52224)
    guild.dump_guild(bot=bot, save=option.save_guild_data)


##################################################################################
# BOT Start
try:
    logger.info("RadioBOT Starting...")
    bot.run(bot_token)
except discord.errors.LoginFailure:
    logger.critical("**Invalid token loaded!!**")
    token.reset_token()
except Exception as e:
    logger.critical("=" * 30)
    logger.critical("<< Bot is dead >>")
    logger.critical(e)
    logger.critical("=" * 30)

logger.info("Try to remove cache file...")
cache.run()
