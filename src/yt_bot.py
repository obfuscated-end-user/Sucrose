import discord
import morefunc as m
import requests
import os
import time
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil.relativedelta import relativedelta
from discord.ext import bridge, commands
from random import choice, shuffle
from sucrose import make_embed

dir_path = os.path.dirname(os.path.realpath(__file__))
bot = bridge.Bot()

start = time.time()
yt_ids = m.load_yt_id_file()
shuffle(yt_ids)
yt_ids = yt_ids[:2000]
end = time.time()
print(f"Time taken to process the ID list: {end - start}\n")
print(yt_ids, "\n")

class Yt_Bot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @bot.bridge_command(aliases=["ytlink", "ytl", "youtube", "randomvideo", "randvid"])
    async def yt(self, ctx: discord.ext.bridge.context.BridgeApplicationContext):
        """(NSFW WARNING) Returns a random YouTube link. May sometimes return deleted/privated videos."""
        start = time.time()
        await ctx.response.defer()

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

        await ctx.respond(embed=make_embed(f"### ⚠️ POTENTIAL NSFW/L WARNING!\nIf the embed does not show up, the video may be deleted or set to private. Alternatively, you can try viewing it [here](https://web.archive.org/web/https://www.youtube.com/watch?v={id}).\nClick [here](https://web.archive.org/save/https://www.youtube.com/shorts/{id}) to save a copy to the Wayback Machine.\n\nTitle: **{title}**\nUploader: **{uploader}**\nDate uploaded: **{date_uploaded} ({time_diff})**\nViews: **{view_count}**"))
        # https://www.youtube.com/shorts/{id}
        # https://web.archive.org/web/https://www.youtube.com/shorts/{id}
        # https://web.archive.org/save/https://www.youtube.com/shorts/{id}
        # , delete_after=200
    
        await ctx.respond(f"[link]({link})")
        end = time.time()
        print(f"Time taken by s!yt: {end - start}")


    @bot.bridge_command()
    async def ytdebug(self, ctx: discord.ext.bridge.context.BridgeApplicationContext):
        """debug yt command"""
        start = time.time()

        random_links = []
        for _ in range(5):
            random_links.append(choice(m.yt_link_formats) + choice(yt_ids))

        await ctx.respond(f"{random_links[0][-11:]} {random_links[1][-11:]} {random_links[2][-11:]} {random_links[3][-11:]} {random_links[4][-11:]}\n{random_links[0]}\n{random_links[1]}\n{random_links[2]}\n{random_links[3]}\n{random_links[4]}")
        end = time.time()
        print(f"Time taken by s!ytdebug: {end - start}")


s = requests.Session()
def get_id():
    """Get ID. This should not return an ID for a deleted/privated video."""
    id = choice(yt_ids)
    print(f"INIT: {id}")
    id_availability = m.is_id_available(id, s, include_private=True)
    while (id_availability):
        print(f"EPIC FAIL 404: {id}")
        yt_ids.remove(id)
        id = choice(yt_ids)
        id_availability = m.is_id_available(id, s, include_private=True)

    # id = choice(m.hj)
    print(f"SUCCESS 200: {id}")
    return id


def setup(bot):
    bot.add_cog(Yt_Bot(bot))
