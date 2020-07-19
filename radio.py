# -*- coding: utf-8 -*-

import os
import sys
import random
import logging
import asyncio
import hashlib
import subprocess

try:
    import discord
    from discord.ext import commands
    from discord.ext.commands.cooldowns import BucketType
except ModuleNotFoundError:
    print("===< Installing Module >===")
    try:
        subprocess.run(['pip', 'install', 'discord'])
        subprocess.run(['pip', 'install', 'discord.py'])
        subprocess.run(['pip', 'install', 'PyNaCl'])
    except OSError:
        subprocess.run(['pip3', 'install', 'discord'])
        subprocess.run(['pip3', 'install', 'discord.py'])
        subprocess.run(['pip3', 'install', 'PyNaCl'])
    print("===========================")

    import discord
    from discord.ext import commands
    from discord.ext.commands.cooldowns import BucketType

try:
    from data.lib import guild, language, log, music, playlist, start_page, token
except ModuleNotFoundError:
    print("Fail to load Cat library...")
    print(" - PLZ Download again")
    print(" - Download: https://github.com/chick0/RadioBOT")
    sys.exit(-1)

try:
    import option
except ModuleNotFoundError:
    print("Option File is Missing!")
    sys.exit(-2)
##################################################################################
# Setting
log.create_logger()
logger = logging.getLogger()

lang = language.get_data()
p_list = playlist.get_playlist()

bot_token = token.get_token()
bot = commands.Bot(command_prefix=option.prefix)
radioWorker = dict()


##################################################################################
# Radio Class
class Radio:
    def __init__(self, ctx, voice_client):
        self.ctx = ctx
        self.client = voice_client
        self.playNow = random.randint(0, len(p_list) - 1)
        self.played = [self.playNow]
        self.stat = [0, 0]
        # { type: ["play_mode", "play_next"], play_mode: {0: "normal", 1: "play play_next", 2: "repeat mode"} }
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
                                      description=f"```{lang['msg']['save']}```", color=option.color.info)
                asyncio.run_coroutine_threadsafe(self.ctx.send(embed=embed), bot.loop)
                asyncio.run_coroutine_threadsafe(self.client.disconnect(), bot.loop)
            else:
                if self.stat[0] == 0:
                    self.playNow = random.randint(0, len(p_list) - 1)
                    while True:
                        if len(self.played) == len(p_list):
                            del self.played[:]
                            break

                        if self.playNow in self.played:
                            self.playNow = random.randint(0, len(p_list) - 1)
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
            player = discord.FFmpegOpusAudio(p_list[self.playNow]['name'],
                                             executable="./bin/ffmpeg.exe")
        except OSError:
            player = discord.FFmpegOpusAudio(p_list[self.playNow]['name'])

        if self.stat[0] != 2:
            asyncio.Task(self.send_play(self.ctx), loop=bot.loop)
        self.client.play(player, after=self.play_next)

    async def send_play(self, ctx):
        if option.private_mode:
            return
        else:
            now_play = lang['msg']['track-info'].replace("#artist#", p_list[self.playNow]['artist'])
            now_play = now_play.replace("#title#", p_list[self.playNow]['title'])
            warn = ""
            if p_list[self.playNow]['user_upload'] is True:
                warn = lang['msg']['warn-user-upload']
            try:
                embed = discord.Embed(title=lang['title']['now-play'],
                                      description=f"```{now_play}```\n{warn}",
                                      color=option.color.normal)
                await ctx.send(embed=embed)
            except discord.errors.Forbidden:
                await ctx.send(f"> {lang['title']['now-play']}\n```{now_play}```\n{warn}")
                if self.ctx == ctx:
                    await self.ctx.send(lang['msg']['perm-missing'])
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

        embed = discord.Embed(title=lang['title']['nothing-to-say'],
                              description=f"```{lang['msg']['plz-join-voice']}```",
                              color=option.color.info)
        await ctx.send(embed=embed)
        return
    except discord.errors.ClientException as join_error_ClientException:
        logger.error(f"Radio connection error at {ctx.guild.id} [{join_error_ClientException}]")

        embed = discord.Embed(title=lang['title']['nothing-to-say'],
                              description=f"```{lang['msg']['join-error']}```",
                              color=option.color.info)
        await ctx.send(embed=embed)
        return

    if voice_client.is_playing():
        embed = discord.Embed(title=lang['title']['nothing-to-say'],
                              description=f"```{lang['msg']['i-am-working']}```",
                              color=option.color.info)
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
        embed = discord.Embed(title=lang['title']['nothing-to-say'],
                              description=f"```{lang['msg']['radio-dead']}```",
                              color=option.color.info)
        await ctx.send(embed=embed)
    return


async def radio_skip(ctx):
    try:
        stat = radioWorker[ctx.guild.id].get_stat()
        if stat[0] == 2:
            embed = discord.Embed(title=lang['title']['cant-use'],
                                  description=f"```{lang['msg']['private-mode-enable']}```",
                                  color=option.color.warn)
            await ctx.send(embed=embed)
        else:
            radioWorker[ctx.guild.id].get_client().stop()
    except KeyError:
        logger.error(f"No radioWorker at {ctx.guild.id}")
        embed = discord.Embed(title=lang['title']['nothing-to-say'],
                              description=f"```{lang['msg']['radio-dead']}```",
                              color=option.color.info)
        await ctx.send(embed=embed)
    return


async def radio_nowplay(ctx):
    if option.private_mode:
        logger.warning("[private_mode] is working")
        try:
            embed = discord.Embed(title=lang['title']['cant-use'],
                                  description=f"```{lang['msg']['private-mode-enable']}```",
                                  color=option.color.warn)
            await ctx.send(embed=embed)
        except discord.errors.Forbidden:
            await ctx.send(f"> {lang['title']['cant-use']}\n```{lang['msg']['private-mode-enable']}```")
        return

    try:
        await radioWorker[ctx.guild.id].send_play(ctx)
    except KeyError:
        logger.error(f"No radioWorker at {ctx.guild.id}")
        embed = discord.Embed(title=lang['title']['nothing-to-say'],
                              description=f"```{lang['msg']['radio-dead']}```",
                              color=option.color.info)
        await ctx.channel.send(embed=embed)
    return


async def radio_repeat(ctx):
    try:
        stat = radioWorker[ctx.guild.id].get_stat()
        mode_msg = str()
        if stat[0] == 2:
            mode_msg = lang['msg']['set-mode-normal']
            radioWorker[ctx.guild.id].set_stat(0, 0)
        elif stat[0] != 2:
            mode_msg = lang['msg']['set-mode-repeat']
            radioWorker[ctx.guild.id].set_stat(2, 0)

        embed = discord.Embed(title=lang['title']['set-complete'],
                              description=f"```{mode_msg}```",
                              color=option.color.normal)
        await ctx.send(embed=embed)
    except KeyError:
        logger.error(f"No Radio Worker at {ctx.guild.id}")
        embed = discord.Embed(title=lang['title']['nothing-to-say'],
                              description=f"```{lang['msg']['radio-dead']}```",
                              color=option.color.info)
        await ctx.send(embed=embed)
        return
    return


async def radio_play(ctx, query):
    try:
        play_next = int(query)
    except ValueError:
        embed = discord.Embed(title=lang['title']['nothing-to-say'],
                              description=f"```{lang['msg']['plz-int']}```",
                              color=option.color.info)
        await ctx.send(embed=embed)
        return

    if play_next < 0 or play_next > len(p_list) - 1:
        embed = discord.Embed(title=lang['title']['nothing-to-say'],
                              description=f"```{lang['msg']['not-in-list']}```",
                              color=option.color.info)
        await ctx.send(embed=embed)
        return

    try:
        t_next = lang['msg']['next-song'].replace("#artist#", p_list[play_next]['artist'])
        t_next = t_next.replace("#title#", p_list[play_next]['title'])

        radioWorker[ctx.guild.id].set_stat(1, play_next)
        embed = discord.Embed(title=lang['title']['set-complete'],
                              description=f"```{t_next}```",
                              color=option.color.normal)
        await ctx.send(embed=embed)
    except KeyError:
        logger.error(f"No Radio Worker at {ctx.guild.id}")
        embed = discord.Embed(title=lang['title']['nothing-to-say'],
                              description=f"```{lang['msg']['radio-lost']}```",
                              color=option.color.info)
        await ctx.send(embed=embed)
        return
    return


async def radio_search(ctx, query):
    try:
        search_id = int(query)
        try:
            search_result = lang['msg']['track-info'].replace("#artist#", p_list[search_id]['artist'])
            search_result = search_result.replace("#title#", p_list[search_id]['title'])

            embed = discord.Embed(title=lang['title']['search-complete'],
                                  color=option.color.normal)
            embed.add_field(name=lang['msg']['track-no'].replace("#number#", str(search_id)),
                            value=search_result,
                            inline=True)
            await ctx.send(embed=embed)
            return
        except IndexError:
            embed = discord.Embed(title=lang['title']['nothing-to-say'],
                                  description=f"```{lang['msg']['search-result-zero']}```",
                                  color=option.color.warn)
            await ctx.send(embed=embed)
            return
    except ValueError:
        result = 0
        if len(query) < 3:
            embed = discord.Embed(title=lang['title']['search-cancel'],
                                  description=f"```{lang['msg']['too-short-query']}```",
                                  color=option.color.warn)
            await ctx.send(embed=embed)
            return
        embed = discord.Embed(title=lang['title']['search-complete'],
                              color=option.color.normal)
        for temp_playlist in p_list:
            def check_it(q):
                if q.upper() in str(temp_playlist['artist']).upper():
                    return True
                elif q.upper() in str(temp_playlist['title']).upper():
                    return True
                else:
                    return False

            if check_it(query):
                result += 1
                search_result = lang['msg']['track-info'].replace("#artist#", temp_playlist['artist'])
                search_result = search_result.replace("#title#", temp_playlist['title'])

                embed.add_field(
                    name=lang['msg']['track-no'].replace("#number#", str(p_list.index(temp_playlist))),
                    value=f"```{search_result}```",
                    inline=False
                )

        if result > 0:
            embed.set_footer(text=lang['msg']['search-result-footer'].replace("#number#", str(result)))
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title=lang['title']['nothing-to-say'],
                                  description=f"```{lang['msg']['search-result-zero']}```",
                                  color=option.color.warn)
            await ctx.send(embed=embed)
    return


##################################################################################
# Radio Function - Permission check
def is_public(ctx):
    return not isinstance(ctx.message.channel, discord.abc.PrivateChannel)


##################################################################################
# Radio Function - For owner
class RadioOwner(commands.Cog, name=f"Radio - {lang['help-msg']['type-admin']}"):
    @commands.command(help=lang['help-msg']['admin-close'])
    @commands.check(is_public)
    async def close(self, ctx):
        if await ctx.bot.is_owner(user=ctx.author):
            await ctx.send(lang['msg']['shutdown-bot'])
            if len(radioWorker) > 0:
                await self.leave_all(ctx)
            await ctx.bot.close()
        else:
            logger.warning(f"[{ctx.author.id}]{ctx.author} try to use owner command")

    @commands.command(help=lang['help-msg']['admin-leave-all'])
    @commands.check(is_public)
    async def leave_all(self, ctx):
        if await ctx.bot.is_owner(user=ctx.author):
            await ctx.send(lang['msg']['turn-off-all'])
            key = list(radioWorker.keys())
            for temp_key in key:
                await radioWorker[temp_key].get_ctx().send(f"```{lang['msg']['shutdown-by-admin']}```")
                await radioWorker[temp_key].get_client().disconnect()
        else:
            logger.warning(f"[{ctx.author.id}]{ctx.author} try to use owner command")

    @commands.command(help=lang['help-msg']['admin-reload-playlist'])
    @commands.check(is_public)
    async def reload_playlist(self, ctx):
        if await ctx.bot.is_owner(user=ctx.author):
            if len(radioWorker) > 0:
                await self.leave_all(ctx)

            global p_list
            p_list = playlist.get_playlist()
            await ctx.send(f"```{lang['msg']['complete-reload-playlist']}```")
        else:
            logger.warning(f"[{ctx.author.id}]{ctx.author} try to use owner command")

    @commands.command(help=lang['help-msg']['upload'])
    @commands.cooldown(rate=1, per=10, type=BucketType.guild)
    @commands.check(is_public)
    async def upload(self, ctx):
        if await ctx.bot.is_owner(user=ctx.author):
            if len(ctx.message.attachments) == 0:
                embed = discord.Embed(title=lang['title']['upload-cancel'],
                                      description=f"```{lang['msg']['upload-cancel-no-upload']}```",
                                      color=option.color.info)
                await ctx.send(embed=embed)
                return

            try:
                logger.info("Testing User Upload Directory")
                with open("./data/user_upload/test", "w") as upload_directory_test:
                    upload_directory_test.write("Hello, World")
                    logger.info("OK! - Upload Directory Alive")
            except FileNotFoundError:
                logger.info("FAIL - Try to create User Upload Directory")
                try:
                    os.mkdir("./data/user_upload")
                    logger.info("OK! - Upload Directory is Online")
                except PermissionError:
                    logger.info("FAIL - Cancel Upload event")
                    embed = discord.Embed(title=lang['title']['upload-cancel'],
                                          description=f"```{lang['msg']['upload-cancel-directory']}```",
                                          color=option.color.warn)
                    await ctx.send(embed=embed)
                    return

            for item in ctx.message.attachments:
                extension = item.filename.split(".")[-1]
                hash_result = hashlib.sha1(item.filename.encode()).hexdigest()

                file_name = f"{ctx.author.id}_{hash_result}.{extension}"
                await item.save(fp=os.fspath(f"./data/user_upload/{file_name}"))

                data = music.get_data(f"./data/user_upload/{file_name}")
                if data is not None:
                    embed = discord.Embed(title=lang['title']['upload-complete'],
                                          color=option.color.normal)
                    embed.add_field(name=lang['title']['upload-result-info'],
                                    value=f"{data['artist']} - {data['title']}", inline=False)
                    embed.add_field(name=lang['title']['upload-result-name'],
                                    value=f"{file_name}", inline=False)
                    await ctx.send(embed=embed)
                    p_list.append(data)
                else:
                    embed = discord.Embed(title=lang['title']['upload-cancel'],
                                          description=f"```{lang['msg']['upload-cancel-fail']}```",
                                          color=option.color.info)
                    await ctx.send(embed=embed)
                    os.remove(f"./data/user_upload/{file_name}")
        else:
            logger.warning(f"[{ctx.author.id}]{ctx.author} try to use owner command")


##################################################################################
# Radio Function - For @everyone
class RadioPlayer(commands.Cog, name=f"Radio - {lang['help-msg']['type-player']}"):
    @commands.command(help=lang['help-msg']['join'])
    @commands.check(is_public)
    async def join(self, ctx):
        await radio_join(ctx)

    @commands.command(help=lang['help-msg']['exit'])
    @commands.check(is_public)
    async def exit(self, ctx):
        await radio_exit(ctx)

    @commands.command(help=lang['help-msg']['skip'])
    @commands.check(is_public)
    async def skip(self, ctx):
        await radio_skip(ctx)

    @commands.command(help=lang['help-msg']['now-play'])
    @commands.check(is_public)
    async def nowplay(self, ctx):
        await radio_nowplay(ctx)

    @commands.command(help=lang['help-msg']['repeat'])
    @commands.check(is_public)
    async def repeat(self, ctx):
        await radio_repeat(ctx)

    @commands.command(help=lang['help-msg']['play'])
    @commands.check(is_public)
    async def play(self, ctx, query=None):
        if query is None:
            embed = discord.Embed(title=lang['title']['nothing-to-say'],
                                  description=f"```{lang['msg']['play-fail']}```",
                                  color=option.color.info)
            await ctx.send(embed=embed)
            return

        await radio_play(ctx, query)

    @commands.command(help=lang['help-msg']['search'])
    @commands.check(is_public)
    async def search(self, ctx, query=None):
        if query is None:
            embed = discord.Embed(title=lang['title']['nothing-to-say'],
                                  description=f"```{lang['msg']['find-fail']}```",
                                  color=option.color.info)
            await ctx.send(embed=embed)
            return

        await radio_search(ctx, query)


##################################################################################
# Radio **Short** Function - For @everyone
class RadioShort(commands.Cog, name=f"Radio - {lang['help-msg']['type-short']}"):
    @commands.command(help=lang['help-msg']['short-join'].replace("#prefix#", option.prefix))
    @commands.check(is_public)
    async def j(self, ctx):
        await radio_join(ctx)

    @commands.command(help=lang['help-msg']['short-exit'].replace("#prefix#", option.prefix))
    @commands.check(is_public)
    async def e(self, ctx):
        await radio_exit(ctx)

    @commands.command(help=lang['help-msg']['short-skip'].replace("#prefix#", option.prefix))
    @commands.check(is_public)
    async def s(self, ctx):
        await radio_skip(ctx)

    @commands.command(help=lang['help-msg']['short-now-play'].replace("#prefix#", option.prefix))
    @commands.check(is_public)
    async def np(self, ctx):
        await radio_nowplay(ctx)

    @commands.command(help=lang['help-msg']['short-repeat'].replace("#prefix#", option.prefix))
    @commands.check(is_public)
    async def re(self, ctx):
        await radio_repeat(ctx)

    @commands.command(help=lang['help-msg']['short-play'].replace("#prefix#", option.prefix))
    @commands.check(is_public)
    async def p(self, ctx, query=None):
        if query is None:
            embed = discord.Embed(title=lang['title']['nothing-to-say'],
                                  description=f"```{lang['msg']['play-fail']}```",
                                  color=option.color.info)
            await ctx.send(embed=embed)
            return

        await radio_play(ctx, query)

    @commands.command(help=lang['help-msg']['short-search'].replace("#prefix#", option.prefix))
    @commands.check(is_public)
    async def sh(self, ctx, query=None):
        if query is None:
            embed = discord.Embed(title=lang['title']['nothing-to-say'],
                                  description=f"```{lang['msg']['find-fail']}```",
                                  color=option.color.info)
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
    try:
        logger.info(f"[{ctx.author.id}]{ctx.author} use [{ctx.message.content}] command at [{ctx.guild.id}]")
    except AttributeError:
        logger.critical("Logging fail")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandOnCooldown):
        # I need help in here
        await ctx.send(error)
        return

    try:
        logger.error(f"[{ctx.author.id}]{ctx.author} meet the [{error}] at [{ctx.guild.id}]")
    except AttributeError:
        logger.critical("Logging fail")


@bot.event
async def on_ready():
    await start_page.set_status(bot, "idle", "listening", lang['title']['music'])

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
