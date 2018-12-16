import discord
from discord.ext import commands

import os, datetime
import re
import asyncio
import aiohttp
import json
import feedparser
import time

class Roles:

	def __init__(self, bot):
		self.bot = bot
		self.loop = bot.loop
		self._leaks = {}
		self._it = {}
		self._web = {}
		self._samp = {}
		self.loop.create_task(self.feedparser())

	async def feedparser(self):
		await self.bot.wait_until_ready()
		channel = self.bot.get_channel("452115433164767233")
		server = self.bot.get_server("451066437789024256")
		leaks_role = discord.utils.get(server.roles, id="452114719390564362")
		it_role = discord.utils.get(server.roles, id="452115033686671360")
		web_role = discord.utils.get(server.roles, id="452115127936745472")
		samp_role = discord.utils.get(server.roles, id="452409982206345216")
		print("\033[1;90m[{time}]\033[1;37m [FEED] fetching information, please wait..".format(time=time.strftime("%H:%M:%S")))
		while 1:
			if self._samp:
				async with aiohttp.ClientSession() as ses:
					async with ses.get("http://tm5qwtee.leaks.ro/index.php?/rss/forums/6-samp-rss/") as url:
						samp_to_parse = await url.text()
				modified_samp = feedparser.parse(samp_to_parse)
				if not self._samp['last_modified'] != datetime.datetime.strptime(modified_samp.feed.published, "%a, %d %b %Y %H:%M:%S %z").replace(tzinfo=None):
					await asyncio.sleep(1)
				else:
					await self.bot.edit_role(server, samp_role, mentionable=True)
					await self.bot.send_message(channel, "{1.mention} ➜ **{0.title}**\n{0.link}".format(modified_samp.entries[0], samp_role))
					await self.bot.edit_role(server, samp_role, mentionable=False)
					del self._samp['last_modified']
					print("\033[1;90m[{time}]\033[1;37m [SAMP] message sent".format(time=time.strftime("%H:%M:%S")))
			else:
				async with aiohttp.ClientSession() as ses:
					async with ses.get("http://tm5qwtee.leaks.ro/index.php?/rss/forums/6-samp-rss/") as url:
						samp_to_parse = await url.text()
				feed_samp = feedparser.parse(samp_to_parse)
				self._samp['last_modified'] = datetime.datetime.strptime(feed_samp.feed.published, "%a, %d %b %Y %H:%M:%S %z").replace(tzinfo=None)
				print("\033[1;90m[{time}]\033[1;37m [SAMP] content parsed".format(time=time.strftime("%H:%M:%S")))

			if self._leaks:
				async with aiohttp.ClientSession() as ses:
					async with ses.get("http://tm5qwtee.leaks.ro/index.php?/rss/forums/3-leaks-rss/") as url:
						leaks_to_parse = await url.text()
				modified_leaks = feedparser.parse(leaks_to_parse)
				if not self._leaks['last_modified'] != datetime.datetime.strptime(modified_leaks.feed.published, "%a, %d %b %Y %H:%M:%S %z").replace(tzinfo=None):
					await asyncio.sleep(1)
				else:
					await self.bot.edit_role(server, leaks_role, mentionable=True)
					await self.bot.send_message(channel, "{1.mention} ➜ **{0.title}**\n{0.link}".format(modified_leaks.entries[0], leaks_role))
					await self.bot.edit_role(server, leaks_role, mentionable=False)
					del self._leaks['last_modified']
					print("\033[1;90m[{time}]\033[1;37m [LEAKS] message sent".format(time=time.strftime("%H:%M:%S")))
			else:
				async with aiohttp.ClientSession() as ses:
					async with ses.get("http://tm5qwtee.leaks.ro/index.php?/rss/forums/3-leaks-rss/") as url:
						leaks_to_parse = await url.text()
				feed_leaks = feedparser.parse(leaks_to_parse)
				self._leaks['last_modified'] = datetime.datetime.strptime(feed_leaks.feed.published, "%a, %d %b %Y %H:%M:%S %z").replace(tzinfo=None)
				print("\033[1;90m[{time}]\033[1;37m [LEAKS] content parsed".format(time=time.strftime("%H:%M:%S")))

			if self._it:
				async with aiohttp.ClientSession() as ses:
					async with ses.get("http://tm5qwtee.leaks.ro/index.php?/rss/forums/4-it-rss/") as url:
						it_to_parse = await url.text()
				modified_it = feedparser.parse(it_to_parse)
				if not self._it['last_modified'] != datetime.datetime.strptime(modified_it.feed.published, "%a, %d %b %Y %H:%M:%S %z").replace(tzinfo=None):
					await asyncio.sleep(1)
				else:
					await self.bot.edit_role(server, it_role, mentionable=True)
					await self.bot.send_message(channel, "{1.mention} ➜ **{0.title}**\n{0.link}".format(modified_it.entries[0], it_role))
					await self.bot.edit_role(server, it_role, mentionable=False)
					del self._it['last_modified']
					print("\033[1;90m[{time}]\033[1;37m [IT] message sent".format(time=time.strftime("%H:%M:%S")))
			else:
				async with aiohttp.ClientSession() as ses:
					async with ses.get("http://tm5qwtee.leaks.ro/index.php?/rss/forums/4-it-rss/") as url:
						it_to_parse = await url.text()
				feed_it = feedparser.parse(it_to_parse)
				self._it['last_modified'] = datetime.datetime.strptime(feed_it.feed.published, "%a, %d %b %Y %H:%M:%S %z").replace(tzinfo=None)
				print("\033[1;90m[{time}]\033[1;37m [IT] content parsed".format(time=time.strftime("%H:%M:%S")))

			if self._web:
				async with aiohttp.ClientSession() as ses:
					async with ses.get("http://tm5qwtee.leaks.ro/index.php?/rss/forums/5-web-rss/") as url:
						web_to_parse = await url.text()
				modified_web = feedparser.parse(web_to_parse)
				if not self._web['last_modified'] != datetime.datetime.strptime(modified_web.feed.published, "%a, %d %b %Y %H:%M:%S %z").replace(tzinfo=None):
					await asyncio.sleep(1)
				else:
					await self.bot.edit_role(server, web_role, mentionable=True)
					await self.bot.send_message(channel, "{1.mention} ➜ **{0.title}**\n{0.link}".format(modified_web.entries[0], web_role))
					await self.bot.edit_role(server, web_role, mentionable=False)
					del self._web['last_modified']
					print("\033[1;90m[{time}]\033[1;37m [WEB] message sent".format(time=time.strftime("%H:%M:%S")))
			else:
				async with aiohttp.ClientSession() as ses:
					async with ses.get("http://tm5qwtee.leaks.ro/index.php?/rss/forums/5-web-rss/") as url:
						web_to_parse = await url.text()
				feed_web = feedparser.parse(web_to_parse)
				self._web['last_modified'] = datetime.datetime.strptime(feed_web.feed.published, "%a, %d %b %Y %H:%M:%S %z").replace(tzinfo=None)
				print("\033[1;90m[{time}]\033[1;37m [WEB] content parsed".format(time=time.strftime("%H:%M:%S")))

			#add try catch for errors when requests ain't working (None.feed.published)

			print("\033[1;90m[{time}]\033[1;37m [ALL] categories have been refreshed".format(time=time.strftime("%H:%M:%S")))
			await asyncio.sleep(120)

	@commands.group(pass_context=True)
	async def subscribe(self, ctx):
		if ctx.invoked_subcommand is None:
			return await self.bot.say("Categorii disponibile: `samp`, `leaks`, `it`, `web`.\nPentru a te abona la o categorie, foloseste comanda: `/subscribe <categorie>`.")

	@subscribe.command(pass_context=True)
	async def samp(self, ctx):
		role = discord.utils.get(ctx.message.server.roles, id="452409982206345216")
		if not role in ctx.message.author.roles:
			await self.bot.add_roles(ctx.message.author, role)
			await self.bot.say("Ți-a fost adăugat gradul de `SA:MP`. Acum vei primi notificări atunci când se postează ceva nou.")
		else:
			await self.bot.remove_roles(ctx.message.author, role)
			await self.bot.say("Ți-a fost scos gradul de `SA:MP`.")

	@subscribe.command(pass_context=True)
	async def leaks(self, ctx):
		role = discord.utils.get(ctx.message.server.roles, id="452114719390564362")
		if not role in ctx.message.author.roles:
			await self.bot.add_roles(ctx.message.author, role)
			await self.bot.say("Ți-a fost adăugat gradul de `LEAKS`. Acum vei primi notificări atunci când se postează ceva nou.")
		else:
			await self.bot.remove_roles(ctx.message.author, role)
			await self.bot.say("Ți-a fost scos gradul de `LEAKS`.")

	@subscribe.command(pass_context=True)
	async def it(self, ctx):
		role = discord.utils.get(ctx.message.server.roles, id="452115033686671360")
		if not role in ctx.message.author.roles:
			await self.bot.add_roles(ctx.message.author, role)
			await self.bot.say("Ți-a fost adăugat gradul de `IT`. Acum vei primi notificări atunci când se postează ceva nou.")
		else:
			await self.bot.remove_roles(ctx.message.author, role)
			await self.bot.say("Ți-a fost scos gradul de `IT`.")

	@subscribe.command(pass_context=True)
	async def web(self, ctx):
		role = discord.utils.get(ctx.message.server.roles, id="452115127936745472")
		if not role in ctx.message.author.roles:
			await self.bot.add_roles(ctx.message.author, role)
			await self.bot.say("Ți-a fost adăugat gradul de `WEB`. Acum vei primi notificări atunci când se postează ceva nou.")
		else:
			await self.bot.remove_roles(ctx.message.author, role)
			await self.bot.say("Ți-a fost scos gradul de `WEB`.")

	@commands.command(pass_context=True)
	async def nsfw(self, ctx):
		role = discord.utils.get(ctx.message.server.roles, id="451079198627594240")
		if not role in ctx.message.author.roles:
			await self.bot.add_roles(ctx.message.author, role)
			await self.bot.say("Ți-a fost adăugat gradul de `NSFW`.")
		else:
			await self.bot.remove_roles(ctx.message.author, role)
			await self.bot.say("Ți-a fost scos gradul de `NSFW`.")

def setup(bot):
	bot.add_cog(Roles(bot))
