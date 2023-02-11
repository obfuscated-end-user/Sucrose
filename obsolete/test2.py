# uses discord.py
import discord
import os
from dotenv import load_dotenv

import random

load_dotenv()
TOKEN = os.getenv("TESTING_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"{client.user} has connected to Discord!")

    """ for guild in client.guilds:
        if guild.name == GUILD:
            break """
    # guild = discord.utils.find(lambda g: g.name == GUILD, client.guilds)
    guild = discord.utils.get(client.guilds, name=GUILD)
    
    # ignore the fucking warnings, it works
    print(
        f"{client.user} is connected to the following guild:\n{guild.name} (id: {guild.id})"
    )

    members = "\n - ".join([member.name for member in guild.members])
    print(f"Guild Members:\n - {members}")

@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(f"Hi {member.name}, welcome to my Discord server!")

@client.event
async def on_message(message):
    # prevents a potentially recursive case where the bot might call the function again, based on messages sent by itself
    # tl;dr ignores its own mesages
    if message.author == client.user:
        return

    brooklyn_99_quotes = [
        "I\'m the human form of the 💯 emoji.",
        "Bingpot!",
        (
            "Cool. Cool cool cool cool cool cool cool, "
            "no doubt no doubt no doubt no doubt."
        ),
    ]
    
    if message.content == "99!":
        response = random.choice(brooklyn_99_quotes)
        await message.channel.send(response)
    elif message.content == "Hello Sucrose!":
        await message.channel.send(f"Hello, {message.author.name}!")

    # error handling? shitty way to this btw
    elif message.content == "raise-exception":
        raise discord.DiscordException

# better error handler
@client.event
async def on_error(event, *args, **kwargs):
    with open("err.log", "a") as f:
        if event == "on_message":
            f.write(f"Unhandled message: {args[0]}\n")
        else:
            raise


client.run(TOKEN)

# As you’ve seen already, discord.py is an event-driven system.