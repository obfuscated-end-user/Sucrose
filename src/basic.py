# uses pycord
import discord
import random
import sucrose_dict
from dotenv import load_dotenv
from discord.ext import bridge, commands
from sucrose import anemo_color

load_dotenv()
bot = bridge.Bot()

class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # REGULAR COMMANDS
    @bot.bridge_command()
    async def hello(self, ctx):
        """Sucrose greets you back."""
        hello_quotes = [
            "Hello!",
            "Nice to meet you!",
            "Hi!",
            "sup bro you good"
        ]
        response = random.choice(hello_quotes)
        await ctx.respond(response)

    @bot.bridge_command()
    async def say(self, ctx):
        """Says something random in the current channel."""
        responses = [
            "Anemo test 6308!",
            "Adsorption test.",
            "死ね！",
            f"{ctx.author.name} is a faggot!",
            "はじめまして、スクロースと申します。えっと。。。あたし、頑張る！",
            "wala kang tite",
            "putang ina mo",
            f"tang ina mo {ctx.author.name}"
        ]
        response = random.choice(responses)
        await ctx.respond(response)

    @bot.bridge_command(aliases=["latency", "ms"])
    async def ping(self, ctx):
        """Sends the bot's latency, in milliseconds."""
        await ctx.respond(f"Ping: {int(self.bot.latency * 1000)}ms")

    @bot.bridge_command()
    async def sum(self, ctx, num1, num2):
        """Adds two numbers together and says the result in the current channel."""
        sum = float(num1) + float(num2)
        await ctx.respond(f"The sum of {num1} and {num2} is {sum}.")

    @bot.bridge_command()
    async def echo(self, ctx, *, message):
        """Parrots back whatever you said."""
        await ctx.respond(message)

    @bot.bridge_command(aliases=["disconnect", "out", "leave", "dc"])
    async def voice_disconnect(self, ctx):
        """Leaves your voice channel."""
        vc = ctx.guild.voice_client
        if vc:
            await vc.disconnect()

def setup(bot):
    bot.add_cog(Basic(bot))
