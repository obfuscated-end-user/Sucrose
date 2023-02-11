# uses pycord
import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from discord.ext import bridge  # for both slash and text-based command support

load_dotenv()
bot = discord.Bot()
TOKEN = os.getenv("TESTING_TOKEN")

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

@bot.slash_command(name="hello", description="Say hello to the bot")
async def hello(ctx):
    await ctx.respond("Hey!")

bot.run(TOKEN)