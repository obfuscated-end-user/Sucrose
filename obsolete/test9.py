# uses pycord
import discord
import os
import wavelink
from dotenv import load_dotenv
from discord.ext import commands, bridge

load_dotenv()
bot = bridge.Bot(intents=discord.Intents.all(), command_prefix="s!")
TOKEN = os.getenv("TESTING_TOKEN")

async def connect_nodes():
    """Connect to our Lavalink nodes."""
    await bot.wait_until_ready()

    await wavelink.NodePool.create_node(
        bot=bot,
        host="127.0.0.1",
        port=2333,
        password="youshallnotpass"
    )

@bot.event
async def on_ready():
    await connect_nodes()
    print(f"{bot.user} is ready and online!")

@bot.event
async def on_wavelink_node_ready(node: wavelink.Node):
    print(f"{node.identifier} is ready.")

@bot.bridge_command(name="hello", description="Say hello to the bot")
async def hello(ctx):
    await ctx.respond("Hey!")

@bot.bridge_command()
async def play(ctx, search: str):
    vc = ctx.voice_client

    if not vc:
        vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)

    if ctx.author.voice.channel.id != vc.channel.id:
        return await ctx.respond("You must be in the same voice channel as the bot.")
    
    song = await wavelink.YouTubeTrack.search(query=search, return_first=True)

    if not song:
        return await ctx.respond("No song found.")
    
    await vc.play(song)
    await ctx.respond(f"Now playing:\"{vc.source.title}\"")

bot.run(TOKEN)