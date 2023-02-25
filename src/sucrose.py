# uses pycord
# run from here, don't run the other files
import discord
import os
from dotenv import load_dotenv
from discord.ext import commands, bridge

load_dotenv()
bot = bridge.Bot(intents=discord.Intents.all(), command_prefix="s!")
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

@bot.event
async def on_connect():
    print("Connected!")
    # change this bot's status. for now, it's currently impossible to have a status just like a normal user would. for bots, you need to set it as an activity (listening, playing, streaming, etc.).
    await bot.change_presence(activity=discord.Game(name="VALORANT"), status=discord.Status.dnd)
    # await bot.change_presence(activity=discord.Streaming(name="VALORANT", url="https://code.visualstudio.com/docs/languages/dotnet", game="VALORANT"), status=discord.Status.dnd)
    # await bot.change_presence(status=discord.Status.offline)

cogs = [
    "basic",
    "music",
    "other"
]

for cog in cogs:
    bot.load_extension(cog)

bot.run(TOKEN)