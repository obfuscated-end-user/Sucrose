# uses pycord
# run from here, don't run the cogs
import discord
import os
from dotenv import load_dotenv
from discord.ext import commands, bridge

load_dotenv()
bot = bridge.Bot(intents=discord.Intents.all(), command_prefix="s!")
# bot = bridge.Bot(intents=discord.Intents.all(), command_prefix="d!")    # debug
TOKEN = os.getenv("SUCROSE_TOKEN")
# TOKEN = os.getenv("TESTING_TOKEN")  # debug

anemo_color = discord.Colour.from_rgb(84, 220, 179)

# customizing help
class Help(commands.MinimalHelpCommand):
    async def send_pages(self):
        # the channel used to send this help command
        destination = self.get_destination()
        # for each page in this help command
        for page in self.paginator.pages:
            # make an embed
            embed = discord.Embed(description=page, color=anemo_color)
            # and send the embed to the current destination
            await destination.send(embed=embed)
# override the default help command
bot.help_command = Help()

@bot.event
async def on_ready():
    print(f"{bot.user.name} is ready and online!")
    # change Sucrose's status. for now, it's currently impossible to have a status just like a normal user would. for bots, you need to set it as an activity (listening, playing, streaming, etc.).

@bot.event
async def on_connect():
    print("Connected!")
    await bot.change_presence(activity=discord.Game(name="God"), status=discord.Status.idle)
    # await bot.change_presence(status=discord.Status.offline)

cogs_list = [
    "basic",
    "music"
]

for cog in cogs_list:
    bot.load_extension(cog)

bot.run(TOKEN)