import os
import requests
import time

import discord
import morefunc as m

from bs4 import BeautifulSoup
from datetime import datetime
from dateutil.relativedelta import relativedelta
from discord.ext import bridge, commands
from morefunc import bcolors as c
from random import choice, shuffle
from sucrose import make_embed

dir_path = os.path.dirname(os.path.realpath(__file__))
bot = bridge.Bot()

start = time.time()
yt_ids = m.load_yt_id_file()
shuffle(yt_ids)
yt_ids = yt_ids[:2000]
end = time.time()
m.print_with_timestamp(f"Time taken to process the ID list: {end - start}")

class Yt_Bot(commands.Cog):
	def __init__(self, bot: discord.ext.bridge.Bot):
		self.bot = bot
		self.last_warning_time = {}


	@bot.bridge_command(aliases=["rv", "ytlink", "ytl", "youtube", "randomvideo", "randvid"])
	async def yt(
		self,
		ctx: discord.ext.bridge.context.BridgeApplicationContext
	) -> None:
		"""
		(NSFW WARNING) Returns a random YouTube link.
		May sometimes return deleted/privated/region-locked videos.
		"""
		start = time.time()
		await ctx.defer()

		user_id = ctx.author.id
		now_user = time.time()
		cooldown = 180

		id = get_id()
		# link = random.choice(yt_link_formats) + id # DO NOT USE
		link = m.yt_link_formats[3] + id
		soup = BeautifulSoup(requests.get(link).text, "html.parser") # "lxml" doesn't work
		# view_count_temp = soup.select_one("meta[itemprop='interactionCount'][content]")["content"]
		# 2025/04/01 - from "interactionCount" to "userInteractionCount"
		# 2025/05/15 - view_count_temp = soup.find("meta", attrs={"itemprop":"userInteractionCount"})["content"]
		view_count_temp = soup.find_all("meta", attrs={"itemprop":"userInteractionCount"})[1]["content"]
		view_count = f"{int(view_count_temp):,}"
		uploader = soup.select_one("link[itemprop='name'][content]")["content"].replace("*", "\*")
		title = soup.find_all(name="title")[0].text.split(" - YouTube")[0].replace("*", "\*")
	
		# the dates will depend on your time zone
		# for example, all dates returned by soup are one day ahead
		# this reflects the fact that i'm a day ahead from where youtube is from
		date_uploaded = soup.find_all("meta", attrs={"itemprop":"uploadDate"})[0]["content"]
		date_obj = datetime.strptime(date_uploaded[:10], "%Y-%m-%d")
		date_uploaded = f"{date_obj.day} {date_obj.strftime('%B %Y')}"

		now = datetime.now()
		delta = relativedelta(now, date_obj)
		parts = []
		if delta.years > 0:
			parts.append(f"{delta.years} year{'s' if delta.years > 1 else ''}")
		if delta.months > 0:
			parts.append(f"{delta.months} month{'s' if delta.months > 1 else ''}")
		if delta.days > 0:
			parts.append(f"{delta.days} day{'s' if delta.days > 1 else ''}")
		time_diff = ", ".join(parts) + " ago" if parts else "today"

		embed_string = (
			"If the embed does not show up, the video "
			"may be deleted or set to private. "
			"Alternatively, you can try viewing it "
			f"[here](https://web.archive.org/web/https://www.youtube.com/watch?v={id}).\n"
			f"Click [here](https://web.archive.org/save/https://www.youtube.com/shorts/{id}) "
			"to save a copy to the Wayback Machine."
			f"\n\nTitle: **{title}**\nUploader: **{uploader}**\nDate uploaded: "
			f"**{date_uploaded} ({time_diff})**\nViews: **{view_count}**"
		)

		# prevents sending the nsfw warning every invocation
		if user_id not in self.last_warning_time or now_user - self.last_warning_time[user_id] > cooldown:
			self.last_warning_time[user_id] = now_user
			await ctx.respond(embed=make_embed(f"### ⚠️ POTENTIAL NSFW/L WARNING!\n" + embed_string))
		else:
			await ctx.respond(embed=make_embed(embed_string))
	
		await ctx.respond(f"[link]({link})")
		end = time.time()
		m.print_with_timestamp(f"Time taken by s!yt: {end - start}")
		m.print_with_timestamp(
			f"{c.OKBLUE}@{ctx.author.name}{c.ENDC} in "
			f"{c.OKGREEN}{ctx.guild.name}{c.ENDC} - YT - {id} {self.last_warning_time}"
		)


	@bot.bridge_command()
	@commands.is_owner()
	@commands.has_permissions(administrator=True)
	async def ytdebug(
		self,
		ctx: discord.ext.bridge.context.BridgeApplicationContext
	) -> None:
		"""
		Debug s!yt.
		"""
		start = time.time()

		random_links = []
		for _ in range(5):
			random_links.append(choice(m.yt_link_formats) + choice(yt_ids))

		await ctx.respond(
			f"{random_links[0][-11:]} {random_links[1][-11:]} {random_links[2][-11:]} "
			f"{random_links[3][-11:]} {random_links[4][-11:]}\n{random_links[0]}"
			f"\n{random_links[1]}\n{random_links[2]}\n{random_links[3]}\n{random_links[4]}"
		)
		end = time.time()
		m.print_with_timestamp(f"Time taken by s!ytdebug: {end - start}")
		m.print_with_timestamp(
			f"{c.OKBLUE}@{ctx.author.name}{c.ENDC} in "
			f"{c.OKGREEN}{ctx.guild.name}{c.ENDC} - YTDEBUG"
		)


s = requests.Session()
def get_id() -> str:
	"""
	Get ID. This should not return an ID for a deleted/privated video.
	"""
	id = choice(yt_ids)
	m.print_with_timestamp(f"INIT: {id}")
	id_availability = m.is_id_available(id, s, include_private=True)
	while (id_availability):
		m.print_with_timestamp(f"EPIC FAIL 404: {id}")
		yt_ids.remove(id)
		id = choice(yt_ids)
		id_availability = m.is_id_available(id, s, include_private=True)

	# id = choice(m.hj)
	m.print_with_timestamp(f"SUCCESS 200: {id}")
	return id


def setup(bot):
	bot.add_cog(Yt_Bot(bot))
