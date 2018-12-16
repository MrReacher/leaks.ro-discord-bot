import discord
from discord.ext import commands

import os, time
import datetime
import re
import asyncio
import sqlite3

async def sqlite():
	with sqlite3.connect('marry.db') as conn:
		c = conn.cursor()
		c.execute("""
			CREATE TABLE IF NOT EXISTS `users` (
			`userid`	INTEGER,
			`gender`	TEXT
		)""")
		c.execute("""
			CREATE TABLE IF NOT EXISTS `status` (
			`userid1`	INTEGER,
			`userid2`	INTEGER,
			`time`	INTEGER
		)""")

class Marry:

	def __init__(self, bot):
		self.bot = bot
		asyncio.get_event_loop().create_task(sqlite())

	@commands.group(pass_context=True, no_pm=True)
	async def marry(self, ctx):
		if ctx.invoked_subcommand is None:
			return await self.bot.say("Comenzi disponibile: ```apache\n/marry propose, /marry divorce, /marry setgender, /marry check```")

	@marry.command(pass_context=True, no_pm=True)
	async def propose(self, ctx, target: discord.Member=None):
		if target is None: return await self.bot.say("Trebuie să specifici persoana cu care vrei să te căsătorești.")
		if target.bot: return await self.bot.say("Înțeleg că ești trist, dar nu te poți căsători cu un bot.")
		if ctx.message.author == target: return await self.bot.say("Nu te poți căsători cu tine însuți.")
		role = discord.utils.get(ctx.message.server.roles, id="453258213874466816")
		with sqlite3.connect('marry.db') as conn:
			c = conn.cursor()
			c.execute("SELECT * FROM users WHERE userid == {0}".format(ctx.message.author.id))
			response = c.fetchall()
			if not response: return await self.bot.say("Va trebui să-ți precizezi sexul înainte de a te căsători. Te rog folosește comanda `/marry setgender <bărbat>|<femeie>`.")
			c.execute("SELECT * FROM users WHERE userid == {0}".format(target.id))
			member_response = c.fetchall()
			if not member_response: return await self.bot.say("Persoana precizată nu și-a setat încă sexul. Spune-i să folosească comanda `/marry setgender <bărbat>|<femeie>`.")
			if response[0][1] == member_response[0][1]: return await self.bot.say("Nu te poti casatori cu o persoana de acelasi sex.")
			c.execute("SELECT * FROM status WHERE userid1 == {0} OR userid2 == {0}".format(ctx.message.author.id))
			check_if_married = c.fetchall()
			if check_if_married: return await self.bot.say("Ești deja căsătorit cu {0.mention}. Pentru a te căsători cu altă persoană va trebui să divorțezi de cea actuală. Acest act este posibil folosind comanda `/marry divorce`.".format(ctx.message.server.get_member(str(check_if_married[0][1]) if not ctx.message.author.id != str(check_if_married[0][0]) else str(check_if_married[0][0]))))
			c.execute("SELECT * FROM status WHERE userid1 == {0} OR userid2 == {0}".format(target.id))
			check_if_person_married = c.fetchall()
			if check_if_person_married: return await self.bot.say("Persoana precizată este deja căsătorită. Folosește `/marry check @{0}` pentru a verifica cu cine este căsătorit.".format(target.name))
			await self.bot.say("{0}, {1} te-a cerut în căsătorie. Pentru a accepta oferta, te rog răspunde cu `da`, iar pentru a refuza, răspunde cu `nu`.".format(target.mention, ctx.message.author.mention))
			waiting = await self.bot.wait_for_message(timeout=30, author=target, check=lambda m: m.content.lower() in ['da', 'nu'])
			if waiting is None: return await self.bot.say("Cererea în căsătorie pentru {0} a expirat.".format(target.mention))
			if waiting.content.lower() != "da": return await self.bot.say("Cererea de căsătorie a fost refuzată. Poate vei avea mai mult noroc data viitoare.")
			time_when = datetime.datetime.now()
			await self.bot.say("{0} și {1} tocmai s-au căsătorit. :heart:\nRelația lor a început astăzi, `{2}`.".format(ctx.message.author.mention, target.mention, time_when.strftime("%d-%m-%Y %H:%M:%S")))
			for member in [ctx.message.author, target]:
				try:
					await self.bot.add_roles(member, role)
				except:
					continue
			c.execute("INSERT INTO status(`userid1`, `userid2`, `time`) VALUES ('{0}', '{1}', '{2}')".format(ctx.message.author.id, target.id, time_when.strftime("%s")))
			conn.commit()

	@marry.command(pass_context=True)
	async def divorce(self, ctx):
		role = discord.utils.get(ctx.message.server.roles, id="453258213874466816")
		with sqlite3.connect('marry.db') as conn:
			c = conn.cursor()
			c.execute("SELECT * FROM status WHERE userid1 == {0} OR userid2 == {0}".format(ctx.message.author.id))
			response = c.fetchall()
			if not response: return await self.bot.say("Nu eşti căsătorit.")
			for member in [ctx.message.server.get_member(str(response[0][0])), ctx.message.server.get_member(str(response[0][1]))]:
				try:
					await self.bot.remove_roles(member, role)
				except:
					continue
			c.execute("DELETE FROM status WHERE userid1 == {0} OR userid2 == {0}".format(ctx.message.author.id))
			time_now = int(datetime.datetime.now().strftime("%s"))
			time_final = time_now - response[0][2]
			time_days_final = (time_now - response[0][2]) / 60 / 60 / 24
			try:
				await self.bot.say("{1} și {0.mention} tocmai au divorțat. :broken_heart:\nRelația lor a durat {2:.0f} zile. (`{3}`)".format(ctx.message.server.get_member(str(response[0][1]) if not ctx.message.author.id != str(response[0][0]) else str(response[0][0])), ctx.message.author.mention, time_days_final, datetime.datetime.fromtimestamp(response[0][2]).strftime("%d-%m-%Y %H:%M:%S")))
			except:
				await self.bot.say("{0.mention}, tocmai ai divorțat. :broken_heart:\nRelația ta a durat {1:.0f} zile. (`{2}`)".format(ctx.message.author, time_days_final, datetime.datetime.fromtimestamp(response[0][2]).strftime("%d-%m-%Y %H:%M:%S")))
			conn.commit()

	@marry.command(pass_context=True, no_pm=True)
	async def setgender(self, ctx, option: str=None):
		
		options = ["barbat", "bărbat", "femeie"]
		if option is None: return await self.bot.say("Sexul nu a fost specificat. Momentan sunt acceptate următoarele sexe: `bărbat`, `femeie`.")
		if not option.lower() in options: return await self.bot.say("Acest sex nu poate fi regăsit în opțiunile acceptate.")
		with sqlite3.connect('marry.db') as conn:
			c = conn.cursor()
			c.execute("SELECT * FROM users WHERE userid == {0}".format(ctx.message.author.id))
			response = c.fetchall()

			if option == "barbat":
				if response:
					if response[0][1] == "barbat" or response[0][1] == "bărbat": return await self.bot.say("Ți-ai ales deja sexul a fi `barbat`.")
					c.execute("UPDATE users SET gender = 'barbat' WHERE userid == {0}".format(ctx.message.author.id))
					await self.bot.say("Ți-ai schimbat sexul in `barbat`.")
				else:
					c.execute("INSERT INTO users(`userid`,`gender`) VALUES ('{0}', 'barbat')".format(ctx.message.author.id))
					await self.bot.say("Ți-ai atribuit sexul de `barbat` cu succes.")
			if option == "femeie":
				if response:
					if response[0][1] == "femeie": return await self.bot.say("Ți-ai ales deja sexul a fi `femeie`.")
					c.execute("UPDATE users SET gender = 'femeie' WHERE userid == {0}".format(ctx.message.author.id))
					await self.bot.say("Ți-ai schimbat sexul in `femeie`.")
				else:
					c.execute("INSERT INTO users(`userid`,`gender`) VALUES ('{0}', 'femeie')".format(ctx.message.author.id))
					await self.bot.say("Ți-ai atribuit sexul de `femeie` cu succes.")
			conn.commit()

	@marry.command(pass_context=True, no_pm=True)
	async def check(self, ctx, target: discord.Member=None):
		if target is None:
			target = ctx.message.author
		with sqlite3.connect('marry.db') as conn:
			c = conn.cursor()
			c.execute("SELECT * FROM status WHERE userid1 == {0} OR userid2 == {0}".format(target.id))
			response = c.fetchall()
			if not response: return await self.bot.say("Persoana precizată nu este căsătorită.")
			time_now = int(datetime.datetime.now().strftime("%s"))
			time_final = time_now - response[0][2]
			time_days_final = (time_now - response[0][2]) / 60 / 60 / 24
			try:
				await self.bot.say("**STATISTICI PENTRU** {0.mention} & {1.mention}```apache\nCăsătoriţi de {2:.0f} zile ({3})```".format(ctx.message.server.get_member(str(response[0][0])), ctx.message.server.get_member(str(response[0][1])), time_days_final, datetime.datetime.fromtimestamp(response[0][2]).strftime("%d-%m-%Y %H:%M:%S")))
			except:
				await self.bot.say("A intervenit o eroare, unul sau mai mulți membri nu sunt regăsiți în acest server.")

def setup(bot):
	bot.add_cog(Marry(bot))