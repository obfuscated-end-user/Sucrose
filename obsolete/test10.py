# 

import discord
import os
import wavelink
from dotenv import load_dotenv
from discord.ext import bridge

load_dotenv()
bot = bridge.Bot(intents=discord.Intents.all(), command_prefix="s!")
TOKEN = os.getenv("TESTING_TOKEN")

@bot.event
async def on_ready():
    await connect_nodes() # connect to the server

@bot.event
async def on_wavelink_node_ready(node: wavelink.Node):
    print(f"{node.identifier} is ready.") # print a message

async def connect_nodes():
    """Connect to our Lavalink nodes."""
    await bot.wait_until_ready() # wait until the bot is ready
    await wavelink.NodePool.create_node(
        bot=bot,
        host='127.0.0.1',
        port=2333,
        password='youshallnotpass'
    )

song_queue = []
@bot.bridge_command(aliases=["p", "pl"])
async def play(ctx, *, search: str):
    vc = ctx.voice_client # define our voice client

    if not vc: # check if the bot is not in a voice channel
        vc = await ctx.author.voice.channel.connect(cls=wavelink.Player) # connect to the voice channel

    if ctx.author.voice.channel.id != vc.channel.id: # check if the bot is not in the voice channel
        return await ctx.respond("You must be in the same voice channel as the bot.") # return an error message

    # song = await wavelink.YouTubeTrack.search(query=search, return_first=True) # search for the song
    youtube_playlist = await wavelink.YouTubePlaylist.search(query=search)
    print(youtube_playlist)

    if not youtube_playlist: # check if the song is not found
        return await ctx.respond("No song found.") # return an error message

    for track in youtube_playlist.tracks:
        song_queue.append(track)
    print(song_queue)

    await vc.play(song_queue[1]) # play the song
    await ctx.respond(f"Now playing: `{vc.source.title}`")

bot.run(TOKEN)