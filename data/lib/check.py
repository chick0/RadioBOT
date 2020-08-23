# -*- coding: utf-8 -*-

import discord


def is_public(ctx):
    return not isinstance(ctx.message.channel, discord.abc.PrivateChannel)


def is_join(ctx):
    vcs = ctx.bot.voice_clients
    for t_vc in vcs:
        if t_vc.guild.id is ctx.message.guild.id:
            if ctx.message.author in t_vc.channel.members:
                return True
    return False
