# uses pycord
import aiohttp
import asyncio
import os
import random

import discord
import morefunc as m
import requests

from datetime import datetime
from discord.ext import bridge, commands
from morefunc import bcolors as c
from sucrose import make_embed, ANEMO_COLOR

bot = bridge.Bot()

class Basic(commands.Cog):
	def __init__(self, bot: discord.ext.bridge.Bot):
		self.bot = bot

	@bot.bridge_command()
	async def hello(
		self,
		ctx: discord.ext.bridge.context.BridgeApplicationContext
	) -> None:
		"""
		Sucrose greets you back.
		"""
		hello_quotes = [
			"Hello!",
			"Nice to meet you!",
			"Hi!",
			"sup bro you good"
		]
		await ctx.respond(random.choice(hello_quotes))
		m.print_with_timestamp(
			f"{c.OKBLUE}@{ctx.author.name}{c.ENDC} in "
			f"{c.OKGREEN}{ctx.guild.name}{c.ENDC} - HELLO"
		)


	@bot.bridge_command(aliases=["latency", "ms"])
	async def ping(
		self,
		ctx: discord.ext.bridge.context.BridgeApplicationContext
	) -> None:
		"""
		Sends the bot's latency, in milliseconds.
		"""
		latency = f"{int(self.bot.latency * 1000)}ms"
		await ctx.respond(embed=make_embed(latency), delete_after=20)
		m.print_with_timestamp(
			f"{c.OKBLUE}@{ctx.author.name}{c.ENDC} in "
			f"{c.OKGREEN}{ctx.guild.name}{c.ENDC} - PING {latency}"
		)


	@bot.bridge_command()
	async def sum(
		self,
		ctx: discord.ext.bridge.context.BridgeApplicationContext,
		num1: float,
		num2: float
	) -> None:
		"""
		Adds two numbers together and says the result in the current channel.
		"""
		sum = num1 + num2
		await ctx.respond(f"The sum of {num1} and {num2} is {sum}.")
		m.print_with_timestamp(
			f"{c.OKBLUE}@{ctx.author.name}{c.ENDC} in "
			f"{c.OKGREEN}{ctx.guild.name}{c.ENDC} - SUM"
		)


	@bot.bridge_command()
	async def echo(
		self,
		ctx: discord.ext.bridge.context.BridgeApplicationContext,
		*,
		msg: str
	) -> None:
		"""
		Parrots back whatever you said.
		"""
		await ctx.respond(msg)
		m.print_with_timestamp(
			f"{c.OKBLUE}@{ctx.author.name}{c.ENDC} in "
			f"{c.OKGREEN}{ctx.guild.name}{c.ENDC} - ECHO {msg}"
		)


	@bot.bridge_command(aliases=["wk", "wiki"])
	async def wikipedia(
		self,
		ctx: discord.ext.bridge.context.BridgeApplicationContext
	) -> None:
		"""
		Fetch a random English Wikipedia article.
		"""
		try:
			response = requests.get("https://en.wikipedia.org/wiki/Special:Random")

			url = response.url
			# wikipedia article urls are like:
			# https://en.wikipedia.org/wiki/Article_Name
			article_name = url.split("/wiki/")[-1].replace("_", " ")
			markdown_link = f"[.]({url})"

			await ctx.respond(
				f"Here's a random Wikipedia article for you:\n{markdown_link}"
			)
		except requests.RequestException as e:
			await ctx.respond(f"EPIC FAIL: {e}")
		m.print_with_timestamp(
			f"{c.OKBLUE}@{ctx.author.name}{c.ENDC} in "
			f"{c.OKGREEN}{ctx.guild.name}{c.ENDC} - WIKIPEDIA - {article_name}"
		)


	@bot.bridge_command(aliases=["sing"])
	async def tts(
		self,
		ctx: discord.ext.bridge.context.BridgeApplicationContext,
		*,
		msg: str
	) -> None:
		"""
		Parrots back whatever you said, using my voice. (not really)
		TTS voice will depend on your Discord's language settings.
		"""
		await ctx.send(f"\"{msg}\"", tts=True, delete_after=15)
		m.print_with_timestamp(
			f"{c.OKBLUE}@{ctx.author.name}{c.ENDC} in "
			f"{c.OKGREEN}{ctx.guild.name}{c.ENDC} - TTS - {msg}"
		)


	@bot.bridge_command(aliases=["xk"])
	async def xkcd(
		self,
		ctx: discord.ext.bridge.context.BridgeApplicationContext
	) -> None:
		"""
		Get random xkcd comic.
		"""
		MAX_XKCD_COUNT = 3108
		# because xkcd #404 actually returns a 404 page
		id = random.choice([i for i in range(1, MAX_XKCD_COUNT) if i not in [404]])
		# https://xkcd.com/json.html
		url = f"https://xkcd.com/{id}/info.0.json"
		async with aiohttp.ClientSession() as session:
			async with session.get(url) as resp:
				if resp.status != 200:
					await ctx.respond(
						embed=make_embed("something happened lol"),
						delete_after=20
					)
					return
				data = await resp.json()
		embed = discord.Embed(
			title=f"xkcd #{data['num']}: {data['title']}",
			url=f"https://xkcd.com/{data['num']}",
			description=data.get("alt", ""),
			color=ANEMO_COLOR
		)
		embed.set_image(url=data["img"])
		embed.set_footer(text="xkcd")
		await ctx.respond(embed=embed, delete_after=60)
		m.print_with_timestamp(
			f"{c.OKBLUE}@{ctx.author.name}{c.ENDC} in "
			f"{c.OKGREEN}{ctx.guild.name}{c.ENDC} - XKCD - {id}"
		)


	@bot.bridge_command(aliases=["think"])
	async def type(
		self, 
		ctx: discord.ext.bridge.context.BridgeApplicationContext, 
		*, 
		interval: int=10
	) -> None:
		"""
		Pretends to send a very important announcement.
		"""
		repeat_interval = 5
		elapsed = 0

		while elapsed < interval:
			await ctx.trigger_typing()
			to_sleep = min(repeat_interval, interval - elapsed)
			await asyncio.sleep(to_sleep)
			elapsed += to_sleep

		m.print_with_timestamp(
			f"{c.OKBLUE}@{ctx.author.name}{c.ENDC} in "
			f"{c.OKGREEN}{ctx.guild.name}{c.ENDC} - TYPE - {interval}"
		)



	@bot.bridge_command(aliases=["fumofumo"])
	async def fumo(
		self, 
		ctx: discord.ext.bridge.context.BridgeApplicationContext
	) -> None:
		"""
		ᗜˬᗜ
		"""
		fumo_path = f"{m.dir_path}/ignore/fumo"

		images = [file for file in os.listdir(fumo_path)
			if file.lower().endswith((".png", ".jpg", ".jpeg", ".gif", "webp"))]
		
		if not images:
			await ctx.respond("ᗜ˰ᗜ NOT FUNKY")
			return

		chosen_fumo = random.choice(images)
		file_path = os.path.join(fumo_path, chosen_fumo)
		file = discord.File(file_path, filename=chosen_fumo)

		m.print_with_timestamp(
			f"{c.OKBLUE}@{ctx.author.name}{c.ENDC} in "
			f"{c.OKGREEN}{ctx.guild.name}{c.ENDC} - FUMO - {file.filename}"
		)

		await ctx.respond(file=file)


	@bot.bridge_command(aliases=["abt"])
	async def about(
		self, 
		ctx: discord.ext.bridge.context.BridgeApplicationContext
	) -> None:
		"""
		About Sucrose.
		"""
		await ctx.respond(embed=make_embed(
				f"# Sucrose\nMade by obfuscated-end-user (横浜).\n\n"
				f"© 2023-{datetime.now().strftime('%Y')}"
			),
			delete_after=30
		)
		m.print_with_timestamp(
			f"{c.OKBLUE}@{ctx.author.name}{c.ENDC} in "
			f"{c.OKGREEN}{ctx.guild.name}{c.ENDC} - ABOUT"
		)


	@commands.has_permissions(administrator=True)
	@bot.bridge_command(aliases=["disconnect", "out", "leave", "dc"])
	async def voice_disconnect(
		self,
		ctx: discord.ext.bridge.context.BridgeApplicationContext
	) -> None:
		"""
		Leaves your voice channel.
		"""
		vc = ctx.guild.voice_client
		if vc:
			await vc.disconnect()
		m.print_with_timestamp(
			f"{c.OKBLUE}@{ctx.author.name}{c.ENDC} in "
			f"{c.OKGREEN}{ctx.guild.name}{c.ENDC} - VOICE_DISCONNECT"
		)


def setup(bot):
	bot.add_cog(Basic(bot))
