# -*- coding: utf-8 -*-

import os
import time
import json
import random
import logging
import asyncio
import subprocess

try:
    import discord
    from discord.ext import commands, tasks
except ModuleNotFoundError:
    subprocess.run(['pip', 'install', 'discord==1.0.1'])
    subprocess.run(['pip', 'install', 'discord.py==1.3.2'])
    subprocess.run(['pip', 'install', 'PyNaCl==1.3.0'])
    import discord
    from discord.ext import commands, tasks

import data.lib.option as option_manager
import data.lib.token_manager as token_manager
import data.lib.playlist_loader as playlist
import data.lib.language_manager as language_manager

##################################################################################
# Logger Setting
log_formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s]: %(message)s",
    "%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

boot_time = time.strftime("%Y-%m-%d %HH %MM", time.localtime(time.time()))
try:
    file_handler = logging.FileHandler(f"log/{boot_time}.log")
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)
except FileNotFoundError:
    os.mkdir("log/")
    file_handler = logging.FileHandler(f"log/{boot_time}.log")
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)
##################################################################################
# Checking Essential directory
try:
    logger.info("Checking Essential directory...")
    with open("./data/check_data_directory", "w", encoding="utf8") as test_f:
        test_f.write(boot_time)
    logger.info("OK! - Essential directory is alive")
except FileNotFoundError:
    logger.info("FAIL - Directory not found")
    os.mkdir("data/")

del boot_time
##################################################################################
# Setting
option = option_manager.get_option()
bot_token = token_manager.get_token()
playlist = playlist.get_playlist()
language = language_manager.get_data()

bot = commands.Bot(command_prefix=option['prefix'])
radioWorker = dict()


##################################################################################
# Radio Class
class Radio:
    def __init__(self, ctx, voice_client):
        self.ctx = ctx
        self.client = voice_client
        self.playNow = random.randint(0, len(playlist) - 1)
        self.played = [self.playNow]
        self.stat = [0, 0]
        logger.info(f"Radio ON at {self.ctx.guild.id} by [{self.ctx.author.id}]{self.ctx.author}")

    def __del__(self):
        logger.info(f"Radio OFF at {self.ctx.guild.id}")

    def get_ctx(self):
        return self.ctx

    def get_client(self):
        return self.client

    def get_stat(self):
        return self.stat[0], self.stat[1]

    def set_stat(self, new_mode, new_next):
        self.stat[0] = new_mode
        self.stat[1] = new_next

    def play_next(self, error):
        if error is not None:
            logger.error(f"Oops, radio player meet the [{error}]")

        if self.client.is_connected():
            if len(self.client.channel.members) == 1:
                embed = discord.Embed(title=":deciduous_tree: :evergreen_tree: :deciduous_tree: :evergreen_tree:",
                                      description=language['msg']['save'], color=option['color']['info'])
                asyncio.run_coroutine_threadsafe(self.ctx.send(embed=embed), bot.loop)
                asyncio.run_coroutine_threadsafe(self.client.disconnect(), bot.loop)
            else:
                if self.stat[0] == 0:
                    self.playNow = random.randint(0, len(playlist) - 1)
                    while True:
                        if len(self.played) == len(playlist):
                            del self.played[:]
                            break

                        if self.playNow in self.played:
                            self.playNow = random.randint(0, len(playlist) - 1)
                        else:
                            break
                    self.played.append(self.playNow)
                    self.play_radio()
                elif self.stat[0] == 1:
                    self.playNow = self.stat[1]
                    self.stat[0] = 0
                    self.play_radio()
                elif self.stat[0] == 2:
                    self.play_radio()
        else:
            del radioWorker[self.ctx.guild.id]

    def play_radio(self):
        try:
            player = discord.FFmpegOpusAudio(option['music_dir'] + playlist[self.playNow]['name'],
                                             executable="bin/ffmpeg.exe")
        except OSError:
            player = discord.FFmpegOpusAudio(option['music_dir'] + playlist[self.playNow]['name'])

        if self.stat[0] != 2:
            asyncio.Task(self.send_play(self.ctx), loop=bot.loop)
        self.client.play(player, after=self.play_next)

    async def send_play(self, ctx):
        if option['private_mode']:
            return
        else:
            now_play = language['msg']['track-info'].replace("#artist#", playlist[self.playNow]['artist'])
            now_play = now_play.replace("#title#", playlist[self.playNow]['title'])
            try:
                embed = discord.Embed(title=language['title']['now-play'],
                                      description=now_play,
                                      color=option['color']['normal'])
                await ctx.send(embed=embed)
            except discord.errors.Forbidden:
                await ctx.send(f"> {language['title']['now-play']}\n```{now_play}```")
                if self.ctx == ctx:
                    await self.ctx.send(language['msg']['perm-missing'])
                    logger.warning(f"Permission missing at {self.ctx.guild.id}")
            return


##################################################################################
# Radio Worker
async def radio_join(ctx):
    try:
        logger.info(f"Radio Connected at {ctx.guild.id}")
        voice_client = await ctx.author.voice.channel.connect()
    except AttributeError as join_error_AttributeError:
        logger.error(f"Radio connection error at {ctx.guild.id} [{join_error_AttributeError}]")

        embed = discord.Embed(title=language['title']['nothing-to-say'],
                              description=language['msg']['plz-join-voice'], color=option['color']['info'])
        await ctx.send(embed=embed)
        return
    except discord.errors.ClientException as join_error_ClientException:
        logger.error(f"Radio connection error at {ctx.guild.id} [{join_error_ClientException}]")

        embed = discord.Embed(title=language['title']['nothing-to-say'],
                              description=language['msg']['join-error'], color=option['color']['info'])
        await ctx.send(embed=embed)
        return

    if voice_client.is_playing():
        embed = discord.Embed(title=language['title']['nothing-to-say'],
                              description=language['msg']['i-am-working'], color=option['color']['info'])
        await ctx.send(embed=embed)
        return

    radioWorker[ctx.guild.id] = Radio(ctx, voice_client)
    radioWorker[ctx.guild.id].play_radio()


async def radio_exit(ctx):
    try:
        await radioWorker[ctx.guild.id].get_client().disconnect()
        await ctx.send(":wave:")
    except KeyError:
        logger.error(f"No radioWorker at {ctx.guild.id}")
        embed = discord.Embed(title=language['title']['nothing-to-say'],
                              description=language['msg']['radio-dead'], color=option['color']['info'])
        await ctx.send(embed=embed)
    return


async def radio_skip(ctx):
    try:
        stat = radioWorker[ctx.guild.id].get_stat()
        if stat[0] == 2:
            embed = discord.Embed(title=language['title']['cant-use'],
                                  description=language['msg']['private-mode-enable'], color=option['color']['warn'])
            await ctx.send(embed=embed)
        else:
            radioWorker[ctx.guild.id].get_client().stop()
    except KeyError:
        logger.error(f"No radioWorker at {ctx.guild.id}")
        embed = discord.Embed(title=language['title']['nothing-to-say'],
                              description=language['msg']['radio-dead'], color=option['color']['info'])
        await ctx.send(embed=embed)
    return


async def radio_nowplay(ctx):
    if option['private_mode']:
        logger.warning("[private_mode] is working")
        try:
            embed = discord.Embed(title=language['title']['cant-use'],
                                  description=language['msg']['private-mode-enable'], color=option['color']['warn'])
            await ctx.send(embed=embed)
        except discord.errors.Forbidden:
            await ctx.send(f"> {language['title']['cant-use']}\n```{language['msg']['private-mode-enable']}```")
        return

    try:
        await radioWorker[ctx.guild.id].send_play(ctx)
    except KeyError:
        logger.error(f"No radioWorker at {ctx.guild.id}")
        embed = discord.Embed(title=language['title']['nothing-to-say'],
                              description=language['msg']['radio-dead'], color=option['color']['info'])
        await ctx.channel.send(embed=embed)
    return


async def radio_repeat(ctx):
    try:
        stat = radioWorker[ctx.guild.id].get_stat()
        mode_msg = str()
        if stat[0] == 2:
            mode_msg = language['msg']['set-mode-normal']
            radioWorker[ctx.guild.id].set_stat(0, 0)
        elif stat[0] != 2:
            mode_msg = language['msg']['set-mode-repeat']
            radioWorker[ctx.guild.id].set_stat(2, 0)

        embed = discord.Embed(title=language['title']['set-complete'],
                              description=mode_msg, color=option['color']['normal'])
        await ctx.send(embed=embed)
    except KeyError:
        logger.error(f"No Radio Worker at {ctx.guild.id}")
        embed = discord.Embed(title=language['title']['nothing-to-say'],
                              description=language['msg']['radio-dead'], color=option['color']['info'])
        await ctx.send(embed=embed)
        return
    return


async def radio_play(ctx, query):
    try:
        play_next = int(query)
    except ValueError:
        embed = discord.Embed(title=language['title']['nothing-to-say'],
                              description=language['msg']['plz-int'], color=option['color']['info'])
        await ctx.send(embed=embed)
        return

    if play_next < 0 or play_next > len(playlist) - 1:
        embed = discord.Embed(title=language['title']['nothing-to-say'],
                              description=language['msg']['not-in-list'], color=option['color']['info'])
        await ctx.send(embed=embed)
        return

    try:
        t_next = language['msg']['next-play'].replace("#artist#", playlist[play_next]['artist'])
        t_next = t_next.replace("#title#", playlist[play_next]['title'])

        radioWorker[ctx.guild.id].set_stat(1, play_next)
        embed = discord.Embed(title=language['title']['set-complete'],
                              description=t_next, color=option['color']['normal'])
        await ctx.send(embed=embed)
    except KeyError:
        logger.error(f"No Radio Worker at {ctx.guild.id}")
        embed = discord.Embed(title=language['title']['nothing-to-say'],
                              description=language['msg']['radio-lost'], color=option['color']['info'])
        await ctx.send(embed=embed)
        return
    return


async def radio_search(ctx, query):
    try:
        search_id = int(query)
        try:
            search_result = language['msg']['track-info'].replace("#artist#", playlist[search_id]['artist'])
            search_result = search_result.replace("#title#", playlist[search_id]['title'])

            embed = discord.Embed(title=language['title']['search-complete'], color=option['color']['normal'])
            embed.add_field(name=language['msg']['track-no'].replace("#number#", str(search_id)),
                            value=search_result, inline=True)
            await ctx.send(embed=embed)
            return
        except IndexError:
            embed = discord.Embed(title=language['title']['nothing-to-say'],
                                  description=language['msg']['search-result-zero'], color=option['color']['warn'])
            await ctx.send(embed=embed)
            return
    except ValueError:
        result = 0
        if len(query) < 3:
            embed = discord.Embed(title=language['title']['search-cancel'],
                                  description=language['msg']['too-short-query'], color=option['color']['warn'])
            await ctx.send(embed=embed)
            return
        embed = discord.Embed(title=language['title']['search-complete'], color=option['color']['normal'])
        for temp_playlist in playlist:
            if query.upper() in str(temp_playlist['artist']).upper() or query.upper() in str(temp_playlist['title']).upper():
                result += 1
                search_result = language['msg']['track-info'].replace("#artist#", temp_playlist['artist'])
                search_result = search_result.replace("#title#", temp_playlist['title'])

                embed.add_field(name=language['msg']['track-no'].replace("#number#", str(playlist.index(temp_playlist))),
                                value=search_result, inline=False)

        if result > 0:
            embed.set_footer(text=language['msg']['search-result-footer'].replace("#number#", str(result)))
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title=language['title']['nothing-to-say'],
                                  description=language['msg']['search-result-zero'], color=option['color']['warn'])
            await ctx.send(embed=embed)
    return


##################################################################################
# Radio Function - Permission check
def is_owner(ctx):
    return ctx.author.id == option['owner_id']


def is_public(ctx):
    return not isinstance(ctx.message.channel, discord.abc.PrivateChannel)


##################################################################################
# Radio Function - For owner
class RadioOwner(commands.Cog, name=f"Radio - {language['help-msg']['type-admin']}"):
    @commands.command(help=language['help-msg']['admin-close'])
    @commands.check(is_owner)
    async def close(self, ctx):
        await ctx.send(language['msg']['shutdown-bot'])
        if len(radioWorker) > 0:
            await self.leave_all(ctx)
        await bot.close()

    @commands.command(help=language['help-msg']['admin-leave-all'])
    @commands.check(is_owner)
    async def leave_all(self, ctx):
        await ctx.send(language['msg']['turn-off-all'])
        key = list(radioWorker.keys())
        for temp_key in key:
            await radioWorker[temp_key].get_ctx().send(f"```{language['msg']['shutdown-by-admin']}```")
            await radioWorker[temp_key].get_client().disconnect()
        return


##################################################################################
# Radio Function - For @everyone
class RadioPlayer(commands.Cog, name=f"Radio - {language['help-msg']['type-player']}"):
    @commands.command(help=language['help-msg']['join'])
    @commands.check(is_public)
    async def join(self, ctx):
        """#""".replace("#", language['help-msg']['join'])
        await radio_join(ctx)

    @commands.command(help=language['help-msg']['exit'])
    @commands.check(is_public)
    async def exit(self, ctx):
        await radio_exit(ctx)

    @commands.command(help=language['help-msg']['skip'])
    @commands.check(is_public)
    async def skip(self, ctx):
        await radio_skip(ctx)

    @commands.command(help=language['help-msg']['nowplay'])
    @commands.check(is_public)
    async def nowplay(self, ctx):
        await radio_nowplay(ctx)

    @commands.command(help=language['help-msg']['repeat'])
    @commands.check(is_public)
    async def repeat(self, ctx):
        await radio_repeat(ctx)

    @commands.command(help=language['help-msg']['play'])
    @commands.check(is_public)
    async def play(self, ctx, query=None):
        if query is None:
            embed = discord.Embed(title=language['title']['nothing-to-say'],
                                  description=language['msg']['play-fail'], color=option['color']['info'])
            await ctx.send(embed=embed)
            return

        await radio_play(ctx, query)

    @commands.command(help=language['help-msg']['search'])
    @commands.check(is_public)
    async def search(self, ctx, query=None):
        if query is None:
            embed = discord.Embed(title=language['title']['nothing-to-say'],
                                  description=language['msg']['find-fail'], color=option['color']['info'])
            await ctx.send(embed=embed)
            return

        await radio_search(ctx, query)


##################################################################################
# Radio **Short** Function - For @everyone
class RadioShort(commands.Cog, name=f"Radio - {language['help-msg']['type-short']}"):
    @commands.command(help=language['help-msg']['short-join'].replace("#prefix#", option['prefix']))
    @commands.check(is_public)
    async def j(self, ctx):
        await radio_join(ctx)

    @commands.command(help=language['help-msg']['short-exit'].replace("#prefix#", option['prefix']))
    @commands.check(is_public)
    async def e(self, ctx):
        await radio_exit(ctx)

    @commands.command(help=language['help-msg']['short-skip'].replace("#prefix#", option['prefix']))
    @commands.check(is_public)
    async def s(self, ctx):
        await radio_skip(ctx)

    @commands.command(help=language['help-msg']['short-nowplay'].replace("#prefix#", option['prefix']))
    @commands.check(is_public)
    async def np(self, ctx):
        await radio_nowplay(ctx)

    @commands.command(help=language['help-msg']['short-repeat'].replace("#prefix#", option['prefix']))
    @commands.check(is_public)
    async def re(self, ctx):
        await radio_repeat(ctx)

    @commands.command(help=language['help-msg']['short-play'].replace("#prefix#", option['prefix']))
    @commands.check(is_public)
    async def p(self, ctx, query=None):
        if query is None:
            embed = discord.Embed(title=language['title']['nothing-to-say'],
                                  description=language['msg']['play-fail'], color=option['color']['info'])
            await ctx.send(embed=embed)
            return

        await radio_play(ctx, query)

    @commands.command(help=language['help-msg']['short-search'].replace("#prefix#", option['prefix']))
    @commands.check(is_public)
    async def sh(self, ctx, query=None):
        if query is None:
            embed = discord.Embed(title=language['title']['nothing-to-say'],
                                  description=language['msg']['find-fail'], color=option['color']['info'])
            await ctx.send(embed=embed)
            return

        await radio_search(ctx, query)


bot.add_cog(RadioPlayer())
bot.add_cog(RadioOwner())
bot.add_cog(RadioShort())


##################################################################################
# BOT Event
@bot.event
async def on_command(ctx):
    logger.info(f"[{ctx.author.id}]{ctx.author} use [{ctx.message.content}] command at [{ctx.guild.id}]")


@bot.event
async def on_command_error(ctx, error):
    logger.error(f"[{ctx.author.id}]{ctx.author} meet the [{error}] at [{ctx.guild.id}]")


@bot.event
async def on_ready():
    auto = await bot.application_info()
    if auto.bot_public and option['private_mode']:
        logger.warning("This BOT is Public bot!")
        logger.warning("Private mode is now OFF")
        option['private_mode'] = False

    if option['auto_owner']:
        option['owner_id'] = auto.owner.id
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Activity(type=discord.ActivityType.listening,
                                                        name=language['title']['music']))

    logger.info("-" * 50)
    logger.info(f"BOT Login -> {bot.user}")
    logger.info(f"BOT Owner -> {option['owner_id']}")
    if option['owner_id'] != auto.owner.id:
        logger.warning("BOT Owner is not the same as Auto Detect mode")
        logger.warning(f"Auto Detect Owner -> {auto.owner.id} / {auto.owner}")
    logger.info("-" * 50)
    logger.info(f"invite bot: https://discordapp.com/api/oauth2/authorize?client_id={bot.user.id}"
                f"&permissions=52224&scope=bot")
    logger.info("-" * 50)
    logger.info(f"Connected to {len(bot.guilds)} servers")
    result = list()
    for temp_guild in bot.guilds:
        logger.info(f" - Name: {temp_guild.name}")
        result.append({'id': temp_guild.id, 'name': temp_guild.name})
    logger.info("-" * 50)
    if option['save_guild_data'] is True:
        with open("./data/guild.json", "w", encoding="utf8") as guild_f:
            guild_f.write(json.dumps(result, sort_keys=True, indent=4))


##################################################################################
# BOT Start
try:
    logger.info("RadioBOT Starting...")
    bot.run(bot_token)
except discord.errors.LoginFailure:
    logger.critical("**Invalid token loaded!!**")
    token_manager.reset_token()
except Exception as e:
    logger.critical("=" * 30)
    logger.critical("<< Bot is dead >>")
    logger.critical(e)
    logger.critical("=" * 30)
