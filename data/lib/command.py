# -*- coding: utf-8 -*-

import json
import logging

import discord

import option
from data.lib import core

logger = logging.getLogger()

# cache loader
p_list = json.load(open("data/cache__playlist.json", "r"))
lang = json.load(open("data/cache__language.json", "r"))


async def radio_join(ctx):
    try:
        voice_client = await ctx.author.voice.channel.connect()
        logger.info(f"Radio Connected at {ctx.guild.id}")
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

    core.radioDict[ctx.guild.id] = core.Radio(ctx, voice_client)
    core.radioDict[ctx.guild.id].play_radio()


async def radio_exit(ctx):
    try:
        await ctx.guild.voice_client.disconnect()
        await ctx.send(":wave:")
    except AttributeError:
        logger.error(f"No radioWorker at {ctx.guild.id}")
        embed = discord.Embed(title=lang['title']['nothing-to-say'],
                              description=f"```{lang['msg']['radio-dead']}```",
                              color=option.color.info)
        await ctx.send(embed=embed)
    return


async def radio_skip(ctx):
    try:
        stat = core.radioDict[ctx.guild.id].get_stat()
        if stat[0] == 2:
            embed = discord.Embed(title=lang['title']['cant-use'],
                                  description=f"```{lang['msg']['repeat-on']}```",
                                  color=option.color.warn)
            await ctx.send(embed=embed)
        else:
            await ctx.guild.voice_client.stop()
    except AttributeError:
        logger.error(f"No radioWorker at {ctx.guild.id}")
        embed = discord.Embed(title=lang['title']['nothing-to-say'],
                              description=f"```{lang['msg']['radio-dead']}```",
                              color=option.color.info)
        await ctx.send(embed=embed)
    return


async def radio_now_play(ctx):
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
        await core.radioDict[ctx.guild.id].send_play(ctx)
    except KeyError:
        logger.error(f"No radioWorker at {ctx.guild.id}")
        embed = discord.Embed(title=lang['title']['nothing-to-say'],
                              description=f"```{lang['msg']['radio-dead']}```",
                              color=option.color.info)
        await ctx.channel.send(embed=embed)
    return


async def radio_repeat(ctx):
    try:
        stat = core.radioDict[ctx.guild.id].get_stat()

        mode_msg = lang['msg']['set-mode-normal']
        if stat[0] == 2:
            mode_msg = lang['msg']['set-mode-repeat']
            core.radioDict[ctx.guild.id].set_stat(0, 0)
        elif stat[0] != 2:
            core.radioDict[ctx.guild.id].set_stat(2, 0)

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

        core.radioDict[ctx.guild.id].set_stat(1, play_next)
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
