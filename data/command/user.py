# -*- coding: utf-8 -*-

import logging

import discord
from discord.ext import commands

from data.lib import invite

logger = logging.getLogger()


def is_public(ctx):
    return not isinstance(ctx.message.channel, discord.abc.PrivateChannel)


class Commands(commands.Cog, name="User Command"):
    @commands.command(help="Get Invitation Link")
    @commands.check(is_public)
    async def invite(self, ctx):
        embed = discord.Embed(title="Invite Me!", color=16579836,
                              description="Please Click me!",
                              url=invite.get_link(ctx.bot))
        try:
            await ctx.author.send(embed=embed)
        except discord.errors.Forbidden:
            pass
