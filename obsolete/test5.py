# uses pycord
# literally used discord.py for 1 fucking day lol

import discord
import os # default module
from dotenv import load_dotenv

load_dotenv() # load all the variables from the env file
bot = discord.Bot()

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

@bot.slash_command(name="hello", description="Say hello to the bot")
async def hello(ctx):
    await ctx.respond("Hey!")

bot.run(os.getenv('TESTING_TOKEN')) # run the bot with the token

""" import discord
import dotenv
import os

bot = discord.Bot()

@bot.slash_command(name="sucrose")
async def sucrose(ctx):
    await ctx.respond("Sucrose did something!")

dotenv.load_dotenv()
bot.run(os.getenv("DISCORD_TOKEN")) """

""" import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

bot = commands.Bot()
TOKEN = str(os.getenv('DISCORD_TOKEN'))

async def on_ready():
    print("Sucrose has connected to Discord!")

@bot.slash_command(name="sucrose")
async def sucrose(ctx):
    await ctx.respond("Sucrose did something!")

bot.run(TOKEN) """