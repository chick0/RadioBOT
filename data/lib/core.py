# -*- coding: utf-8 -*-

import json
import random
import asyncio
import logging

import discord

import option

logger = logging.getLogger()

# cache loader
playlist = json.load(open("data/cache__playlist.json", "r"))
lang = json.load(open("data/cache__language.json", "r"))


radioDict = dict()


class Radio:
    def __init__(self, ctx, vc):
        self.ctx = ctx
        self.voice_client = vc
        self.playNow = random.randint(0, len(playlist) - 1)
        self.played = [self.playNow]
        self.stat = [0, 0]
        # { type: ["play_mode", "play_next"], play_mode: {0: "normal", 1: "play play_next", 2: "repeat mode"} }
        logger.info(f"Radio ON at {self.ctx.guild.id} by [{self.ctx.author.id}]{self.ctx.author}")
        print(self.voice_client)

    def __del__(self):
        try:
            logger.info(f"Radio OFF at {self.ctx.guild.id}")
        except Exception as e:
            logger.info(f"Radio OFF at 'Unknown' cause '{e.__class__.__name__}'")

        try:
            asyncio.Task(coro=self.voice_client.disconnect(), loop=self.ctx.bot.loop)
        except Exception as e:
            logger.warning(f"{e.__class__.__name__}: {e}")

    def get_ctx(self):
        return self.ctx

    def get_stat(self):
        return self.stat

    def set_stat(self, new_mode, new_next):
        self.stat[0] = new_mode
        self.stat[1] = new_next

    def play_next(self, error):
        if error is not None:
            logger.error(f"Oops, radio player meet the [{error}]")

        if self.voice_client.is_connected():
            if len(self.voice_client.channel.members) == 1:
                embed = discord.Embed(title=":deciduous_tree: :evergreen_tree: :deciduous_tree: :evergreen_tree:",
                                      description=f"```{lang['msg']['save']}```", color=option.color.info)
                asyncio.run_coroutine_threadsafe(self.ctx.send(embed=embed), self.ctx.bot.loop)
                asyncio.run_coroutine_threadsafe(self.voice_client.disconnect(), self.ctx.bot.loop)
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

    def play_radio(self):
        try:
            player = discord.FFmpegOpusAudio(playlist[self.playNow]['name'],
                                             executable="./bin/ffmpeg.exe")
        except Exception as e:
            logger.warning(f"Fail to use 'bin/ffmpeg.exe' cause '{e.__class__.__name__}: {e}'")
            player = discord.FFmpegOpusAudio(playlist[self.playNow]['name'])

        if self.stat[0] != 2:
            asyncio.Task(self.send_play(self.ctx), loop=self.ctx.bot.loop)
        self.voice_client.play(player, after=self.play_next)

    async def send_play(self, ctx):
        if option.private_mode:
            return
        else:
            now_play = lang['msg']['track-info'].replace("#artist#", playlist[self.playNow]['artist'])
            now_play = now_play.replace("#title#", playlist[self.playNow]['title'])
            warn = ""
            if playlist[self.playNow]['user_upload'] is True:
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
