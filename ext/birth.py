import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

import os, datetime
import re
import asyncio
import sqlite3

async def sqlite():
	with sqlite3.connect('birthdays.db') as conn:
		c = conn.cursor()
		c.execute("""
			CREATE TABLE IF NOT EXISTS `birth` (
			`userid`	INTEGER,
			`date`	TEXT,
			`year`	INTEGER
		)""")

class Birthday:

	def __init__(self, bot):
		self.bot = bot
		asyncio.get_event_loop().create_task(sqlite())

	@commands.cooldown(1, 3, BucketType.user)
	@commands.group(pass_context=True)
	async def birthday(self, ctx):
		if ctx.invoked_subcommand is None:
			return

	@birthday.command(pass_context=True)
	async def add(self, ctx, member: discord.Member, date: str, year: int):
		if not ctx.message.author.id == "443476962871214090": return
		with sqlite3.connect('birthdays.db') as conn:
			c = conn.cursor()
			c.execute("SELECT * FROM birth WHERE userid == {0}".format(member.id))
			response = c.fetchall()
			if response: return await self.bot.say("Acest membru este deja înregistrat în baza de date.")
			await self.bot.say(":ok_hand:")
			c.execute("INSERT INTO birth(`userid`, `date`, `year`) VALUES ('{0}', '{1}', '{2}')".format(member.id, date, year))
			conn.commit()

	@birthday.command(pass_context=True)
	async def remove(self, ctx, id: str):
		if not ctx.message.author.id == "443476962871214090": return
		with sqlite3.connect('birthdays.db') as conn:
			c = conn.cursor()
			c.execute("SELECT * FROM birth WHERE userid == {0}".format(id))
			response = c.fetchall()
			if not response: return await self.bot.say("Acest membru nu este înregistrat în baza de date.")
			await self.bot.say(":ok_hand:")
			c.execute("DELETE FROM birth WHERE userid == {0}".format(id))
			conn.commit()

	@birthday.command(pass_context=True)
	async def list(self, ctx):
		with sqlite3.connect('birthdays.db') as conn:
			c = conn.cursor()
			c.execute("SELECT * FROM birth WHERE date == '{0}'".format(datetime.datetime.now().strftime("%m-%d")))
			response = c.fetchall()
			c.execute("SELECT * FROM birth WHERE date BETWEEN '{0}' AND '{1}'".format(datetime.datetime.now().strftime("%m-%d"), (datetime.datetime.now() + datetime.timedelta(days=7)).strftime("%m-%d")))
			response2 = c.fetchall()
			
			if not response: response = []
			
			#this returns dates
			#example - ['06-21']
			rows = [x[1] for x in response]
			
			#comparing dates
			#example - 06-21 with 06-21
			if rows:
				compare = rows[0] == datetime.datetime.now().strftime("%m-%d")
			else:
				compare = False
			
			#if someone has birth today - true
			#if not - false
			compare_turned = False
			if compare:
				#we return the member id
				compare = [x[0] for x in response][0]
			
				#member turned x years old
				c.execute("SELECT * FROM birth WHERE userid == {0}".format(compare))
				member_turned = c.fetchall()
				rows_turned = [x[2] for x in member_turned][0]
				compare_turned = int(datetime.datetime.now().strftime("%Y")) - int(rows_turned)
			
			#for the next 7 days we do not need their YEAR information in order to print what they turn into
			#so we need to print the dates, like 06-22 and so on

			if not response2: response2 = None
			if response2 is not None:
				rows2 = dict([(str(discord.utils.get(self.bot.get_all_members(), id=str(x[0]))), str(x[1])) for x in response2])
				margin = max(len(key) for key in rows2)
				body = []
				for key, value in rows2.items():
					body.append(("{:<%d} | {}" % margin).format(key, value))
				members = "\n".join(body)

			else:
				members = "----"

			c.execute("SELECT * FROM birth")
			total = c.fetchall()
			member = discord.utils.get(self.bot.get_all_members(), id=str(compare))

			await self.bot.say("{0}\nZile de naștere în următoarele 7 zile:```apache\n{1}```\nAu fost înregistrate `{2}` zile de naştere.".format("Astăzi, `{0}` a împlinit vârsta de `{1}` ani.".format(member, compare_turned) if member is not None else "Astăzi nu se sărbătorește nicio zi de naștere.", members, len(total))) 

def setup(bot):
	bot.add_cog(Birthday(bot))
