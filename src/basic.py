# uses pycord
import discord
import random
from discord.ext import bridge, commands
from sucrose import make_embed

bot = bridge.Bot()

class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @bot.bridge_command()
    async def hello(self, ctx):
        """Sucrose greets you back."""
        hello_quotes = [
            "Hello!",
            "Nice to meet you!",
            "Hi!",
            "sup bro you good"
        ]
        await ctx.respond(random.choice(hello_quotes))

    @bot.bridge_command(aliases=["latency", "ms"])
    async def ping(self, ctx):
        """Sends the bot's latency, in milliseconds."""
        await ctx.respond(embed=make_embed(f"{int(self.bot.latency * 1000)}ms"), delete_after=20)

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
