# uses pycord
# repo here: https://github.com/Pycord-Development/pycord
# docs here: https://docs.pycord.dev/en/stable
# remember to add the copyright copypasta bullshit that all published code on github must possess

# run from here, don't run the other files
import discord
import os
import random
import sucrose_dict

from dotenv import load_dotenv
from discord.ext import commands, bridge, tasks

load_dotenv()
bot = bridge.Bot(intents=discord.Intents.all(), command_prefix="s!")    # main
# bot = bridge.Bot(intents=discord.Intents.all(), command_prefix="d!")    # debug
TOKEN = os.getenv("SUCROSE_TOKEN")
# TOKEN = os.getenv("TESTING_TOKEN")  # debug

# customizing help
class Help(commands.MinimalHelpCommand):
    async def send_pages(self):
        # the channel used to send this help command
        destination = self.get_destination()
        # for each page in this help command
        for page in self.paginator.pages:
            # make an embed
            embed = discord.Embed(description=page, color=discord.Colour.from_rgb(84, 220, 179))
            # and send the embed to the current destination
            await destination.send(embed=embed)
# override the default help command
bot.help_command = Help()

def make_embed(text: str) -> discord.Embed:
    """Returns an embed."""
    # anemo color
    return discord.Embed(description=text, color=discord.Colour.from_rgb(84, 220, 179))

@bot.event
async def on_ready():
    print(f"{bot.user.name} is ready and online!")
    change_status_task.start()

@bot.event
async def on_connect():
    print("Connected!")
    # major bug: song queue is the same across all servers this bot has joined in, fix it by checking if the server id is the same as the caller or some wacky shit

# change Sucrose's status on specified interval
@tasks.loop(seconds=10)
async def change_status_task():
    # change this bot's status. for now, it's currently impossible to have a status just like a normal user would. for bots, you need to set it as an activity (listening, playing, streaming, etc.).
    discord_statuses = [discord.Status.dnd, discord.Status.idle, discord.Status.online]
    game_name = random.choice(sucrose_dict.activity_names)
    discord_status = random.choice(discord_statuses)
    await bot.change_presence(activity=discord.Game(name=game_name), status=discord_status)

cogs = [
    "basic",
    # "music", # currently doesn't work, random updated module in pip fucked up the version i have installed in my machine, will fix later
    "other",
    "yt_bot"
]

for cog in cogs:
    bot.load_extension(cog)

# makes the bot work
bot.run(TOKEN)
