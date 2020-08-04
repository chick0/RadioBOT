# -*- coding: utf-8 -*-

import os
import hashlib
import logging

import discord
from discord.ext import commands

import option
from data.lib import check, language, music, playlist

from data.lib.core import radioDict

lang = language.get_data()
logger = logging.getLogger()


class RadioOwner(commands.Cog, name=f"Radio - {lang['help-msg']['type-admin']}"):
    @commands.command(help=lang['help-msg']['admin-close'])
    @commands.check(check.is_public)
    async def close(self, ctx):
        if await ctx.bot.is_owner(user=ctx.author):
            await ctx.send(lang['msg']['shutdown-bot'])
            if len(ctx.bot.voice_clients) > 0:
                await self.leave_all(ctx)
            await ctx.bot.close()
        else:
            logger.warning(f"[{ctx.author.id}]{ctx.author} try to use owner command")

    @commands.command(help=lang['help-msg']['admin-leave-all'])
    @commands.check(check.is_public)
    async def leave_all(self, ctx):
        if await ctx.bot.is_owner(user=ctx.author):
            await ctx.send(lang['msg']['turn-off-all'])

            clients = ctx.bot.voice_clients
            for client in clients:
                await radioDict[ctx.guild.id].get_ctx().send(f"{lang['msg']['shutdown-by-admin']}")
                await client.disconnect()
        else:
            logger.warning(f"[{ctx.author.id}]{ctx.author} try to use owner command")

    @commands.command(help=lang['help-msg']['admin-reload-playlist'])
    @commands.check(check.is_public)
    async def reload(self, ctx):
        if await ctx.bot.is_owner(user=ctx.author):
            if len(ctx.bot.voice_clients) > 0:
                await self.leave_all(ctx)

            playlist.get_playlist()
            await ctx.send(f"{lang['msg']['complete-reload-playlist']}")
        else:
            logger.warning(f"[{ctx.author.id}]{ctx.author} try to use owner command")

    @commands.command(help=lang['help-msg']['upload'])
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.guild)
    @commands.check(check.is_public)
    async def upload(self, ctx):
        if await ctx.bot.is_owner(user=ctx.author):
            if len(ctx.message.attachments) == 0:
                embed = discord.Embed(title=lang['title']['upload-cancel'],
                                      description=f"```{lang['msg']['upload-cancel-no-upload']}```",
                                      color=option.color.info)
                await ctx.send(embed=embed)
                return

            try:
                logger.info("Testing User Upload Directory")
                with open("./data/user_upload/test", "w") as upload_directory_test:
                    upload_directory_test.write("Hello, World")
                    logger.info("OK! - Upload Directory Alive")
            except FileNotFoundError:
                logger.info("FAIL - Try to create User Upload Directory")
                try:
                    os.mkdir("./data/user_upload")
                    logger.info("OK! - Upload Directory is Online")
                except PermissionError:
                    logger.info("FAIL - Cancel Upload event")
                    embed = discord.Embed(title=lang['title']['upload-cancel'],
                                          description=f"```{lang['msg']['upload-cancel-directory']}```",
                                          color=option.color.warn)
                    await ctx.send(embed=embed)
                    return

            for item in ctx.message.attachments:
                extension = item.filename.split(".")[-1]
                hash_result = hashlib.sha1(item.filename.encode()).hexdigest()

                file_name = f"{ctx.author.id}_{hash_result}.{extension}"
                await item.save(fp=os.fspath(f"./data/user_upload/{file_name}"))

                data = music.get_data(f"./data/user_upload/{file_name}")
                if data is not None:
                    embed = discord.Embed(title=lang['title']['upload-complete'],
                                          color=option.color.normal)
                    embed.add_field(name=lang['title']['upload-result-info'],
                                    value=f"{data['artist']} - {data['title']}", inline=False)
                    embed.add_field(name=lang['title']['upload-result-name'],
                                    value=f"{file_name}", inline=False)
                    await ctx.send(embed=embed)
                    playlist.get_playlist()
                else:
                    embed = discord.Embed(title=lang['title']['upload-cancel'],
                                          description=f"```{lang['msg']['upload-cancel-fail']}```",
                                          color=option.color.info)
                    await ctx.send(embed=embed)
                    os.remove(f"./data/user_upload/{file_name}")
        else:
            logger.warning(f"[{ctx.author.id}]{ctx.author} try to use owner command")
