# -*- coding: utf-8 -*-

import discord


def is_public(ctx):
    return not isinstance(ctx.message.channel, discord.abc.PrivateChannel)
