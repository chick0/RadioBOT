# -*- coding: utf-8 -*-

import json
import logging

import discord
from discord.ext import commands

import option
from data.lib import command, check

lang = json.load(open("data/cache__language.json", "r"))
logger = logging.getLogger()


class RadioShort(commands.Cog, name=f"Radio - {lang['help-msg']['type-short']}"):
    @commands.command(help=lang['help-msg']['short-join'].replace("#prefix#", option.prefix))
    @commands.check(check.is_public)
    async def j(self, ctx):
        await command.radio_join(ctx)

    @commands.command(help=lang['help-msg']['short-exit'].replace("#prefix#", option.prefix))
    @commands.check(check.is_public)
    async def e(self, ctx):
        await command.radio_exit(ctx)

    @commands.command(help=lang['help-msg']['short-skip'].replace("#prefix#", option.prefix))
    @commands.check(check.is_public)
    async def s(self, ctx):
        await command.radio_skip(ctx)

    @commands.command(help=lang['help-msg']['short-now-play'].replace("#prefix#", option.prefix))
    @commands.check(check.is_public)
    async def np(self, ctx):
        await command.radio_now_play(ctx)

    @commands.command(help=lang['help-msg']['short-repeat'].replace("#prefix#", option.prefix))
    @commands.check(check.is_public)
    async def re(self, ctx):
        await command.radio_repeat(ctx)

    @commands.command(help=lang['help-msg']['short-play'].replace("#prefix#", option.prefix))
    @commands.check(check.is_public)
    async def p(self, ctx, query=None):
        if query is None:
            embed = discord.Embed(title=lang['title']['nothing-to-say'],
                                  description=f"```{lang['msg']['play-fail']}```",
                                  color=option.color.info)
            await ctx.send(embed=embed)
            return

        await command.radio_play(ctx, query)

    @commands.command(help=lang['help-msg']['short-search'].replace("#prefix#", option.prefix))
    @commands.check(check.is_public)
    async def sh(self, ctx, query=None):
        if query is None:
            embed = discord.Embed(title=lang['title']['nothing-to-say'],
                                  description=f"```{lang['msg']['find-fail']}```",
                                  color=option.color.info)
            await ctx.send(embed=embed)
            return

        await command.radio_search(ctx, query)
