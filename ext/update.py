import discord
from discord.ext import commands

import os, datetime
import re
import asyncio

class Update:

	def __init__(self, bot):
		self.bot = bot

	async def on_member_update(self, before, after):
			#Not a game update, skip it
			if before.game is None and after.game is None:
				return

			role = discord.utils.get(after.server.roles, name="Advertising Squad")
			is_leaksro = lambda g: g.name == "leaks.ro"
			update_member = lambda m: after.server.get_member(m.id)

			async def add(member):
				if role not in member.roles:
					await self.bot.add_roles(member, role)

			async def remove(member):
				if role in member.roles:
					await self.bot.remove_roles(member, role)

			if role is None:
				return print('advertising squad role was not found.')

			if before.game is None and after.game is not None:
				#start playing
				if is_leaksro(after.game):
					await add(after)

			elif before.game is not None and after.game is not None:
				if is_leaksro(after.game):
					await add(after)
				if not is_leaksro(after.game):
					await remove(after)

			elif before.game is not None and after.game is None:
				#stopped playing
				await asyncio.sleep(10)
				if is_leaksro(before.game):
					member = update_member(after)

					if member.game is None:
						await remove(after)

			elif before.game is not after.game:
				#switched game
				if is_leaksro(before.game):
					#idk if we should `update_member` here as well...
					pass
				elif is_leaksro(after.game):
					await add(after)

def setup(bot):
	bot.add_cog(Update(bot))