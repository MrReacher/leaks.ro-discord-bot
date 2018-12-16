import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

from bs4 import BeautifulSoup
import aiohttp
import re
import time
import json
import random
import asyncio

class Db:

    def __init__(self, name, **options):
        self.name = name
        self.object_hook = options.pop('object_hook', None)
        self.encoder = options.pop('encoder', None)
        self.loop = options.pop('loop', asyncio.get_event_loop())
        if options.pop('load_later', False):
            self.loop.create_task(self.load())
        else:
            self.load_from_file()

    def load_from_file(self):
        try:
            with open(self.name, 'r') as f:
                self._db = json.load(f, object_hook=self.object_hook)
        except FileNotFoundError:
            self._db = {}

    async def load(self):
        await self.loop.run_in_executor(None, self.load_from_file)

    def _dump(self):
        with open(self.name, 'w') as f:
            json.dump(self._db, f, ensure_ascii=True, cls=self.encoder)

    async def save(self):
        await self.loop.run_in_executor(None, self._dump)

    def get(self, key, *args):
        """Retrieves a config entry."""
        return self._db.get(key, *args)

    async def put(self, key, value, *args):
        """Edits a config entry."""
        self._db[key] = value
        await self.save()

    async def remove(self, key):
        """Removes a config entry."""
        del self._db[key]
        await self.save()

    def __contains__(self, item):
        return self._db.__contains__(item)

    def __len__(self):
        return self._db.__len__()

    def all(self):
        return self._db

class Info:

	def __init__(self, bot):
		self.bot = bot
		self.db = Db('maribu.json', loop=bot.loop)

	async def on_member_join(self, member):
		embed = discord.Embed(title="Membru Nou", color=2858731, description="© 2018 leaks.ro")
		embed.add_field(name=member.server.name, value="Bine ai venit, {}".format(member.mention))
		embed.set_thumbnail(url="https://i.imgur.com/2OM81ez.png")
		embed.set_footer(text="Creat special pentru comunitatea Leaks România | {0}".format(time.strftime("%d-%m-%Y %H:%M:%S")))
		delete = await self.bot.send_message(self.bot.get_channel("451066437789024258"), embed=embed)
		await asyncio.sleep(10)
		await self.bot.delete_message(delete)

	@commands.command(pass_context=True, name="help")
	async def __help(self, ctx):
		channel = self.bot.get_channel("451296527084814348")
		author = ctx.message.author
		if not ctx.message.channel == channel and not author.server_permissions.administrator: return await self.bot.say("Comenzile trebuie folosite doar în {0}.".format(channel.mention), delete_after=3)

		embed = discord.Embed(title="Ajutor", color=2858731, description="© 2018 leaks.ro")
		embed.add_field(inline=False, name="Informaţii", value="/help - afişează toate comenzile.\n/info - informaţii despre forum & server.")
		embed.add_field(inline=False, name="Comenzi", value="/ban - interzice un membru pe server.\n/unban - elimină un membru din lista cu interziceri.\n/clear - şterge un anumit număr de mesaje.\n/mute - adu la tăcere un membru.\n/say - spune ceva în numele bot-ului.\n/marry - căsătorește-te pe discord.\n/birthday list - vezi cine își sărbătorește ziua de naștere.")
		embed.set_thumbnail(url="https://i.imgur.com/2OM81ez.png")
		embed.set_footer(text="Creat special pentru comunitatea Leaks România | {0}".format(time.strftime("%d-%m-%Y %H:%M:%S")))
		await self.bot.say(embed=embed)

	@commands.cooldown(1, 3, BucketType.server)
	@commands.command(pass_context=True)
	async def info(self, ctx):
		server = ctx.message.server
		author = ctx.message.author
		channel = self.bot.get_channel("451296527084814348")

		if not ctx.message.channel == channel and not author.server_permissions.administrator: return await self.bot.say("Comenzile trebuie folosite doar in {0}.".format(channel.mention), delete_after=3)

		delete = await self.bot.say("se incarcă, vă rugăm asteptați..")

		async with aiohttp.ClientSession() as ses:
			async with ses.get("http://tm5qwtee.leaks.ro/") as resp:
				response = await resp.read()
		soup = BeautifulSoup(response, 'html.parser')
		finds = [find for find in soup.find_all("span", class_="sr")]
		total_members = re.sub('[^0-9]', '', str(finds[2]))
		finds_4 = soup.find_all("span", class_="sr_last_member")
		newest_member = re.sub('\<(.*?)\>', '', str(finds_4[0]))
		finds_2 = soup.find_all("h4", class_="statistics_head")
		members_online_today = re.sub('\<(.*?)\>', '', str(finds_2[1]))
		members_online_today_2 = re.sub('[^0-9]', '', members_online_today)
		finds_3 = soup.find_all("h4", class_="statistics_head clearfix")
		online_members = re.sub('\<(.*?)\>', '', str(finds_3[0]))
		online_members_2 = re.findall('\d+', online_members)

		created_at = int(ctx.message.server.created_at.strftime("%s"))
		now = time.time()
		days_created_at = (now - created_at) / 60 / 60 / 24

		embed = discord.Embed(title="Informații", color=2858731, description="**{0}** ({1})".format(server.name, server.id))
		embed.set_thumbnail(url="https://i.imgur.com/2OM81ez.png")
		embed.add_field(inline=False, name='Forum', value="Total membri: {0}\nMembri online: {1}\nMembri online astăzi: {2}\nCel mai nou membru: {3}".format(total_members, online_members_2[0], members_online_today_2, newest_member))
		embed.add_field(inline=False, name='Server', value="Total membri: {0}\nMembri online: {1}\nOwner: {2}\nCreat acum: {3:.0f} zile".format(server.member_count, sum(1 for m in server.members if m.status is not discord.Status.offline), server.owner, days_created_at))

		await self.bot.say(embed=embed)
		await self.bot.delete_message(delete)

	@commands.cooldown(1, 20, BucketType.user)
	@commands.group(pass_context=True)
	async def duma(self, ctx):
		if ctx.invoked_subcommand is None:
			dume = self.db.get('dume', [])
			if len(dume) < 1: return 
			await self.bot.say(random.choice(dume))

	@duma.command(pass_context=True)
	async def add(self, ctx, *, duma: str=None):
		if ctx.message.author.server_permissions.administrator or ctx.message.author.id == "430686599756382219":
			if duma is None: return await self.bot.say("fmm maribule unde ti-e duma")

			dume = self.db.get('dume', [])
			if duma in dume: return await self.bot.say("prost esti ca e deja adaugata")

			dume.append(duma)
			await self.db.put('dume', dume)
			await self.bot.say("gt maribule am adaugat-o")
		else:
			await self.bot.say("n-ai acces haha")

def setup(bot):
	bot.add_cog(Info(bot))