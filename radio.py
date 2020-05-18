# -*- coding: utf-8 -*-

import json
import time
import ffmpeg
import random
import discord
import asyncio
import logging
import getpass
##################################################################################
log_formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s]: %(message)s",
    "%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("log/radio_{0}.log".format(time.strftime('%Y-%m-%d %H%M', time.localtime(time.time()))))
file_handler.setFormatter(log_formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)
##################################################################################
logger.info('Loading Token from [token.json]')
try:
    botToken = json.load(open('data/token.json'))['token']
    if len(botToken) == 59:
        logger.info('Token is Ready!')
    else:
        logger.critical('Invalid token load from [token.json]')
        botToken = '#'
except:
    logger.critical('Failed to load token from [token.json]')
    botToken = '#'

if botToken == '#':
    botToken = getpass.getpass('What is **Your** Token: ')
##################################################################################
owner_id = 686309666690826265 # 0 == Auto Detect
client = discord.Client()

color = {'normal': 0xFCFCFC,
         'info': 0xFFCC4D,
         'warn': 0xCD3B3B}

radioWorker = dict()
##################################################################################
logger.info('Loading playlist...')
try:
    playlist = json.load(open('data/playlist.json'))
    logger.info('Playlist load completed!')
except:
    logger.critical('Playlist load fail!!')
##################################################################################
class Radio:
    def __init__(self, message, voiceclient):
        self.message = message
        self.client = voiceclient
        self.playNow = random.randint(0, len(playlist) - 1)
        self.played = list()
        self.played.append(self.playNow)
        self.stat = [0, 0]
        logger.info('Radio ON at {0} by [{1}]{2}'.format(self.message.guild.id, self.message.author.id, self.message.author))

    def __del__(self):
        logger.info('Radio OFF at {0} by [{1}]{2}'.format(self.message.guild.id, self.message.author.id, self.message.author))

    def end(self):
        asyncio.run_coroutine_threadsafe(self.client.disconnect(), client.loop)
        try:
            del radioWorker[self.message.guild.id]
        except:
            pass

    def getclient(self):
        return self.client

    def getstat(self):
        return (self.stat[0], self.stat[1])

    def setstat(self, mode, playTrack):
        self.stat[0] = mode
        self.stat[1] = playTrack

    def playnext(self, error):
        try:
            if self.client.is_connected():
                if len(self.client.channel.members) == 1:
                    embed = discord.Embed(title=":deciduous_tree: :evergreen_tree: :deciduous_tree: :evergreen_tree:", description='전기와 트래픽을 아껴주세요!', color=color['info'])
                    asyncio.run_coroutine_threadsafe(self.message.channel.send(embed=embed), client.loop)
                    self.end()
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
                        self.playsound()
                    elif self.stat[0] == 1:
                        self.playNow = self.stat[1]
                        self.stat[0] = 0
                        self.playsound()
                    elif self.stat[0] == 2:
                        self.playsound()
            else:
                del radioWorker[self.message.guild.id]
        except:
            try:
                del radioWorker[self.message.guild.id]
            except:
                pass

    def playsound(self):
        try:
            player = discord.FFmpegOpusAudio("data/music/{0}".format(playlist[self.playNow]['name']), executable="bin/ffmpeg.exe")
        except OSError:
            player = discord.FFmpegOpusAudio("data/music/{0}".format(playlist[self.playNow]['name']))
        try:
            if self.stat[0] != 2:
                asyncio.Task( self.sendPlay(self.message), loop=client.loop)
            self.client.play(player, after=self.playnext )
        except Exception as e:
            logger.critical('Voice Connection is dead at {0}, cause {1}'.format(self.message.guild.id, e))
            embed = discord.Embed(title="Warning!", description='<@{0}> (이)가 음악 재생 중에 연결이 끊어졌어요!'.format(client.user.id), color=color['warn'])
            asyncio.run_coroutine_threadsafe(self.message.channel.send(embed=embed), client.loop)
            try:
                asyncio.run_coroutine_threadsafe(self.client.disconnect(), client.loop)
            except:
                pass
            return

    async def sendPlay(self, message):
        try:
            embed = discord.Embed(title=":headphones: - Now Playing", description='{0} - {1}'.format(playlist[self.playNow]['author'], playlist[self.playNow]['title']), color=color['normal'])
            embed.url = playlist[self.playNow]['url']
            await message.channel.send(embed=embed)
        except:
            await message.channel.send(':warning: [링크 첨부] 권한이 부족합니다 :warning:')
            if self.message == message:
                logger.error('Permission missing at {0}'.format(self.message.guild.id))
                self.end()

async def radio_play(message, voiceclient):
    try:
        if voiceclient.is_playing():
            embed = discord.Embed(title="저기요?", description='이미 라디오가 작동하고 있다는데..', color=color['info'])
            await message.channel.send(embed=embed)
            return
    except:
        embed = discord.Embed(title="저기요?", description='라디오가 꺼저있다는데..', color=color['info'])
        await message.channel.send(embed=embed)
        return
    if discord.opus.is_loaded() == False:
        try:
            discord.opus._load_default()
        except:
            logger.critical('opus loading fail!!')

            embed = discord.Embed(title="Warning!", description='opus loading fail!'.format(client.user.id), color=color['warn'])
            await message.channel.send(embed=embed)
            return

    radioWorker[message.guild.id] = Radio(message, voiceclient)
    radioWorker[message.guild.id].playsound()
##################################################################################
def dump_guild():
    guilds = list(client.guilds)
    result = list()
    for i in range(0, len(guilds)):
        t_d = {'id': guilds[i].id, 'name': guilds[i].name}
        result.append(t_d)
    with open('data/guild.json', "w", encoding='utf8') as f:
        f.write(json.dumps(result))
##################################################################################
@client.event
async def on_ready():
    global owner_id
    auto = await client.application_info()
    if owner_id == 0:
        owner_id = auto.owner.id
    await client.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.listening, name="Radio"))

    logger.info('-'*50)
    logger.info('BOT Login -> {0.user}'.format(client))
    logger.info('BOT Owner -> {0}'.format(owner_id))
    if owner_id != auto.owner.id:
        logger.warning('BOT Owner is not the same as Auto Detect mode')
        logger.warning('Auto Detect Owner -> {0} / {1}'.format(auto.owner.id, auto.owner))
    logger.info('-'*50)
    logger.info('invite bot: https://discordapp.com/api/oauth2/authorize?client_id={0}&permissions=52224&scope=bot'.format(client.user.id))
    logger.info('-'*50)
    logger.info('Connected to {0} servers'.format(len(client.guilds)))
    logger.info('-> data/guild.json')
    logger.info('-'*50)
    dump_guild()
##################################################################################
@client.event
async def on_message(message):
    if message.author.bot or isinstance(message.channel, discord.abc.PrivateChannel):
        return

    if client.user.mentioned_in(message):
        await message.channel.send("I'm a teapot")
        return

    if message.content.startswith(';dump') or message.content.startswith(';여ㅡㅔ'):
        if message.author.id == owner_id:
            await message.author.send(radioWorker.keys())
            await message.author.send('radioWorker: {0}'.format(len(radioWorker)))
            await message.author.send('playlist: {0}'.format(len(playlist)))
            dump_guild()
        else:
            logger.warning('[{0}]{1} try to use [{2}] command!'.format(message.author.id, message.author, message.content))
        return

    if message.content.startswith(';die') or message.content.startswith(';얃'):
        if message.author.id == owner_id:
            await message.channel.send(':wave: 봇을 종료합니다')
            await client.close()
        else:
            logger.warning('[{0}]{1} try to use [{2}] command!'.format(message.author.id, message.author, message.content))
            return
##################################################################################
    if message.content.startswith(';run'):
        if message.author.id == owner_id:
            command = message.content[4:].strip()
            await message.channel.send(command)

            run = eval(command)
            await message.channel.send('```\n{0}\n```'.format(run))
##################################################################################
    if message.content.startswith(";reset"):
        if message.author.id == message.guild.owner_id:
            logger.info('[{0}]{1} use [{2}] command at [{3}]'.format(message.author.id, message.author, message.content, message.guild.id))
            try:
                del radioWorker[message.guild.id]
            except:
                pass

            embed = discord.Embed(title='Reset', description='<@{0}>의 음성 채팅방 입장 정보를 초기화 했습니다.'.format(client.user.id), color=color['info'])
            await message.channel.send(embed=embed)
        else:
            logger.warning('[{0}]{1} try to use [{2}] command at [{3}]'.format(message.author.id, message.author, message.content, message.guild.id))
            embed = discord.Embed(title="Radio Reset", description='권한이 부족합니다.', color=color['warn'])
            await message.channel.send(embed=embed)
        return
##################################################################################
    if message.content.startswith(';help'):
        logger.info('[{0}]{1} use [{2}] command at [{3}]'.format(message.author.id, message.author, message.content, message.guild.id))

        embed = discord.Embed(title="도움말", color=color['normal'])
        embed.add_field(name=";join", value='라디오의 전원을 킵니다 (음성채널에 들어가야 합니다)', inline=False)
        embed.add_field(name=";exit", value='라디오의 전원을 끕니다', inline=False)
        embed.add_field(name=";list", value='저장된 음악의 목록을 확인합니다', inline=False)
        embed.add_field(name=";skip", value='지금 나오는 노래를 건너뜁니다', inline=False)
        embed.add_field(name=";reset", value='음성채널 입장정보를 초기화 합니다', inline=False)
        embed.add_field(name=";nowplay", value='지금 재생되는 음악의 정보를 확인합니다', inline=False)

        embed.add_field(name=";repeat", value='반복재생 모드를 활성화/비활성화 합니다', inline=False)
        embed.add_field(name=";play [<트랙번호>]", value='다음에 재생할 노래를 지정합니다', inline=False)
        embed.add_field(name=";search [<검색어>]", value='검색기능은 트랙번호 또는 작곡가 또는 제목으로 검색이 가능합니다', inline=False)
        await message.channel.send(embed=embed)
        return

    if message.content.startswith(';h'):
        logger.info('[{0}]{1} use [{2}] command at [{3}]'.format(message.author.id, message.author, message.content, message.guild.id))

        embed = discord.Embed(title="도움말", color=color['normal'])
        embed.add_field(name=";j", value='라디오의 전원을 킵니다 (음성채널에 들어가야 합니다)', inline=False)
        embed.add_field(name=";e", value='라디오의 전원을 끕니다', inline=False)
        embed.add_field(name=";l", value='저장된 음악의 목록을 확인합니다', inline=False)
        embed.add_field(name=";s", value='지금 나오는 노래를 건너뜁니다', inline=False)
        embed.add_field(name=";np", value='지금 재생되는 음악의 정보를 확인합니다', inline=False)

        embed.add_field(name=";re", value='반복재생 모드를 활성화/비활성화 합니다', inline=False)
        embed.add_field(name=";p [<트랙번호>]", value='다음에 재생할 노래를 지정합니다', inline=False)
        embed.add_field(name=";sh [<검색어>]", value='검색기능은 트랙번호 또는 작곡가 또는 제목으로 검색이 가능합니다', inline=False)
        await message.channel.send(embed=embed)
        return
##################################################################################
    if message.content.startswith(";list") or message.content.startswith(";l") or message.content.startswith(";playlist") or message.content.startswith(";pl"):
        logger.info('[{0}]{1} use [{2}] command at [{3}]'.format(message.author.id, message.author, message.content, message.guild.id))
        content = str(message.content).split()
        try:
            page = int(content[1])
        except:
            page = 1

        if page == 0:
            page = 1

        if page != 1:
            tmp = page - 1
            page = tmp * 10 + 1

        if page > len(playlist):
            embed = discord.Embed(title="Playlist?", description='최대 범위를 넘겼습니다.', color=color['info'])
            await message.channel.send(embed=embed)
        elif page < 0:
            embed = discord.Embed(title="Playlist?", description='최소 범위를 넘겼습니다.', color=color['info'])
            await message.channel.send(embed=embed)
        else:
            embed = discord.Embed(title="Playlist!", color=color['normal'])
            for i in range(page - 1, page + 9):
                try:
                    embed.add_field(name="{0}번 트랙".format(i), value='{0} - {1}'.format(playlist[i]['author'], playlist[i]['title']), inline=True)
                except:
                    pass
            await message.channel.send(embed=embed)
        return

    if message.content.startswith(";search") or message.content.startswith(";sh"):
        logger.info('[{0}]{1} use [{2}] command at [{3}]'.format(message.author.id, message.author, message.content, message.guild.id))
        content = str(message.content).split()
        try:
            searchItem = content[1]
        except:
            embed = discord.Embed(title="어..", description='무엇을 찾았어야 하는 걸까요?', color=color['info'])
            await message.channel.send(embed=embed)
            return

        try:
            search = int(searchItem)
            try:
                author, title = playlist[search]['author'], playlist[search]['title']

                embed = discord.Embed(title="검색 완료", color=color['normal'])
                embed.add_field(name="{0}번 트랙".format(search), value='{0} - {1}'.format(author, title), inline=True)
                await message.channel.send(embed=embed)
                return
            except:
                embed = discord.Embed(title="어..", description='무엇을 찾았어야 하는 걸까요?', color=color['info'])
                await message.channel.send(embed=embed)
                return
        except:
            result = 0
            if len(searchItem) < 3:
                embed = discord.Embed(title="검색 취소됨", description='너무 짧은 검색어', color=color['warn'])
                await message.channel.send(embed=embed)
                return
            embed = discord.Embed(title="검색 완료", color=color['normal'])
            for i in range(0, len(playlist)):
                if searchItem.upper() in playlist[i]['author'].upper() or searchItem.upper() in playlist[i]['title'].upper():
                    result += 1
                    embed.add_field(name="{0}번 트랙".format(i), value='{0} - {1}'.format(playlist[i]['author'], playlist[i]['title']), inline=False)

            if result > 0:
                embed.set_footer(text='검색된 트랙) {0}개 발견됨'.format(result))
                await message.channel.send(embed=embed)
            else:
                embed = discord.Embed(title="어...", description='검색 결과 *정말* 없음', color=color['warn'])
                await message.channel.send(embed=embed)
        return

    if message.content.startswith(";repeat") or message.content.startswith(";re"):
        logger.info('[{0}]{1} use [{2}] command at [{3}]'.format(message.author.id, message.author, message.content, message.guild.id))
        try:
            stat = radioWorker[message.guild.id].getstat()
            mode = str()
            if stat[0] == 2:
                mode = '일반재생'
                radioWorker[message.guild.id].setstat(0, 0)
            elif stat[0] != 2:
                mode = '반복'
                radioWorker[message.guild.id].setstat(2, 0)

            embed = discord.Embed(title="변경완료!", description='{0} 모드가 활성화 되었습니다!'.format(mode), color=color['normal'])
            await message.channel.send(embed=embed)
        except KeyError:
            logger.error('No Radio Worker at {0}'.format(message.guild.id))
            embed = discord.Embed(title="?", description='라디오가 꺼저있다는데..', color=color['info'])
            await message.channel.send(embed=embed)
            return
        return

    if message.content.startswith(";play") or message.content.startswith(";p"):
        logger.info('[{0}]{1} use [{2}] command at [{3}]'.format(message.author.id, message.author, message.content, message.guild.id))
        content = str(message.content).split()
        try:
            playNext = content[1]
        except:
            embed = discord.Embed(title="어..", description='무엇을 틀었어야 하는 걸까요?', color=color['info'])
            await message.channel.send(embed=embed)
            return

        try:
            playTrack = int(playNext)
        except:
            embed = discord.Embed(title="어..", description='재생 지정은 번호로만 지정이 가능해요', color=color['info'])
            await message.channel.send(embed=embed)
            return

        if playTrack < 0 or playTrack > len(playlist) - 1:
            embed = discord.Embed(title="어...", description='해당 트랙은 확인되지 않았습니다', color=color['info'])
            await message.channel.send(embed=embed)
            return

        try:
            radioWorker[message.guild.id].setstat(1, playTrack)
            embed = discord.Embed(title="설정 완료!", description='다음은 \[{0}\]\(이\)가 재생됩니다'.format(playlist[playTrack]['title']), color=color['normal'])
            await message.channel.send(embed=embed)
        except KeyError:
            logger.error('No Radio Worker at {0}'.format(message.guild.id))
            embed = discord.Embed(title="?", description='라디오가 꺼저있다는데..', color=color['info'])
            await message.channel.send(embed=embed)
            return
        return

    if message.content.startswith(";join") or message.content.startswith(";j"):
        logger.info('[{0}]{1} use [{2}] command at [{3}]'.format(message.author.id, message.author, message.content, message.guild.id))
        try:
            logger.info('Radio Connected at {0}'.format(message.guild.id))

            voiceclient = await message.author.voice.channel.connect()
            await radio_play(message, voiceclient)
        except AttributeError as e:
            logger.error('Radio connection error at {0} [{1}]'.format(message.guild.id, e))

            embed = discord.Embed(title="...", description='음성 채널 입장후 다시 시도해 주세요.',color=color['info'])
            await message.channel.send(embed=embed)
        except discord.errors.ClientException as e:
            logger.error('Radio connection error at {0} [{1}]'.format(message.guild.id, e))

            embed = discord.Embed(title="...", description='이미 음성 채널에 입장하고 있어요!',color=color['info'])
            await message.channel.send(embed=embed)
        return

    if message.content.startswith(";nowplay") or message.content.startswith(";np"):
        logger.info('[{0}]{1} use [{2}] command at [{3}]'.format(message.author.id, message.author, message.content, message.guild.id))
        try:
            await radioWorker[message.guild.id].sendPlay(message)
        except KeyError:
            logger.error('No Radio Worker at {0}'.format(message.guild.id))
            embed = discord.Embed(title="?", description='라디오가 꺼저있다는데..', color=color['info'])
            await message.channel.send(embed=embed)
        return

    if message.content.startswith(";skip") or message.content.startswith(";s"):
        logger.info('[{0}]{1} use [{2}] command at [{3}]'.format(message.author.id, message.author, message.content, message.guild.id))
        try:
            stat = radioWorker[message.guild.id].getstat()
            if stat[0] == 2:
                embed = discord.Embed(title="사용불가", description='반복재생 모드가 활성화 되어있습니다!', color=color['warn'])
                await message.channel.send(embed=embed)
            else:
                radioWorker[message.guild.id].getclient().stop()
        except KeyError:
            logger.error('No Radio Worker at {0}'.format(message.guild.id))
            embed = discord.Embed(title="?", description='라디오가 꺼저있다는데..', color=color['info'])
            await message.channel.send(embed=embed)
        return

    if message.content.startswith(";exit") or message.content.startswith(";e"):
        logger.info('[{0}]{1} use [{2}] command at [{3}]'.format(message.author.id, message.author, message.content, message.guild.id))
        try:
            logger.info('Radio Disconnected at {0}'.format(message.guild.id))
            radioWorker[message.guild.id].end()
            await message.channel.send(':wave:')
        except KeyError:
            logger.error('No Radio Worker at {0}'.format(message.guild.id))
            embed = discord.Embed(title="?", description='라디오가 꺼저있다는데..', color=color['info'])
            await message.channel.send(embed=embed)
        return
##################################################################################
client.run(botToken)

