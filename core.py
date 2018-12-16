import discord
from discord.ext import commands
import aiofiles

import sys
import traceback

prefix = ('/', 'leaks pls ', 'views pls ', 'reacher pls ', 'krusher pls ', 'kenn pls ', 'emrys pls ', 'maribu pls ')
bot = commands.Bot(command_prefix=prefix, pm_help=None)
bot.remove_command('help')

ext = ['mod', 'info', 'update', 'marry', 'birth', 'roles']

@bot.event
async def on_ready():
	await bot.change_presence(status=discord.Status.dnd, game=discord.Game(name="www.leaks.ro", type=0))
	print("connected to discord")

@bot.event
async def on_member_join(member):
	if not member.server.id == "451066437789024256": return
	role = discord.utils.get(member.server.roles, name="Member")
	await bot.add_roles(member, role)

@bot.event
async def on_command_error(error, ctx):
    channel = ctx.message.channel
    if isinstance(error, commands.CommandOnCooldown):
        await bot.send_message(ctx.message.channel, "Nu poti folosi comanda pentru inca {retry_after:.2f} secunde.".format(retry_after=error.retry_after))
    elif isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        return
    elif isinstance(error, commands.CommandInvokeError):
        print('In {0.command.qualified_name}:'.format(ctx), file=sys.stderr)
        traceback.print_tb(error.original.__traceback__)
        print('{0.__class__.__name__}: {0}'.format(error.original), file=sys.stderr)

@bot.command(pass_context=True)
async def reload(ctx, *, ext: str):
	if not ctx.message.author.id == "443476962871214090": return
	try:
		bot.unload_extension('ext.'+ext)
		bot.load_extension('ext.'+ext)
		await bot.say("extensia `{0}` a fost reincarcata cu succes".format(ext))
	except ImportError:
		await bot.say("extensia `{0}` n-a putut fi gasita".format(ext))

if __name__ == '__main__':
    for ex in ext:
        try:
            bot.load_extension('ext.'+ex)
            bot.load_extension('eval.ban')
        except Exception as e:
            print('Failed to load extension {}\n{}: {}'.format(ex, type(e).__name__, e))

bot.run('token')
