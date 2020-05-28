# -*- coding: utf-8 -*-

import os
import sys
import time
import json
import random
import logging
import asyncio
import getpass
import subprocess

try:
    import eyed3
except ModuleNotFoundError:
    subprocess.run(['pip3', 'install', 'eyeD3==0.9.5'])
    import eyed3

try:
    import discord
    from discord.ext import commands, tasks
except ModuleNotFoundError:
    subprocess.run(['pip3', 'install', 'discord==1.0.1'])
    subprocess.run(['pip3', 'install', 'discord.py==1.3.2'])
    subprocess.run(['pip3', 'install', 'PyNaCl==1.3.0'])
    import discord
    from discord.ext import commands, tasks
##################################################################################
# Logger Setting
log_formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s]: %(message)s",
    "%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

boot_time = time.strftime("%Y-%m-%d %H%M", time.localtime(time.time()))
try:
    file_handler = logging.FileHandler(f"log/radio_{boot_time}.log")
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)
except FileNotFoundError:
    os.mkdir("log/")
    file_handler = logging.FileHandler(f"log/radio_{boot_time}.log")
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)
del boot_time

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)
##################################################################################
# Loading Option
option_file = "option.json"
logger.info(f"Loading Option from [{option_file}]")
try:
    option = json.load(open(option_file))
except FileNotFoundError:
    logger.info(f"[{option_file}] not found, load default settings")
    option = {
        "auto_owner": True,
        "owner_id": 0,
        "color": {
            "info": 16763981,
            "normal": 16579836,
            "warn": 13450043
        },
        "prefix": ";",
        "private_mode": False,
        "music_dir": "./data/music/",
        "token_file": "./data/token.json"
    }
    with open(option_file, "w", encoding="utf8") as option_f:
        option_f.write(json.dumps(option, indent=4))
##################################################################################
# Loading Token
logger.info(f"Loading Token from [{option['token_file']}]")
try:
    botToken = json.load(open(option['token_file']))['token']
    if len(botToken) == 59:
        logger.info("Token is Ready!")
    else:
        logger.critical(f"Invalid token load from [{option['token_file']}]")
        botToken = "#"
except FileNotFoundError as e:
    logger.critical(f"Failed to load token from [{option['token_file']}] cause {e}")
    botToken = "#"

if botToken == "#":
    botToken = getpass.getpass("What is **Your** Token: ")
    try:
        logger.info(f"Update Token at [{option['token_file']}]")
        with open(option['token_file'], "w", encoding="utf8") as f:
            f.write(json.dumps({"token": botToken}, indent=4))
    except Exception as e:
        logger.critical(f"Fail to save Token at [{option['token_file']}] cause {e}")
##################################################################################
# Global variable
color = option['color']
prefix = option['prefix']
radioWorker, playlist = dict(), list()

bot = commands.Bot(command_prefix=prefix)
bot.remove_command('help')


##################################################################################
# etc.. Function
def dump_guild():
    guilds = list(bot.guilds)
    result = list()
    for temp_guild in guilds:
        t_d = {'id': temp_guild.id, 'name': temp_guild.name}
        result.append(t_d)
    with open("data/guild.json", "w", encoding="utf8") as guild:
        guild.write(json.dumps(result, sort_keys=True, indent=4))


##################################################################################
# Loading music!
logger.info(f"Loading music from [{option['music_dir']}]...")
try:
    musicFiles = os.listdir(option['music_dir'])
    for musicFile in musicFiles:
        try:
            media = eyed3.load(option['music_dir'] + musicFile)
            artist = media.tag.artist
            title = media.tag.title

            if artist is None:
                logger.warning(f"Missing artist in [{musicFile}]")
                artist = "None"
            if title is None:
                logger.warning(f"Missing Title in [{musicFile}]")
                title = "None"
            playlist.append({'artist': artist, 'title': title, 'name': musicFile})
        except AttributeError:
            logger.warning(f"Fail to get data from [{musicFile}]")
            logger.warning(f"Remove [{musicFile}] from playlist")
    try:
        def get_titles(lists):
            return lists['title']


        playlist = sorted(playlist, key=get_titles)
    except TypeError:
        logger.warning("Fail to sort playlist!!")
    logger.info(f"Music is Ready! + {len(playlist)}")
except Exception as e:
    logger.critical(f"Can't Load music at [{option['music_dir']}] cause {e}")
    sys.exit(-1)


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
                                      description="전기와 트래픽을 아껴주세요!", color=color['info'])
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
            try:
                now_play = [playlist[self.playNow]['artist'], playlist[self.playNow]['title']]
                embed = discord.Embed(title=":headphones: - Now Playing",
                                      description=f"{now_play[0]} - {now_play[1]}",
                                      color=color['normal'])
                await ctx.send(embed=embed)
            except discord.errors.Forbidden:
                await ctx.send(f"> :headphones: - Now Playing\n"
                               f"```{playlist[self.playNow]['artist']} - {playlist[self.playNow]['title']}```")
                if self.ctx == ctx:
                    await self.ctx.send(":warning: [링크 첨부] 권한이 부족합니다")
                    logger.warning(f"Permission missing at {self.ctx.guild.id}")
            return


##################################################################################
# Radio Worker
async def radio_help(ctx):
    embed = discord.Embed(title="도움말", color=color['normal'])
    embed.add_field(name=f"{prefix}join", value=bot.get_command("join").help, inline=False)
    embed.add_field(name=f"{prefix}exit", value=bot.get_command("exit").help, inline=False)
    embed.add_field(name=f"{prefix}skip", value=bot.get_command("skip").help, inline=False)
    embed.add_field(name=f"{prefix}nowplay", value=bot.get_command("nowplay").help, inline=False)

    embed.add_field(name=f"{prefix}repeat", value=bot.get_command("repeat").help, inline=False)
    embed.add_field(name=f"{prefix}play [<트랙번호>]", value=bot.get_command("play").help, inline=False)
    embed.add_field(name=f"{prefix}search [<검색어>]", value=bot.get_command("search").help, inline=False)
    await ctx.send(embed=embed)
    return


async def radio_join(ctx):
    try:
        logger.info(f"Radio Connected at {ctx.guild.id}")
        voice_client = await ctx.author.voice.channel.connect()
    except AttributeError as join_error_AttributeError:
        logger.error(f"Radio connection error at {ctx.guild.id} [{join_error_AttributeError}]")

        embed = discord.Embed(title="...", description="음성 채널 입장후 다시 시도해 주세요.", color=color['info'])
        await ctx.send(embed=embed)
        return
    except discord.errors.ClientException as join_error_ClientException:
        logger.error(f"Radio connection error at {ctx.guild.id} [{join_error_ClientException}]")

        embed = discord.Embed(title="...", description="음성 채널에 입장에 실패하였습니다", color=color['info'])
        await ctx.send(embed=embed)
        return

    if voice_client.is_playing():
        embed = discord.Embed(title="저기요?", description="이미 라디오가 작동하고 있다는데..", color=color['info'])
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
        embed = discord.Embed(title="?", description="라디오가 꺼저있다는데..", color=color['info'])
        await ctx.send(embed=embed)
    return


async def radio_skip(ctx):
    try:
        stat = radioWorker[ctx.guild.id].get_stat()
        if stat[0] == 2:
            embed = discord.Embed(title="사용불가", description="반복재생 모드가 활성화 되어있습니다!", color=color['warn'])
            await ctx.send(embed=embed)
        else:
            radioWorker[ctx.guild.id].get_client().stop()
    except KeyError:
        logger.error(f"No radioWorker at {ctx.guild.id}")
        embed = discord.Embed(title="?", description="라디오가 꺼저있다는데..", color=color['info'])
        await ctx.send(embed=embed)
    return


async def radio_nowplay(ctx):
    if option['private_mode']:
        logger.warning("[private_mode] is working")
        try:
            embed = discord.Embed(title="사용불가", description="보호모드가 활성화 되어있습니다", color=color['warn'])
            await ctx.send(embed=embed)
        except discord.errors.Forbidden:
            await ctx.send("> 사용불가\n```보호모드가 활성화 되어있습니다```")
        return

    try:
        await radioWorker[ctx.guild.id].send_play(ctx)
    except KeyError:
        logger.error(f"No radioWorker at {ctx.guild.id}")
        embed = discord.Embed(title="?", description="라디오가 꺼저있다는데..", color=color['info'])
        await ctx.channel.send(embed=embed)
    return


async def radio_repeat(ctx):
    try:
        stat = radioWorker[ctx.guild.id].get_stat()
        mode = str()
        if stat[0] == 2:
            mode = "일반재생"
            radioWorker[ctx.guild.id].set_stat(0, 0)
        elif stat[0] != 2:
            mode = "반복"
            radioWorker[ctx.guild.id].set_stat(2, 0)

        embed = discord.Embed(title="변경완료!", description=f"{mode} 모드가 활성화 되었습니다!", color=color['normal'])
        await ctx.send(embed=embed)
    except KeyError:
        logger.error(f"No Radio Worker at {ctx.guild.id}")
        embed = discord.Embed(title="?", description="라디오가 꺼저있다는데..", color=color['info'])
        await ctx.send(embed=embed)
        return
    return


async def radio_play(ctx, query):
    try:
        play_next = int(query)
    except ValueError:
        embed = discord.Embed(title="어..", description="재생 지정은 번호로만 지정이 가능해요", color=color['info'])
        await ctx.send(embed=embed)
        return

    if play_next < 0 or play_next > len(playlist) - 1:
        embed = discord.Embed(title="어...", description="해당 트랙은 확인되지 않았습니다", color=color['info'])
        await ctx.send(embed=embed)
        return

    try:
        radioWorker[ctx.guild.id].set_stat(1, play_next)
        embed = discord.Embed(title="설정 완료!",
                              description=f"다음은 [{playlist[play_next]['artist']}]의 "
                                          f"[{playlist[play_next]['title']}](이)가 재생됩니다",
                              color=color['normal'])
        await ctx.send(embed=embed)
    except KeyError:
        logger.error(f"No Radio Worker at {ctx.guild.id}")
        embed = discord.Embed(title="?", description="라디오가 꺼저있다는데..", color=color['info'])
        await ctx.send(embed=embed)
        return
    return


async def radio_search(ctx, query):
    try:
        search_id = int(query)
        try:
            search_result = [playlist[search_id]['artist'], playlist[search_id]['title']]

            embed = discord.Embed(title="검색 완료", color=color['normal'])
            embed.add_field(name=f"{search_id}번 트랙", value=f"{search_result[0]} - {search_result[1]}", inline=True)
            await ctx.send(embed=embed)
            return
        except IndexError:
            embed = discord.Embed(title="어...", description="검색 결과 **정말** 없음", color=color['warn'])
            await ctx.send(embed=embed)
            return
    except ValueError:
        result = 0
        if len(query) < 3:
            embed = discord.Embed(title="검색 취소됨", description="너무 짧은 검색어", color=color['warn'])
            await ctx.send(embed=embed)
            return
        embed = discord.Embed(title="검색 완료", color=color['normal'])
        for temp_playlist in playlist:
            if query.upper() in str(temp_playlist['artist']).upper() or query.upper() in str(
                    temp_playlist['title']).upper():
                result += 1
                embed.add_field(name=f"{playlist.index(temp_playlist)}번 트랙",
                                value=f"{temp_playlist['artist']} - {temp_playlist['title']}",
                                inline=False)

        if result > 0:
            embed.set_footer(text=f"검색된 트랙) {result}개 발견됨")
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="어...", description="검색 결과 **정말** 없음", color=color['warn'])
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
@bot.command(hidden=True)
@commands.check(is_owner)
async def close(ctx):
    await ctx.send(":wave: 봇을 종료합니다.")
    if len(radioWorker) > 0:
        await leave_all(ctx)
    await bot.close()


@bot.command(hidden=True)
@commands.check(is_owner)
async def leave_all(ctx):
    await ctx.send("켜저있는 다른 라디오를 모두 종료합니다.")
    key = list(radioWorker.keys())
    for temp_key in key:
        await radioWorker[temp_key].get_ctx().send("`봇 관리자에 의하여 라디오가 종료되었습니다.`")
        await radioWorker[temp_key].get_client().disconnect()
    return


@bot.command(hidden=True)
@commands.check(is_owner)
async def change_set(ctx, option_name=None, option_value=None):
    if option_name is None or option_value is None:
        try:
            embed = discord.Embed(title="잘못된 사용법", description=f"{prefix}change_set [<옵션 명>] [<값>]",
                                  color=color['warn'])
            await ctx.send(embed=embed)
        except discord.errors.Forbidden:
            await ctx.send(":warning: [링크 첨부] 권한이 부족합니다")
            await ctx.send(f"> 잘못된 사용법\n```{prefix}change_set [<옵션 명>] [<값>]```")
        return
    option_able = list(json.load(open(option_file)).keys())
    if option_name not in option_able:
        try:
            embed = discord.Embed(title="지원하지 않는 옵션", description=f"옵션 명\n```{option_able}```", color=color['warn'])
            await ctx.send(embed=embed)
        except discord.errors.Forbidden:
            await ctx.send(":warning: [링크 첨부] 권한이 부족합니다")
            await ctx.send(f"> 지원하지 않는 옵션\n```{option_able}```")
        return

    try:
        embed = discord.Embed(title="변경 완료!", description=f"변경한 옵션```{option_name}```\n"
                                                          f"변경 전 / 변경 후```{option[option_name]} / {option_value}```",
                              color=color['normal'])
        await ctx.send(embed=embed)
    except discord.errors.Forbidden:
        await ctx.send(":warning: [링크 첨부] 권한이 부족합니다")
        await ctx.send(f"> 변경 완료!\n변경한 옵션```{option_name}```\n",
                       f"변경 전 / 변경 후```{option[option_name]} / {option_value}```")
    try:
        if isinstance(option[option_name], int):
            option[option_name] = int(option_value)
        elif isinstance(option[option_name], bool):
            option[option_name] = bool(option_value)
        elif isinstance(option[option_name], dict):
            option[option_name] = dict(option_value)
        elif isinstance(option[option_name], str):
            option[option_name] = str(option_value)
        else:
            raise ValueError
    except ValueError:
        await ctx.send("`옵션 값이 잘못되어 변경이 취소 됩니다`")
        return

    await ctx.send(":warning: 옵션이 변경되었습니다, 일부 옵션은 봇을 다시 시작해야 적용됩니다")
    logger.warning("Option Changed, please restart bot")
    with open(option_file, "w", encoding="utf8") as option_change:
        option_change.write(json.dumps(option, indent=4))


##################################################################################
# Radio Function - For @everyone
@bot.command()
@commands.check(is_public)
async def help(ctx):
    """라디오의 설명서를 봅니다"""
    await radio_help(ctx)


@bot.command()
@commands.check(is_public)
async def join(ctx):
    """라디오의 전원을 킵니다! (음성채널에 입장해야 합니다.)"""
    await radio_join(ctx)


@bot.command()
@commands.check(is_public)
async def exit(ctx):
    """라디오의 전원을 끕니다..."""
    await radio_exit(ctx)


@bot.command()
@commands.check(is_public)
async def skip(ctx):
    """지금 재생되고 있는 노래를 넘깁니다"""
    await radio_skip(ctx)


@bot.command()
@commands.check(is_public)
async def nowplay(ctx):
    """지금 재생되는 음악의 정보를 확인합니다"""
    await radio_nowplay(ctx)


@bot.command()
@commands.check(is_public)
async def repeat(ctx):
    """반복재생 모드를 [활성화/비활성화] 합니다"""
    await radio_repeat(ctx)


@bot.command()
@commands.check(is_public)
async def play(ctx, query=None):
    """다음에 재생할 노래를 지정합니다"""
    if query is None:
        embed = discord.Embed(title="어..", description="무엇을 틀었어야 하는 걸까요?", color=color['info'])
        await ctx.send(embed=embed)
        return

    await radio_play(ctx, query)


@bot.command()
@commands.check(is_public)
async def search(ctx, query=None):
    """검색기능은 트랙번호 또는 작곡가 또는 제목으로 검색이 가능합니다"""
    if query is None:
        embed = discord.Embed(title="어..", description="무엇을 찾았어야 하는 걸까요?", color=color['info'])
        await ctx.send(embed=embed)
        return

    await radio_search(ctx, query)


##################################################################################
# Radio **Short** Function - For @everyone
@bot.command(hidden=True)
@commands.check(is_public)
async def h(ctx):
    await radio_help(ctx)


@bot.command(hidden=True)
@commands.check(is_public)
async def j(ctx):
    await radio_join(ctx)


@bot.command(hidden=True)
@commands.check(is_public)
async def e(ctx):
    await radio_exit(ctx)


@bot.command(hidden=True)
@commands.check(is_public)
async def s(ctx):
    await radio_skip(ctx)


@bot.command(hidden=True)
@commands.check(is_public)
async def np(ctx):
    await radio_nowplay(ctx)


@bot.command(hidden=True)
@commands.check(is_public)
async def re(ctx):
    await radio_repeat(ctx)


@bot.command(hidden=True)
@commands.check(is_public)
async def p(ctx, query=None):
    if query is None:
        embed = discord.Embed(title="어..", description="무엇을 틀었어야 하는 걸까요?", color=color['info'])
        await ctx.send(embed=embed)
        return

    await radio_play(ctx, query)


@bot.command(hidden=True)
@commands.check(is_public)
async def sh(ctx, query=None):
    if query is None:
        embed = discord.Embed(title="어..", description="무엇을 찾았어야 하는 걸까요?", color=color['info'])
        await ctx.send(embed=embed)
        return

    await radio_search(ctx, query)


##################################################################################
# BOT Event
@bot.event
async def on_command(ctx):
    logger.info(f"[{ctx.author.id}]{ctx.author} use [{ctx.message.content}] command at [{ctx.guild.id}]")


@bot.event
async def on_command_error(ctx, error):
    logger.error(f"[{ctx.author.id}]{ctx.author} meet the [{error}] error at [{ctx.guild.id}]")


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
                              activity=discord.Activity(type=discord.ActivityType.listening, name="Music"))

    logger.info("-" * 50)
    logger.info(f"BOT Login -> {bot.user}")
    logger.info(f"BOT Owner -> {option['owner_id']}")
    if option['owner_id'] != auto.owner.id:
        logger.warning("BOT Owner is not the same as Auto Detect mode")
        logger.warning(f"Auto Detect Owner -> {auto.owner.id} / {auto.owner}")
    logger.info("-" * 50)
    logger.info(
        f"invite bot: https://discordapp.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=52224&scope=bot")
    logger.info("-" * 50)
    logger.info(f"Connected to {len(bot.guilds)} servers")
    logger.info("-> data/guild.json")
    logger.info("-" * 50)
    dump_guild()


##################################################################################
# BOT Start
try:
    bot.run(botToken)
except discord.errors.LoginFailure:
    logger.critical("Invalid token loaded!!")
    try:
        logger.info(f"Reset Token at [{option['token_file']}]")
        with open(option['token_file'], "w", encoding="utf8") as f:
            f.write(json.dumps({"token": "#"}, indent=4))
    except Exception as e:
        logger.critical(f"Fail to Reset Token -> {e}")
except Exception as e:
    logger.critical(f"Bot is dead -> {e}")

