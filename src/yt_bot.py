import discord
import random
import requests
import os
import time

from bs4 import BeautifulSoup
from discord.ext import bridge, commands
from sucrose import make_embed

dir_path = os.path.dirname(os.path.realpath(__file__))
bot = bridge.Bot()

yt_link_formats = [
    "https://www.youtube.com/watch?v=",
    "https://youtu.be/",
    "http://y2u.be/",
]

start = time.time()
with open(f"{dir_path}/yt_ids.txt", "r") as file:
    yt_ids = [id for [id] in [line.strip().split("\n") for line in file.readlines()]]
end = time.time()
print(f"Time taken to process the ID list: {end - start}")

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
        link = yt_link_formats[1] + id
        soup = BeautifulSoup(requests.get(link).text, "html.parser") # "lxml" doesn't work
        view_count_temp = soup.select_one("meta[itemprop='interactionCount'][content]")["content"]
        view_count = f"{int(view_count_temp):,}"
        uploader = soup.select_one("link[itemprop='name'][content]")["content"].replace("*", "\*")
        title = soup.find_all(name="title")[0].text.strip(" - YouTube").replace("*", "\*")
        await ctx.respond(embed=make_embed(f"### ⚠️ POTENTIAL NSFW/NSFL WARNING! ⚠️\nIf the embed does not show up, the video may be deleted, or is set to private. Alternatively, you can try viewing it [here](https://web.archive.org/web/https://www.youtube.com/watch?v={id}).\n\nTitle: **{title}**\nUploader: **{uploader}**\nViews: **{view_count}**"))
    
        await ctx.respond(link)
        end = time.time()
        print(f"Time taken by s!yt: {end - start}")


    @bot.bridge_command()
    async def ytdebug(self, ctx: discord.ext.bridge.context.BridgeApplicationContext):
        """debug yt command"""
        start = time.time()

        random_links = []
        for _ in range(5):
            random_links.append(random.choice(yt_link_formats) + random.choice(yt_ids))

        await ctx.respond(f"{random_links[0][-11:]} {random_links[1][-11:]} {random_links[2][-11:]} {random_links[3][-11:]} {random_links[4][-11:]}\n{random_links[0]}\n{random_links[1]}\n{random_links[2]}\n{random_links[3]}\n{random_links[4]}")
        end = time.time()
        print(f"Time taken by s!ytdebug: {end - start}")


s = requests.Session()
def is_id_available(id):
    """Check if ID is available. Returns True if ID is not available, False otherwise."""
    check = s.get(f"https://youtu.be/{id}")
    indicators = [
        "Video unavailable",
        "This video isn't available anymore",
        "Private video"
    ]
    response = [indicator for indicator in indicators if (indicator in check.text)]

    return bool(response)


def get_id():
    """Get ID. This should not return an ID for a deleted/privated video."""
    id = random.choice(yt_ids)
    print(f"INIT: {id}")
    id_availability = is_id_available(id)
    while (id_availability):
        print(f"EPIC FAIL 404: {id}")
        yt_ids.remove(id)
        id = random.choice(yt_ids)
        id_availability = is_id_available(id)

    print(f"SUCCESS 200: {id}")
    return id


def setup(bot):
    bot.add_cog(Yt_Bot(bot))
