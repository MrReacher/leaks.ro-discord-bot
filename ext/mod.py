import discord
from discord.ext import commands

import os, datetime
import re
import asyncio
import json
from datetime import timedelta

class TimeParser:
	def __init__(self, argument):
		compiled = re.compile(r"(?:(?P<hours>\d+)h)?(?:(?P<minutes>\d+)m)?(?:(?P<seconds>\d+)s)?")
		self.original = argument
		try:
			self.seconds = int(argument)
		except ValueError as e:
			match = compiled.match(argument)
			if match is None or not match.group(0):
				raise commands.BadArgument('Failed to parse time.') from e

			self.seconds = 0
			hours = match.group('hours')
			if hours is not None:
				self.seconds += int(hours) * 3600
			minutes = match.group('minutes')
			if minutes is not None:
				self.seconds += int(minutes) * 60
			seconds = match.group('seconds')
			if seconds is not None:
				self.seconds += int(seconds)

class Mod:

	def __init__(self, bot):
		self.bot = bot
		self.muted = {}
		self.cooldown = {}
		self.is_active = []

	@commands.command(pass_context=True, no_pm=True, aliases=['cc'])
	async def clear(self, ctx, limit: int=None):
		author = ctx.message.author
		server = ctx.message.server
		channel = ctx.message.channel
		comenzi = self.bot.get_channel("451296527084814348")

		if not ctx.message.channel == comenzi and not author.server_permissions.manage_messages: return await self.bot.say("Comenzile trebuie folosite doar în {0}.".format(comenzi.mention), delete_after=3)

		if limit is None: return await self.bot.say("Specifică câte mesaje vrei să ștergi.")
		if limit <= 0: return await self.bot.say("Nu este posibil să ștergi un număr `NULL` de mesaje.")
		if author.server_permissions.manage_messages:
			if server.get_member(self.bot.user.id).server_permissions.manage_messages:
				try:
					await self.bot.delete_message(ctx.message)
					purge = await self.bot.purge_from(channel, limit=limit)
					await self.bot.say("Au fost șterse **{}** mesaje.".format(len(purge)))
					await self.bot.send_message(self.bot.get_channel("451403088457236490"), "Au fost șterse **{}** mesaje în {} de către `{}#{}`.".format(len(purge), channel.mention, author.name, author.discriminator))
				except discord.HTTPException:
					await self.bot.say("Nu poți șterge mesajele mai vechi de 14 zile.")
				except discord.Forbidden:
					await self.bot.say("Nu am acces să șterg mesaje.")
				except Exception as e:
					print(e)
			else:
				await self.bot.say("Nu am acces să șterg mesaje.")
		else:
			await self.bot.say("Nu ai acces să folosești această comandă.")

	@commands.command(pass_context=True, no_pm=True)
	async def ban(self, ctx, member: discord.Member=None, *, reason: str=None):
		author = ctx.message.author
		server = ctx.message.server
		comenzi = self.bot.get_channel("451296527084814348")

		if not ctx.message.channel == comenzi and not author.server_permissions.ban_members: return await self.bot.say("Comenzile trebuie folosite doar în {0}.".format(comenzi.mention), delete_after=3)

		if member is None: return await self.bot.say("Menționați membrul pe care vreți să-l interziceți pe server.")
		if reason is None: return await self.bot.say("Un motiv trebuie specificat înainte de a interzice membrul de pe server.")
		if author.server_permissions.ban_members and author.top_role.position > member.top_role.position:
			if server.get_member(self.bot.user.id).server_permissions.ban_members and server.get_member(self.bot.user.id).top_role.position > member.top_role.position:
				try:
					await self.bot.send_message(member, "Ai fost interzis pe server-ul **{}** pentru```php\n{}```".format(server.name, reason))
					await self.bot.ban(member, delete_message_days=1)
				except discord.Forbidden:
					await self.bot.ban(member, delete_message_days=1)
				await self.bot.say("`{}#{}` a fost interzis permanent pe server de către `{}#{}` pentru **{}**.".format(member.name, member.discriminator, author.name, author.discriminator, reason))
				await self.bot.send_message(self.bot.get_channel("451403088457236490"), "`{}#{}` a fost interzis permanent pe server de către `{}#{}` pentru **{}**.".format(member.name, member.discriminator, author.name, author.discriminator, reason))
			else:
				return await self.bot.say("Nu poți interzice acest membru de pe server.")
		else:
			return await self.bot.say("Nu ai acces să folosești această comandă.")

	@commands.command(pass_context=True, no_pm=True)
	async def unban(self, ctx, member: str=None):
		author = ctx.message.author
		server = ctx.message.server
		comenzi = self.bot.get_channel("451296527084814348")

		if not ctx.message.channel == comenzi and not author.server_permissions.ban_members: return await self.bot.say("Comenzile trebuie folosite doar în {0}.".format(comenzi.mention), delete_after=3)

		if member is None: return await self.bot.say("Precizați membrul pe care vreți să-l eliminați din lista cu interziceri.")
		if not author.server_permissions.ban_members: return await self.bot.say("Nu ai acces să folosești această comandă.")
		banned_users = await self.bot.get_bans(server)
		matches = [user for user in banned_users if user.name.lower().startswith(member.lower())]
		if len(matches) != 1: return await self.bot.say("Membrul nu a fost găsit.")
		member = matches[0]
		try:
			await self.bot.unban(server, member)
			await self.bot.say("`{}` a fost eliminat din lista cu interziceri.".format(member.name))
			await self.bot.send_message(self.bot.get_channel("451403088457236490"), "`{}` a fost eliminat din lista cu interziceri de către `{}#{}`.".format(member.name, author.name, author.discriminator))
		except discord.Forbidden:
			return await self.bot.say("Nu am acces pentru a elimina membrul din lista cu interziceri.")

	@commands.command(pass_context=True, no_pm=True)
	async def mute(self, ctx, member: discord.Member=None, time: TimeParser=None, *, reason: str=None):
		author = ctx.message.author
		server = ctx.message.server
		comenzi = self.bot.get_channel("451296527084814348")

		if not ctx.message.channel == comenzi and not author.server_permissions.manage_messages: return await self.bot.say("Comenzile trebuie folosite doar în {0}.".format(comenzi.mention), delete_after=3)

		if member is None: return await self.bot.say("Menționați membrul pe care vreți să-l aduceți la tăcere.")
		if time is None: return await self.bot.say("Timpul trebuie specificat. Exemple:```php\nmute [membru] 10m / mute [membru] 2h```")
		if reason is None:
			reason = "motiv nespecificat"

		if time.seconds > 7200: return await self.bot.say("Timpul specificat nu trebuie să depășească 7200 de secunde. (2 ore)")
		if not author.server_permissions.manage_messages: return await self.bot.say("Nu ai acces să folosești această comandă.")

		muted_role = discord.utils.get(server.roles, name="Muted")

		if not author.top_role.position > member.top_role.position: return await self.bot.say("Acest membru nu poate fi adus la tăcere.")
		if muted_role in member.roles: return await self.bot.say("Acest membru a fost deja adus la tacere.")
		await self.bot.add_roles(member, muted_role)
		await self.bot.say("`{}#{}` a fost adus la tăcere de către `{}#{}` pentru {} secunde.".format(member.name, member.discriminator, author.name, author.discriminator, time.seconds))
		await self.bot.send_message(self.bot.get_channel("451403088457236490"), "`{}#{}` a fost adus la tăcere de către `{}#{}` pentru {} secunde. ({})".format(member.name, member.discriminator, author.name, author.discriminator, time.seconds, reason))
		self.muted[member.id] = "true"
		await asyncio.sleep(time.seconds)
		if self.muted:
			if self.muted[member.id] == "true":
				print(self.muted)
				await self.bot.remove_roles(member, muted_role)
				del self.muted[member.id]

	@commands.command(pass_context=True, no_pm=True)
	async def unmute(self, ctx, member: discord.Member=None, *, reason: str=None):
		author = ctx.message.author
		server = ctx.message.server
		comenzi = self.bot.get_channel("451296527084814348")

		if not ctx.message.channel == comenzi and not author.server_permissions.manage_messages: return await self.bot.say("Comenzile trebuie folosite doar în {0}.".format(comenzi.mention), delete_after=3)

		if member is None: return await self.bot.say("Menționați membrul pe care vreți să-l eliberați de la tăcere.")
		if reason is None:
			reason = "motiv nespecificat"

		if not author.server_permissions.manage_messages: return await self.bot.say("Nu ai acces să folosești această comandă.")

		muted_role = discord.utils.get(server.roles, name="Muted")
		if not muted_role in member.roles: return await self.bot.say("Acest membru nu a fost adus la tăcere.")
		if self.muted:
			if self.muted[member.id] == "true":
				await self.bot.remove_roles(member, muted_role)
				del self.muted[member.id]
				await self.bot.say("Acest membru a fost eliberat de la tăcere.")
				await self.bot.send_message(self.bot.get_channel("451403088457236490"), "`{}#{}` a fost eliberat de la tăcere de către `{}#{}`. ({})".format(member.name, member.discriminator, author.name, author.discriminator, reason))

	@commands.command(pass_context=True)
	async def say(self, ctx, *, message: str=None):
		author = ctx.message.author
		comenzi = self.bot.get_channel("451296527084814348")

		if not ctx.message.channel == comenzi and not author.server_permissions.administrator: return await self.bot.say("Comenzile trebuie folosite doar în {0}.".format(comenzi.mention), delete_after=3)

		if not author.server_permissions.administrator: return await self.bot.say("Nu ai acces să folosești această comandă.")
		await self.bot.delete_message(ctx.message)
		await self.bot.say(message)

	async def on_message(self, message):
		if message.author.bot: return
		server = self.bot.get_server("451066437789024256")

		async def detect_advertising(message):
			if "discord.gg/" in message.content:
				invite_list = []
				invites = await self.bot.invites_from(server)
				for invite in invites:
					invite_list.append(invite.code)
				if [invite for invite in invite_list if "discord.gg/{}".format(invite) in message.content]: return
				try:
					await self.bot.ban(server.get_member(message.author.id), delete_message_days=1)
					await self.bot.send_message(server.get_channel("451066437789024258"), "**AUTOMATIC** - a fost detectată reclamă, `{}#{}` a fost interzis permanent de pe server.".format(message.author.name, message.author.discriminator))
				except:
					pass

		if message.server is None:
			return await detect_advertising(message)

		if message.author.server_permissions.administrator: return
		await detect_advertising(message)

		async def check(message):
			mess = []
			async for message in self.bot.logs_from(message.channel, limit=5, reverse=True):
				if message.author.server_permissions.administrator: pass
				mess.append(int(message.timestamp.strftime("%s")))

			diff = mess[-1] - mess[0]
			if diff < 4.5:
				return True
			else:
				if len(self.is_active) != 0:
					self.is_active.remove('active')
				return False

		async def del_mess(message):
			try:
				await self.bot.delete_message(message)
			except:
				pass

		check = await check(message)
		if check:
			if not self.is_active:
				active = await self.bot.send_message(message.channel, "**AUTOMATIC** - a fost detectat spam, chat-ul este **ÎNCETINIT**.")
				self.is_active.append('active')
			if message.author.id in self.cooldown:
				if self.cooldown[message.author.id] + timedelta(seconds=5) < message.timestamp:
					del self.cooldown[message.author.id]
				else:
					await del_mess(message)
			else:
				await del_mess(message)
				self.cooldown[message.author.id] = message.timestamp


def setup(bot):
	bot.add_cog(Mod(bot))