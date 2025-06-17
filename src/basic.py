# uses pycord
import random

import discord
import morefunc as m
import requests

from datetime import datetime
from discord.ext import bridge, commands
from morefunc import bcolors as c
from sucrose import make_embed

bot = bridge.Bot()

class Basic(commands.Cog):
    def __init__(self, bot: discord.ext.bridge.Bot):
        self.bot = bot

    @bot.bridge_command()
    async def hello(self, ctx: discord.ext.bridge.context.BridgeApplicationContext) -> None:
        """Sucrose greets you back."""
        hello_quotes = [
            "Hello!",
            "Nice to meet you!",
            "Hi!",
            "sup bro you good"
        ]
        await ctx.respond(random.choice(hello_quotes))
        m.print_with_timestamp(f"{c.OKBLUE}@{ctx.author.name}{c.ENDC} in {c.OKGREEN}{ctx.guild.name}{c.ENDC} - HELLO")


    @bot.bridge_command(aliases=["latency", "ms"])
    async def ping(self, ctx: discord.ext.bridge.context.BridgeApplicationContext) -> None:
        """Sends the bot's latency, in milliseconds."""
        await ctx.respond(embed=make_embed(f"{int(self.bot.latency * 1000)}ms"), delete_after=20)
        m.print_with_timestamp(f"{c.OKBLUE}@{ctx.author.name}{c.ENDC} in {c.OKGREEN}{ctx.guild.name}{c.ENDC} - PING")


    @bot.bridge_command()
    async def sum(self, ctx: discord.ext.bridge.context.BridgeApplicationContext, num1: float, num2: float) -> None:
        """Adds two numbers together and says the result in the current channel."""
        sum = float(num1) + float(num2)
        await ctx.respond(f"The sum of {num1} and {num2} is {sum}.")
        m.print_with_timestamp(f"{c.OKBLUE}@{ctx.author.name}{c.ENDC} in {c.OKGREEN}{ctx.guild.name}{c.ENDC} - SUM")


    @bot.bridge_command()
    async def echo(self, ctx: discord.ext.bridge.context.BridgeApplicationContext, *, msg:  str) -> None:
        """Parrots back whatever you said."""
        await ctx.respond(msg)
        m.print_with_timestamp(f"{c.OKBLUE}@{ctx.author.name}{c.ENDC} in {c.OKGREEN}{ctx.guild.name}{c.ENDC} - ECHO {msg}")


    @bot.bridge_command(aliases=["wk", "wiki"])
    async def wikipedia(self, ctx: discord.ext.bridge.context.BridgeApplicationContext) -> None:
        """Fetch a random English Wikipedia article."""
        try:
            response = requests.get("https://en.wikipedia.org/wiki/Special:Random")

            url = response.url
            # wikipedia article urls are like: https://en.wikipedia.org/wiki/Article_Name
            article_name = url.split("/wiki/")[-1].replace("_", " ")
            markdown_link = f"[.]({url})"

            await ctx.respond(f"Here's a random Wikipedia article for you:\n{markdown_link}")
        except requests.RequestException as e:
            await ctx.respond(f"EPIC FAIL: {e}")
        m.print_with_timestamp(f"{c.OKBLUE}@{ctx.author.name}{c.ENDC} in {c.OKGREEN}{ctx.guild.name}{c.ENDC} - WIKIPEDIA - {article_name}")


    @bot.bridge_command(aliases=["sing"])
    async def tts(self, ctx: discord.ext.bridge.context.BridgeApplicationContext, *, msg: str) -> None:
        """
        Parrots back whatever you said, using my voice. (not really)
        TTS voice will depend on your Discord's language settings.
        """
        await ctx.send(f"\"{msg}\"", tts=True, delete_after=15)
        m.print_with_timestamp(f"{c.OKBLUE}@{ctx.author.name}{c.ENDC} in {c.OKGREEN}{ctx.guild.name}{c.ENDC} - TTS - {msg}")


    @bot.bridge_command(aliases=["abt"])
    async def about(self, ctx: discord.ext.bridge.context.BridgeApplicationContext) -> None:
        """About Sucrose."""
        await ctx.respond(embed=make_embed(f"# Sucrose\nMade by obfuscated-end-user (横浜).\n\n© 2023-{datetime.now().strftime('%Y')}"), delete_after=30)
        m.print_with_timestamp(f"{c.OKBLUE}@{ctx.author.name}{c.ENDC} in {c.OKGREEN}{ctx.guild.name}{c.ENDC} - ABOUT")


    @commands.has_permissions(administrator=True)
    @bot.bridge_command(aliases=["disconnect", "out", "leave", "dc"])
    async def voice_disconnect(self, ctx: discord.ext.bridge.context.BridgeApplicationContext) -> None:
        """Leaves your voice channel."""
        vc = ctx.guild.voice_client
        if vc:
            await vc.disconnect()
        m.print_with_timestamp(f"{c.OKBLUE}@{ctx.author.name}{c.ENDC} in {c.OKGREEN}{ctx.guild.name}{c.ENDC} - VOICE_DISCONNECT")


def setup(bot):
    bot.add_cog(Basic(bot))
