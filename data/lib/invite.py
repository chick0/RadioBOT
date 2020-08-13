# -*- coding: utf-8 -*-

from option import default_permission


def get_link(bot, permission=default_permission):
    return f"https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions={permission}&scope=bot"
