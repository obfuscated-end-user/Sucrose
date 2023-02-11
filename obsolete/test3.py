# uses discord.py
import os
import random
import discord
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv("TESTING_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")

@bot.command(name="hello", help="Greets the user who called this command.")
# ctx is the context, which is mostly the message and its properties and shit
async def say_hello(ctx):
    hello_quotes = [
        "Hello!",
        "Nice to meet you!",
        "Anemo test 6308!",
        "はじめまして、スクロースと申します。えっと。。。あたし、頑張る！"
    ]
    response = random.choice(hello_quotes)
    await ctx.send(response)

@bot.command(name="say", help="Says something random.")
async def say_something(ctx):
    responses = [
        "Adsorption test.",
        "死ね！",
        f"{ctx.author.name} is a faggot!"
    ]
    response = random.choice(responses)
    await ctx.send(response)
    print(discord.utils.get(ctx.guild.channels))

@bot.command(name='roll_dice', help='Simulates rolling dice.')
async def roll(ctx, number_of_dice: int, number_of_sides: int):
    # THE EXTRA PARAMETERS NEXT TO ctx ARE ALSO NEEDED ON THE DISCORD MESSAGE ITSELF
    # example: !roll_dice 3 6
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(', '.join(dice))

@bot.command(name="create_channel", help="Creates a new channel with a specified name.")
@commands.has_role("admin")  # checks if the caller has the role "admin"
async def create_channel(ctx, channel_name="new-channel"):
    # the server
    guild = ctx.guild
    # the channel you want to create
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    # if the channel does not exist, create it
    if not existing_channel:
        print(f"Creating a new channel: {channel_name}")
        await guild.create_text_channel(channel_name)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send("You do not have the correct role for this shit.")

bot.run(TOKEN)