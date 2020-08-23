# -*- coding: utf-8 -*-

import json
import logging

import discord
from discord.ext import commands

import option
from data.lib import command, check, language

lang = json.load(open("data/cache__language.json", "r"))
logger = logging.getLogger()


class RadioPlayer(commands.Cog, name=f"Radio - {lang['help-msg']['type-player']}"):
    @commands.command(help=lang['help-msg']['join'])
    @commands.check(check.is_public)
    async def join(self, ctx):
        await command.radio_join(ctx)

    @commands.command(help=lang['help-msg']['exit'])
    @commands.check(check.is_public)
    @commands.check(check.is_join)
    async def exit(self, ctx):
        await command.radio_exit(ctx)

    @commands.command(help=lang['help-msg']['skip'])
    @commands.cooldown(rate=3, per=50, type=commands.BucketType.user)
    @commands.check(check.is_public)
    @commands.check(check.is_join)
    async def skip(self, ctx):
        await command.radio_skip(ctx)

    @commands.command(help=lang['help-msg']['now-play'])
    @commands.check(check.is_public)
    async def now_play(self, ctx):
        await command.radio_now_play(ctx)

    @commands.command(help=lang['help-msg']['repeat'])
    @commands.check(check.is_public)
    @commands.check(check.is_join)
    async def repeat(self, ctx):
        await command.radio_repeat(ctx)

    @commands.command(help=lang['help-msg']['play'])
    @commands.check(check.is_public)
    @commands.check(check.is_join)
    async def play(self, ctx, query=None):
        if query is None:
            embed = discord.Embed(title=lang['title']['nothing-to-say'],
                                  description=f"```{lang['msg']['play-fail']}```",
                                  color=option.color.info)
            await ctx.send(embed=embed)
            return

        await command.radio_play(ctx, query)

    @commands.command(help=lang['help-msg']['search'])
    @commands.check(check.is_public)
    async def search(self, ctx, query=None):
        if query is None:
            embed = discord.Embed(title=lang['title']['nothing-to-say'],
                                  description=f"```{lang['msg']['find-fail']}```",
                                  color=option.color.info)
            await ctx.send(embed=embed)
            return

        await command.radio_search(ctx, query)
