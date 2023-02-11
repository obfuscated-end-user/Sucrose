# uses pycord
# main bot
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

# customizing help
class Help(commands.MinimalHelpCommand):
    async def send_pages(self):
        # the channel used to send this help command
        destination = self.get_destination()
        # for each page in this help command
        for page in self.paginator.pages:
            # make an embed
            emby = discord.Embed(description=page)
            # and send the embed to the current destination
            await destination.send(embed=emby)
# override the default help command
bot.help_command = Help()

""""
TO-DO:
make this bot play music, support both youtube and spotify urls
distinguish offline from invisibility status, if not impossible

NOTE:
there's a tendency that discord syncs the slash commands slow as shit and are not recognized immediately, but their command_prefix counterparts work fine.
"""

async def connect_nodes():
    """Connect to our Lavalink nodes."""
    await bot.wait_until_ready() # wait until the bot is ready
    # creates a node from that server you just set up
    await wavelink.NodePool.create_node(
        bot=bot,
        # these three should be the same as the one on application.yml file
        host="127.0.0.1",
        port=2333,
        password="youshallnotpass"
    )

# for checking the fucking music state
song_queue = []

@bot.event
async def on_ready():
    global song_queue
    await connect_nodes()
    # song_queue = []
    print(f"{bot.user.name} is ready and online!")
    # change Sucrose's status. for now, it's currently impossible to have a status just like a normal user would. for bots, you need to set it as an activity (listening, playing, streaming, etc.).
    await bot.change_presence(activity=discord.Game(name="God"))

# connects the node to your server when this bot goes online. important for the music shit.
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
    vc: player = ctx.voice_client
    if not vc:
        return
        # vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)
    global song_queue, next_song
    if reason == "STOPPED":
        song_queue = []
    if reason == "FINISHED":
        if len(song_queue) <= 1:
            next_song = False
        if len(song_queue) >= 2:
            next_song = True
            await vc.play(song_queue[0])
            if len(song_queue) <= 1:
                next_song = False
    if len(song_queue):
        song_queue.pop(0)
        # del song_queue[0]
        print(song_queue)
    else:
        return

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

@bot.bridge_command(aliases=["latency"])
async def ping(ctx):
    """Sends the bot's latency, in milliseconds."""
    await ctx.respond(f"Ping: {int(bot.latency * 1000)}ms")
    print(f"{ctx.author.name} ran ping\nmessage: {int(bot.latency * 1000)}ms")

# used for testing commands that take arguments
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

# MUSIC RELATED COMMANDS
"""
TO-DO:
play
stop
pause
resume
next/skip
queue, to show the queue
remove index
leave voice channel after set interval
support playlists
support spotify
IMPORTANT: catch exceptions holy fucking shit
    unavailable videos
    region locked spotify songs

bugs:
1. if one plays a song and stops it, and tries to play another song, it will get added to the queue instead.
2. may be related to the bug above but s!play song shouldn't replace the current song.
3. if the song ends, it should play the next song in the queue.
4. after a song finishes playing, trying to play another song will not play it but only add it to the queue.

DEBUG
normal flow (without skips):
play x4 👌
with other commands:
play - play - next - pause - resume - pause - next - resume
play - play - next - play
    - appends song 1 to queue (and plays it)
    - appends song 2 to queue
    - plays 2nd song (but queue is empty)
    - 3rd song replaces the 2nd song (with queue still empty)
play - play - play - play - next - next
    - play 4 songs
    - next song is correct (second song)
    - next song is wrong, last song is played instead (third song never gets played)
play - stop - play 👌
play - play - pause - next - play
"""

def queued(ctx):
    if len(song_queue) > 0:
        voice = ctx.guild.voice_client
        audio = song_queue.pop(0)
        voice.play(audio, after=lambda x=None: queued(ctx))

@bot.bridge_command(aliases=["p", "pl"])
async def play(ctx, *, search: str):
    """Play music from YouTube. URL, YouTube playlist, and Spotify support will be implemented later."""
    # the voice client
    vc = ctx.voice_client
    # check if the bot is not in a voice channel
    if not vc:
        # connect to the same voice channel as the caller
        vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)
    # if someone tries to play something but they're on a different channel
    if ctx.author.voice.channel.id != vc.channel.id:
        await ctx.respond("You must be in the same voice channel as the bot.")
    # search for the song
    song = await wavelink.YouTubeTrack.search(query=f"\"{search}\"", return_first=True)
    # if song is not found, return an error message
    if not song:
        await ctx.respond("No song found.")
    # play the song and return the title of the song on the current channel. "title" here means the title of the source youtube video.
    if not song_queue: # if queue is empty
        song_queue.append(song) # put song in queue
        # , after=lambda x=None: queued(ctx, guild_id)
        # , after=lambda x=None: queued(ctx)
        await vc.play(song_queue[0], replace=False) # play it
        await ctx.respond(f"Now playing: `{song.title}`")
        # print(f"{ctx.author.name} ran play\nsong: {song.title}\nsong_queue: {song_queue}, song_queue[0]: {song_queue[0]}")
        print(song.title for song in song_queue)
        print("PLAY 1: QUEUE IS EMPTY")
    elif song_queue or vc.is_playing():
    # if vc.is_playing():
        song_queue.append(song) # put song in queue, but don't play it yet
        await ctx.respond(f"`{song.title}` added to the queue.")
        # print(f"{ctx.author.name} ran play\nsong: {song.title}\nsong_queue: {song_queue}, song_queue[0]: {song_queue[0]}\nsong length: {song_queue[0].length}")
        print(song_queue)
        print("PLAY 2: SONG IS PLAYING")
    """
    expected behavior:
    s!play song:
        if queue is empty:
            append song and play it
        else if queue is not empty:
            append song to queue
            wait for an s!next or wait for current song to end

    add later:
    s!play youtube/spotify playlist
        if queue is empty:
            loop through all the songs in the playlist and append them in the queue

    test links
    youtube
        # short songs
            s!play 0SqhSfx2TkE # family reunion
            s!play C6bCWMdarZI # the ballad of wilhelm fink
            s!play 7vwtjFenq-Q # give up
            s!play 3CV4yrXm9qI # lover's oath
        # normal songs
            s!play DF1W3DrXOME # blight of river-systems
        # long songs
            s!play 5dZy-TL4bfs
            s!play F5b3laSpOKQ
    spotify
        # short songs
            -
        # normal songs
            -
        # long songs
            s!play https://open.spotify.com/track/4IuVWyD0fgFvX6V5CL0mHC?si=f39651d6345241aa
    """

@bot.bridge_command(aliases=["next", "slip", "n", "s", "fuck_off"])
async def skip(ctx):
    """Skips current song and plays the next song in queue."""
    # usual shit
    vc = ctx.voice_client
    if not vc:
        vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)
    if ctx.author.voice.channel.id != vc.channel.id:
        await ctx.respond("You must be in the same voice channel as the bot.")
    if len(song_queue) == 1:
        await vc.stop()
        await ctx.respond("Queue is empty.")
    elif len(song_queue) >= 1: # if there is a song in the queue
        # await vc.stop() # stop it
        song_queue.pop(0) # pop the first item on the list
        await vc.play(song_queue[0]) # play it
        await ctx.respond(f"Now playing: `{song_queue[0]}`")
        # print(f"{ctx.author.name} ran next\nsong: {song}\nsong_queue: {song_queue}, song_queue[0]: {song_queue[0]}")
        print(song_queue, len(song_queue))
        print("NEXT 1: QUEUE HAS SONGS")
    elif not song_queue:
        await vc.stop()
        await ctx.respond("Queue is empty.")
        # print(f"{ctx.author.name} ran next but queue is empty\nsong_queue: {song_queue}, song_queue[0]: {song_queue[0]}\nsong length: {song_queue[0].length}")
        print(song_queue)
        print("NEXT 2: QUEUE HAS NO SONGS")
    """
    expected behavior:
    s!next:
        if queue is empty:
            skip the song and stop playing
        else if queue is not empty:
            stop the current song_queue[0] (current song)
            pop song_queue[0]
            play the next song in the queue (song after song_queue[0])
    """

@bot.bridge_command(aliases=["やめろ"])
async def stop(ctx):
    """Stops the current song. Stopped song cannot be resumed afterwards."""
    vc = ctx.voice_client
    global song_queue
    if not vc: # if not in voice channel
        # print(f"{ctx.author.name} ran stop but they're not in a voice channel")
        await ctx.respond("You must be in the same voice channel as me to stop the current song.")
    if not vc.is_playing(): # if song is not playing
        # print(f"{ctx.author.name} ran stop but no song is playing.")
        await ctx.respond("No song is playing.")
    if vc.is_playing(): # if song is playing, stop
        await vc.stop()
        await ctx.respond(f"Stopped playing `{song_queue[0]}`.")
        song_queue = []
        # print(f"{ctx.author.name} ran stop\nsong stopped: {song_queue[0]}\nsong state: {vc.is_playing()}")
    """
    expected behavior:
    s!stop:
        stop the current song
        empty the queue
    ^ do this regardless of the state of the queue (empty or not)
    """

@bot.bridge_command(aliases=["ps"])
async def pause(ctx):
    """Pauses the current song. Use s!resume to resume playing the song."""
    vc = ctx.voice_client
    if not vc or not vc.is_playing(): # if not in voice channel
        # print(f"{ctx.author.name} tried to run pause but did not pause anything.")
        await ctx.respond("I am currently not playing anything.")
    elif vc.is_paused(): # if song is paused
        return
    if vc.is_playing():
        await vc.pause()
        await ctx.respond(f"Paused `{song_queue[0]}`. Type `s!resume` to resume playback.")
    # print(f"{ctx.author.name} ran stop\npaused song: {song_queue[0]}\nsong state: {vc.is_playing()}")
    """
    expected behavior:
    s!pause:
    if user is not in a voice channel or not in the same voice channel as the bot:
        do nothing
    if user is in a voice channel:
        if a song is playing:
            pause the song
        else if song is paused:
            do nothing
        else if nothing is playing:
            do nothing
    """

@bot.bridge_command()
async def resume(ctx):
    """Resumes the current paused song. Does nothing if the current song is playing."""
    vc = ctx.voice_client
    if not vc or not vc.is_playing(): # if not in voice channel
        # print(f"{ctx.author.name} ran resume but they're not in a voice channel")
        await ctx.respond("You must be in the same voice channel as the bot to use this command.")
    elif not vc.is_paused(): # if song is paused, resume
        # print(f"{ctx.author.name} ran resume\nsong resumed: {song_queue[0]}\nsong state: {vc.is_playing()}")
        return
    await vc.resume()
    await ctx.respond(f"Resuming `{song_queue[0]}`")

    """
    expected behavior:
    s!resume:
    if user is not in a voice channel or not in the same voice channel as the bot:
        do nothing
    if user is in a voice channel:
        if a song is playing:
            do nothing
        else if song is paused:
            resume the song
        else if nothing is playing:
            do nothing
    """

@bot.bridge_command(aliases=["q"])
async def queue(ctx):
    """Shows the queue. (TBD)"""
    pass

@bot.bridge_command()
async def shuffle(ctx):
    """Shuffles the queue. (TBD)"""
    pass

bot.run(TOKEN)