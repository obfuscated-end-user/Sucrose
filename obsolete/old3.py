# uses pycord
# main bot
import discord
import os
import random
import wavelink
from dotenv import load_dotenv
from discord.ext import bridge, commands

load_dotenv()
bot = bridge.Bot()

# customizing help
# FIX LATER. CURRENTLY NOT VISIBLE WHEN CALLED.
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

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = []
        self.next_song = True
        self.bot.loop.create_task(self.connect_nodes())

    async def connect_nodes(self):
        """Connect to our Lavalink nodes."""
        await self.bot.wait_until_ready() # wait until the bot is ready
        # creates a node from that server you just set up
        await wavelink.NodePool.create_node(
            bot=self.bot, # THE self HERE IS FUCKING IMPORTANT
            # these three should be the same as the one on application.yml file
            host="127.0.0.1",
            port=2333,
            password="youshallnotpass"
        )

    """"
    TO-DO:
    make this bot play music, support both youtube and spotify urls
    distinguish offline from invisibility status, if not impossible

    NOTE:
    there's a tendency that discord syncs the slash commands slow as shit and are not recognized immediately, but their command_prefix counterparts work fine.
    """

    # connects the node to your server when this bot goes online. important for the music shit.
    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        print(f"{node.identifier} is ready.")

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, player: wavelink.Player, track: wavelink.Track):
        print(f"music start")
        print("TRACK START",[song.title for song in self.song_queue], len(self.song_queue))

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track: wavelink.Track, reason):
        print(f"music end\nreason: {reason}")
        try:
            popped_song = self.song_queue.pop(0) # SKIPPING IS CONSIDERED TRACK END
        except Exception:
            pass
        # ctx = player.ctx
        player = self.bot.voice_clients
        song_queue_length = len(self.song_queue)
        if not player:
            return
            # vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        if reason == "STOPPED": # THIS ALSO GETS 
            self.song_queue = []
            print("STOPPED", [song.title for song in self.song_queue], song_queue_length)
        if reason == "REPLACED":
            print("REPLACED", [song.title for song in self.song_queue], song_queue_length)
        if reason == "FINISHED":
            if len(self.song_queue) >= 1:
                # "SONG QUEUE LESS THAN OR EQUAL TO 1 (FIRST)",
                print("FINISHED, queue >= 1", [song.title for song in self.song_queue], song_queue_length)
                await player[0].play(self.song_queue[0])
                self.next_song = False
            elif len(self.song_queue) < 1:
                print("FINISHED, queue < 1", [song.title for song in self.song_queue], song_queue_length)
                """ await player[0].play(self.song_queue[0])
                self.song_queue.pop(0) """
                # await player[0].stop()
            """ if len(self.song_queue) >= 2:
                print("SONG QUEUE GREATER THAN OR EQUAL TO 2", song_queue_length)
                self.next_song = True
                await player[0].play(self.song_queue[0])
                if len(self.song_queue) <= 1:
                    print("SONG QUEUE LESS THAN OR EQUAL TO 1 (SECOND)", song_queue_length)
                    self.next_song = False """
        """ if len(self.song_queue):
            self.song_queue.pop(0)
            # del song_queue[0]
            print(self.song_queue)
        else:
            return """

    @bot.bridge_command()
    async def hello(self, ctx):
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
    async def say(self, ctx):
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
    async def ping(self, ctx):
        """Sends the bot's latency, in milliseconds."""
        await ctx.respond(f"Ping: {int(self.bot.latency * 1000)}ms")
        print(f"{ctx.author.name} ran ping\nmessage: {int(self.bot.latency * 1000)}ms")

    # used for testing commands that take arguments
    @bot.bridge_command()
    async def sum(self, ctx, num1, num2):
        """Adds two numbers together and says the result in the current channel."""
        sum = float(num1) + float(num2)
        await ctx.respond(f"The sum of {num1} and {num2} is {sum}.")
        print(f"{ctx.author.name} ran ping\nmessage: The sum of {num1} and {num2} is {sum}.")

    @bot.bridge_command()
    async def echo(self, ctx, *, message):
        """Parrots back whatever you said."""
        await ctx.respond(message)
        print(f"{ctx.author.name} ran echo\nmessage: {message}")

    @bot.bridge_command(aliases=["connect", "enter", "join"])
    async def voice_connect(self, ctx):
        # """Joins your voice channel."""
        vc = ctx.guild.voice_client
        if not vc:
            # print("cunt ass")
            await vc.connect()
        
    @bot.bridge_command(aliases=["disconnect", "out", "leave", "dc"])
    async def voice_disconnect(self, ctx):
        """Leaves your voice channel."""
        vc = ctx.guild.voice_client
        # await ctx.voice_clients.disconnect()
        if vc:
            # print("i did something")
            await vc.disconnect()

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
    5. the first two songs works fine when played from the queue, the 3rd, 5th, 7th... are skipped over and the 4th, 6th, 8th... songs are played instead.

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

    @bot.bridge_command(aliases=["p", "pl"])
    async def play(self, ctx, *, search: str):
        """Play music from YouTube. URL, YouTube playlist, and Spotify support will be implemented later."""
        print("PLAY!")
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
        if len(self.song_queue) == 0: # if queue is empty
            self.song_queue.append(song) # put song in queue
            await vc.resume()
            await vc.play(self.song_queue[0], replace=False) # play it
            await ctx.respond(f"Now playing: `{song.title}`")
            # print(f"{ctx.author.name} ran play\nsong: {song.title}\nsong_queue: {song_queue}, song_queue[0]: {song_queue[0]}")
            print("PLAY, queue == 0",[song.title for song in self.song_queue], len(self.song_queue))
        elif len(self.song_queue) > 0 or vc.is_playing():
        # if vc.is_playing():
            self.song_queue.append(song) # put song in queue, but don't play it yet
            await ctx.respond(f"`{song.title}` added to the queue.")
            # print(f"{ctx.author.name} ran play\nsong: {song.title}\nsong_queue: {song_queue}, song_queue[0]: {song_queue[0]}\nsong length: {song_queue[0].length}")
            print("PLAY, playing something",[song.title for song in self.song_queue], len(self.song_queue))
            # print("PLAY 2: SONG IS PLAYING")

    @bot.bridge_command(aliases=["next", "slip", "n", "s", "fuck_off"])
    async def skip(self, ctx):
        """Skips current song and plays the next song in queue."""
        print("SKIPPED!")
        # usual shit
        vc = ctx.voice_client
        if not vc:
            vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        if ctx.author.voice.channel.id != vc.channel.id:
            await ctx.respond("You must be in the same voice channel as the bot.")
        if len(self.song_queue) > 1: # if there is a song in the queue
            # await vc.stop() # stop it
            # popped_song = self.song_queue.pop(0)
            await vc.pause() # stop it
            await vc.play(self.song_queue[1], replace=True) # play it
            await ctx.respond(f"Now playing: `{self.song_queue[1]}`")
            # print(f"{ctx.author.name} ran next\nsong: {song}\nsong_queue: {song_queue}, song_queue[0]: {song_queue[0]}")
            print("SKIP, queue > 1",[song.title for song in self.song_queue], len(self.song_queue))
            popped_song = self.song_queue.pop(0)
            # print("NEXT 1: QUEUE HAS SONGS")
        if len(self.song_queue) == 1:
            # await vc.stop()
            # await vc.pause() # stop it
            try:
                await vc.stop()
                await vc.play(self.song_queue[0], replace=True) # play it
                await ctx.respond(f"Playback stopped since there are no more songs left in the queue.")
                popped_song = self.song_queue.pop(0) # pop the first item on the list
            except Exception:
                pass
            # await ctx.respond(f"2Now playing: `{self.song_queue[0]}`")
            # await ctx.respond("Queue is empty.")
            print("SKIP, queue == 1",[song.title for song in self.song_queue], len(self.song_queue))
        elif not self.song_queue:
            await vc.stop()
            await ctx.respond("Queue is empty.")
            # print(f"{ctx.author.name} ran next but queue is empty\nsong_queue: {song_queue}, song_queue[0]: {song_queue[0]}\nsong length: {song_queue[0].length}")
            print("SKIP, queue == 0",[song.title for song in self.song_queue], len(self.song_queue))
            # print("NEXT 2: QUEUE HAS NO SONGS")

    @bot.bridge_command(aliases=["やめろ"])
    async def stop(self, ctx):
        """Stops the current song. Stopped song cannot be resumed afterwards."""
        vc = ctx.voice_client
        if not vc: # if not in voice channel
            # print(f"{ctx.author.name} ran stop but they're not in a voice channel")
            await ctx.respond("You must be in the same voice channel as me to stop the current song.")
        if not vc.is_playing(): # if song is not playing
            # print(f"{ctx.author.name} ran stop but no song is playing.")
            await ctx.respond("No song is playing.")
        if vc.is_playing(): # if song is playing, stop
            await vc.stop()
            await ctx.respond(f"Stopped playing `{self.song_queue[0]}`.")
            self.song_queue = []
            # print(f"{ctx.author.name} ran stop\nsong stopped: {song_queue[0]}\nsong state: {vc.is_playing()}")

    @bot.bridge_command(aliases=["ps"])
    async def pause(self, ctx):
        """Pauses the current song. Use s!resume to resume playing the song."""
        vc = ctx.voice_client
        if not vc or not vc.is_playing(): # if not in voice channel
            # print(f"{ctx.author.name} tried to run pause but did not pause anything.")
            print("NOT VC NOR IS PLAYING ANYTHING",[song.title for song in self.song_queue], len(self.song_queue))
            await ctx.respond("I am currently not playing anything.")
        elif vc.is_paused(): # if song is paused
            print("VC IS PAUSED",[song.title for song in self.song_queue], len(self.song_queue))
            return
        if vc.is_playing():
            print("VC IS PLAYING",[song.title for song in self.song_queue], len(self.song_queue))
            await vc.pause()
            await ctx.respond(f"Paused `{self.song_queue[0]}`. Type `s!resume` to resume playback.")
        # print(f"{ctx.author.name} ran stop\npaused song: {song_queue[0]}\nsong state: {vc.is_playing()}")

    @bot.bridge_command()
    async def resume(self, ctx):
        """Resumes the current paused song. Does nothing if the current song is playing."""
        vc = ctx.voice_client
        if not vc or not vc.is_playing(): # if not in voice channel
            # print(f"{ctx.author.name} ran resume but they're not in a voice channel")
            await ctx.respond("You must be in the same voice channel as the bot to use this command.")
            print("NOT VC NOR IS PLAYING ANYTHING",[song.title for song in self.song_queue], len(self.song_queue))
        elif not vc.is_paused(): # if song is paused, resume
            # print(f"{ctx.author.name} ran resume\nsong resumed: {song_queue[0]}\nsong state: {vc.is_playing()}")
            print("NOT PAUSED",[song.title for song in self.song_queue], len(self.song_queue))
            return
        await vc.resume()
        await ctx.respond(f"Resuming `{self.song_queue[0]}`")

    @bot.bridge_command(aliases=["q"])
    async def queue(self, ctx):
        """Shows the queue. (TBD)"""
        pass

    @bot.bridge_command()
    async def shuffle(self, ctx):
        """Shuffles the queue. (TBD)"""
        pass

def setup(bot):
    bot.add_cog(Music(bot))
