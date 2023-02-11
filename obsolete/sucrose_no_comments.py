import discord
import os
import random
import wavelink
import asyncio
from dotenv import load_dotenv
from discord.ext import bridge, commands

load_dotenv()
bot = bridge.Bot(intents=discord.Intents.all(), command_prefix="s!")
# bot = bridge.Bot(intents=discord.Intents.all(), command_prefix="d!")    # debug
TOKEN = os.getenv("SUCROSE_TOKEN")
# TOKEN = os.getenv("TESTING_TOKEN")  # debug

class Help(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            emby = discord.Embed(description=page)
            await destination.send(embed=emby)
bot.help_command = Help()

async def connect_nodes():
    """Connect to our Lavalink nodes."""
    await bot.wait_until_ready()
    await wavelink.NodePool.create_node(
        bot=bot,
        host="127.0.0.1",
        port=2333,
        password="youshallnotpass"
    )

song_queue = []

@bot.event
async def on_ready():
    global song_queue
    await connect_nodes()
    print(f"{bot.user.name} is ready and online!")
    await bot.change_presence(activity=discord.Game(name="God"))

@bot.event
async def on_wavelink_node_ready(node: wavelink.Node):
    print(f"{node.identifier} is ready.")

@bot.event
async def on_wavelink_track_start(player: wavelink.Player, track: wavelink.Track):
    print(f"music start")
    print(song_queue)

@bot.event
async def on_wavelink_track_end(player: wavelink.Player, track: wavelink.Track, reason):
    print(f"music end\nreason: {reason}")
    global song_queue
    if reason == "STOPPED":
        song_queue = []

@bot.bridge_command()
async def hello(ctx):
    """Sucrose greets you back."""
    hello_quotes = [
        "Hello!",
        "Nice to meet you!",
        "Hi!",
        "sup bro you good"
    ]
    response = random.choice(hello_quotes)
    await ctx.respond(response)
    print(f"{ctx.author.name} ran hello\nmessage: {response} {type(ctx)}")

@bot.bridge_command()
async def say(ctx):
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
    print(f"{ctx.author.name} ran say\nmessage: {response}")

@bot.bridge_command()
async def ping(ctx):
    """Sends the bot's latency, in milliseconds."""
    await ctx.respond(f"Ping: {int(bot.latency * 1000)}ms")
    print(f"{ctx.author.name} ran ping\nmessage: {int(bot.latency * 1000)}ms")

@bot.bridge_command()
async def sum(ctx, num1, num2):
    """Adds two numbers together and says the result in the current channel."""
    sum = float(num1) + float(num2)
    await ctx.respond(f"The sum of {num1} and {num2} is {sum}.")
    print(f"{ctx.author.name} ran ping\nmessage: The sum of {num1} and {num2} is {sum}.")

@bot.bridge_command()
async def echo(ctx, *, message):
    """Parrots back whatever you said."""
    await ctx.respond(message)
    print(f"{ctx.author.name} ran echo\nmessage: {message}")

@bot.bridge_command(aliases=["p", "pl"])
async def play(ctx, *, search: str):
    """Play music from YouTube. URL, YouTube playlist, and Spotify support will be implemented later."""
    vc = ctx.voice_client
    if not vc:
        vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)
    if ctx.author.voice.channel.id != vc.channel.id:
        await ctx.respond("You must be in the same voice channel as the bot.")
    song = await wavelink.YouTubeTrack.search(query=f"\"{search}\"", return_first=True)
    if not song:
        await ctx.respond("No song found.")
    if not song_queue:
        song_queue.append(song)
        guild_id = ctx.message.guild.id
        await vc.play(song_queue[0], replace=False)
        await ctx.respond(f"Now playing: `{song.title}`")
        print(song.title for song in song_queue)
        print("PLAY 1: QUEUE IS EMPTY")
    elif song_queue or vc.is_playing():
        song_queue.append(song)
        await ctx.respond(f"`{song.title}` added to the queue.")
        print(song_queue)
        print("PLAY 2: SONG IS PLAYING")

@bot.bridge_command(aliases=["skip", "slip", "n", "s", "fuck_off"])
async def next(ctx):
    """Plays the next song in the queue."""
    vc = ctx.voice_client
    if not vc:
        vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)
    if ctx.author.voice.channel.id != vc.channel.id:
        await ctx.respond("You must be in the same voice channel as the bot.")
    if len(song_queue) == 1:
        await vc.stop()
        await ctx.respond("Queue is empty.")
    elif len(song_queue) >= 1:
        song_queue.pop(0)
        await vc.play(song_queue[0])
        await ctx.respond(f"Now playing: `{song_queue[0]}`")
        print(song_queue, len(song_queue))
        print("NEXT 1: QUEUE HAS SONGS")
    elif not song_queue:
        await vc.stop()
        await ctx.respond("Queue is empty.")
        print(song_queue)
        print("NEXT 2: QUEUE HAS NO SONGS")

@bot.bridge_command(aliases=["やめろ"])
async def stop(ctx):
    """Stops the current song. Stopped song cannot be resumed afterwards."""
    vc = ctx.voice_client
    global song_queue
    if not vc:
        await ctx.respond("You must be in the same voice channel as me to stop the current song.")
    if not vc.is_playing():
        await ctx.respond("No song is playing.")
    if vc.is_playing():
        await vc.stop()
        await ctx.respond(f"Stopped playing `{song_queue[0]}`.")
        song_queue = []

@bot.bridge_command()
async def pause(ctx):
    """Pauses the current song. Use s!resume to resume playing the song."""
    vc = ctx.voice_client
    if not vc or not vc.is_playing():
        await ctx.respond("I am currently not playing anything.")
    elif vc.is_paused():
        return
    if vc.is_playing():
        await vc.pause()
        await ctx.respond(f"Paused `{song_queue[0]}`. Type `s!resume` to resume playback.")

@bot.bridge_command()
async def resume(ctx):
    """Resumes the current paused song. Does nothing if the current song is playing."""
    vc = ctx.voice_client
    if not vc or not vc.is_playing():
        await ctx.respond("You must be in the same voice channel as the bot to use this command.")
    elif not vc.is_paused():
        return
    await vc.resume()
    await ctx.respond(f"Resuming `{song_queue[0]}`")

@bot.bridge_command(aliases=["q"])
async def queue(ctx):
    """Shows the queue. (TBD)"""
    pass

@bot.bridge_command()
async def shuffle(ctx):
    """Shuffles the queue. (TBD)"""
    pass

bot.run(TOKEN)