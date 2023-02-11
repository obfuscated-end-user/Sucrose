# uses pycord
import discord
import os
import random
from dotenv import load_dotenv
from discord.ext import bridge, commands

load_dotenv()
bot = bridge.Bot(intents=discord.Intents.all(), command_prefix="s!")
TOKEN = os.getenv("SUCROSE_TOKEN")

# customizing help
class Help(commands.MinimalHelpCommand):
    async def send_pages(self):
        # the channel used to send this help command
        destination = self.get_destination()
        # for each page in this help command
        for page in self.paginator.pages:
            # make an embed
            emby = discord.Embed(description=page)
            # and send the embed to the current destination
            await destination.send(embed=emby)
# override the default help command
bot.help_command = Help()

""""
TO-DO:
make this bot play music, support both youtube and spotify urls
distinguish offline from invisibility status, if not impossible

NOTE:
there's a tendency that discord syncs the slash commands slow as shit and are not immediately recognized, but their command_prefix counterparts work fine.
"""

@bot.event
async def on_ready():
    print(f"{bot.user.name} is ready and online!")
    await bot.change_presence(activity=discord.Game(name="God"))

@bot.bridge_command()
async def hello(ctx):
    """I greet you back."""
    hello_quotes = [
        "Hello.",
        "Hi.",
        "sup bro you good",
        "eat shit bro"
    ]
    response = random.choice(hello_quotes)
    print(f"{ctx.author.name} ran hello\nmessage: {response}")
    await ctx.respond(response)

@bot.bridge_command()
async def say(ctx):
    """Says something random in the current channel."""
    responses = [
        "wala kang tite",
        "putang ina mo",
        f"tang ina mo {ctx.author.name}",
    ]
    response = random.choice(responses)
    print(f"{ctx.author.name} ran say\nmessage: {response}")
    await ctx.respond(response)

@bot.bridge_command()
async def ping(ctx):
    """Sends the bot's latency, in milliseconds."""
    print(f"{ctx.author.name} ran ping\nmessage: {int(bot.latency * 1000)}ms")
    await ctx.respond(f"Ping: {int(bot.latency * 1000)}ms")

# used for testing commands that take arguments
@bot.bridge_command()
async def sum(ctx, num1, num2):
    """Adds two numbers together and says the result in the current channel."""
    sum = float(num1) + float(num2)
    print(f"{ctx.author.name} ran ping\nmessage: The sum of {num1} and {num2} is {sum}.")
    await ctx.respond(f"The sum of {num1} and {num2} is {sum}.")

@bot.bridge_command()
async def echo(ctx, *, message):
    """Parrots back whatever you said."""
    print(f"{ctx.author.name} ran echo\nmessage: {message}")
    await ctx.respond(message)

bot.run(TOKEN)