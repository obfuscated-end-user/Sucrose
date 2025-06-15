# uses pycord
# repo here: https://github.com/Pycord-Development/pycord
# docs here: https://docs.pycord.dev/en/stable
# remember to add the copyright copypasta that all published code on github must possess
# run from here, don't run the other files

import os
import random

import discord
import morefunc as m
import sucrose_dict

from dotenv import load_dotenv
from discord.ext import commands, bridge, tasks

load_dotenv()
bot = bridge.Bot(intents=discord.Intents.all(), command_prefix="s!")    # main
# bot = bridge.Bot(intents=discord.Intents.all(), command_prefix="d!")    # debug
TOKEN = os.getenv("SUCROSE_TOKEN")
# TOKEN = os.getenv("TESTING_TOKEN")  # debug

# customizing help
# function docstrings are used for help info
class Help(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            await destination.send(embed=make_embed(page))

bot.help_command = Help()


def make_embed(text: str) -> discord.Embed:
    """Returns an embed."""
    return discord.Embed(description=text, color=discord.Colour.from_rgb(84, 220, 179)) # anemo color


@bot.event
async def on_ready() -> None:
    m.print_with_timestamp(f"{m.bcolors.OKBLUE}{bot.user.name}{m.bcolors.ENDC} is ready and online!")
    change_status_task.start()


@bot.event
async def on_connect() -> None:
    m.print_with_timestamp(f"{m.bcolors.OKGREEN}Connected!{m.bcolors.ENDC}")
    # major bug: song queue is the same across all servers this bot has joined in, fix it by checking if the server id is the same as the caller


@bot.event
async def on_disconnect() -> None:
    m.print_with_timestamp(f"{m.bcolors.FAIL}Disonnected!{m.bcolors.ENDC}")


@bot.event
async def on_application_command_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.respond(make_embed("❌ Invalid argument type provided."), ephemeral=True)
    else:
        raise error


# change Sucrose's status on specified interval
@tasks.loop(seconds=10)
async def change_status_task() -> None:
    # change this bot's status. for now, it's currently impossible to have a status just like a normal user would. for bots, you need to set it as an activity (listening, playing, streaming, etc.).
    discord_statuses = [discord.Status.dnd, discord.Status.idle, discord.Status.online]
    game_name = random.choice(sucrose_dict.activity_names)
    discord_status = random.choice(discord_statuses)
    await bot.change_presence(activity=discord.Game(name=game_name), status=discord_status)


cogs = [
    "basic",
    "music",
    "other",
    "yt_bot"
]

for cog in cogs:
    bot.load_extension(cog)

# makes the bot work
bot.run(TOKEN)
