# uses pycord
import discord
import os
import random
import time
import wavelink
from discord.ext import bridge, commands
from sucrose import anemo_color
from wavelink.ext import spotify

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

bot = bridge.Bot()

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = []
        self.bot.loop.create_task(self.connect_nodes())

    def format_song_length(self, seconds) -> str:
        """Formats the length of a track in HH:MM:SS."""
        if seconds < 3600: # 3600 seconds is equal to 1 hour
            return time.strftime("%M:%S", time.gmtime(seconds))
        else:
            return time.strftime("%H:%M:%S", time.gmtime(seconds))

    async def connect_nodes(self):
        """Connect to our Lavalink nodes."""
        await self.bot.wait_until_ready()
        await wavelink.NodePool.create_node(
            bot=self.bot,
            host="127.0.0.1",
            port=2333,
            password="youshallnotpass",
            spotify_client=spotify.SpotifyClient(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
        )

    # connects the node to your server when this bot goes online. important for the music shit.
    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        print(f"{node.identifier} is ready.")

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, player: wavelink.Player, track: wavelink.Track):
        # pass
        # ctx = player.ctx
        # player = ctx.voice_client
        # channel = discord.Client.get_channel(self, player.channel)
        # print(player.channel)
        # print()
        # print("on_wavelink_track_start", ctx)
        # vc = ctx.voice_client
        # TBD HOLY SHIT
        channel = player.client.get_channel(channel_id)
        if len(self.song_queue) < 1:
            await channel.send("song queue has nothing")
        elif len(self.song_queue) > 1:
            play_embed = discord.Embed(
                description=f"Now playing: `{self.song_queue[0].title}` **`({self.format_song_length(self.song_queue[0].length)})`**.",
                color=anemo_color
            )
            await channel.send(embed=play_embed, delete_after=15)

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track: wavelink.Track, reason):
        try:
            popped_song = self.song_queue.pop(0)
        except Exception:
            pass
        player = self.bot.voice_clients
        if not player:
            return
        if reason == "STOPPED":
            self.song_queue = []
        if reason == "REPLACED":
            pass
        if reason == "FINISHED":
            if len(self.song_queue) >= 1:
                await player[0].play(self.song_queue[0])
            elif len(self.song_queue) < 1:
                pass

    # MUSIC RELATED COMMANDS
    # have you ever seen a play command this long and fucking stupid?
    @bot.bridge_command(aliases=["p", "pl"])
    async def play(self, ctx, *, search: str):
        """Play a track or playlist."""
        global channel_id
        channel_id = ctx.channel.id
        vc = ctx.voice_client
        if not vc:
            vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        if ctx.author.voice.channel.id != vc.channel.id:
            play_embed = discord.Embed(
                description=f"You must be in the same voice channel as the bot.",
                color=anemo_color
            )
            await ctx.respond(embed=play_embed, delete_after=15)

        # the idea is to check the search query for certain conditions whenever the user tries to play something. if it matches with one of the conditions, do something appropriate.
        # YOUTUBE PLAYLIST OR YOUTUBE MUSIC PLAYLIST
        if "https://www.youtube.com/playlist?list=" in search or "https://music.youtube.com/playlist?list=" in search:
            youtube_playlist = await wavelink.YouTubePlaylist.search(query=search)
            play_embed = discord.Embed(
                description=f"Loading YouTube playlist: `{youtube_playlist}`",
                color=anemo_color
            )
            await ctx.send(embed=play_embed)
            if not youtube_playlist:
                play_embed = discord.Embed(
                    description=f"Playlist `{search}` not found. Try searching for another playlist.",
                    color=anemo_color
                )
                await ctx.respond(embed=play_embed, delete_after=15)
            if len(self.song_queue) == 0:
                temp_playlist = []
                for track in youtube_playlist.tracks:
                    temp_playlist.append(track)
                self.song_queue += temp_playlist
                await vc.resume()
                await vc.play(self.song_queue[0], replace=False)
                play_embed = discord.Embed(
                    description=f"Added {len(temp_playlist)} tracks to the queue.\nNow playing: `{self.song_queue[0].title}` **`({self.format_song_length(self.song_queue[0].length)})`**.",
                    color=anemo_color
                )
                await ctx.respond(embed=play_embed)
                temp_playlist = []
            elif len(self.song_queue) > 0 or vc.is_playing():
                temp_playlist = []
                for track in youtube_playlist.tracks:
                    temp_playlist.append(track)
                self.song_queue += temp_playlist
                play_embed = discord.Embed(
                    description=f"Added {len(temp_playlist)} tracks to the queue.",
                    color=anemo_color
                )
                await ctx.respond(embed=play_embed, delete_after=15)
                temp_playlist = []
        # SPOTIFY
        elif "https://open.spotify.com" in search:
            # single track
            if "track" in search:
                spotify_track = await spotify.SpotifyTrack.search(query=search, return_first=True)
                if len(self.song_queue) == 0:
                    self.song_queue.append(spotify_track)
                    await vc.resume()
                    await vc.play(self.song_queue[0], replace=False) # play it
                    play_embed = discord.Embed(
                        description=f"Now playing: `{self.song_queue[0].title}` **`({self.format_song_length(spotify_track.length)})`**.",
                        color=anemo_color
                    )
                    await ctx.respond(embed=play_embed)
                elif len(self.song_queue) > 0 or vc.is_playing():
                    self.song_queue.append(spotify_track)
                    play_embed = discord.Embed(
                        description=f"`{spotify_track.title}` added to the queue **`({self.format_song_length(spotify_track.length)})`**.",
                        color=anemo_color
                    )
                    await ctx.respond(embed=play_embed, delete_after=15)
            # album or playlist
            elif "album" in search or "playlist" in search:
                play_embed = discord.Embed(
                    description="Loading Spotify playlist/album...",
                    color=anemo_color
                )
                await ctx.send(embed=play_embed)
                spotify_tracks = await spotify.SpotifyTrack.search(query=search, type=spotify.SpotifySearchType.album)
                if not spotify_tracks:
                    play_embed = discord.Embed(
                        description=f"`{search}` not found. Try searching for another playlist or album.",
                        color=anemo_color
                    )
                    await ctx.respond(embed=play_embed, delete_after=15)
                if len(self.song_queue) == 0:
                    temp_playlist = []
                    for track in spotify_tracks:
                        temp_playlist.append(track)
                    self.song_queue += temp_playlist
                    await vc.resume()
                    await vc.play(self.song_queue[0], replace=False)
                    play_embed = discord.Embed(
                        description=f"Added {len(temp_playlist)} tracks to the queue.\nNow playing: `{self.song_queue[0].title}` **`({self.format_song_length(self.song_queue[0].length)})`**.",
                        color=anemo_color
                    )
                    await ctx.respond(embed=play_embed, delete_after=15)
                    temp_playlist = []
                elif len(self.song_queue) > 0 or vc.is_playing():
                    temp_playlist = []
                    for track in spotify_tracks:
                        temp_playlist.append(track)
                    self.song_queue += temp_playlist
                    play_embed = discord.Embed(
                        description=f"Added {len(temp_playlist)} tracks to the queue.",
                        color=anemo_color
                    )
                    await ctx.respond(embed=play_embed, delete_after=15)
                    temp_playlist = []
        # defaults to youtube if everything else fails
        else:
            song = await wavelink.YouTubeTrack.search(query=f"\"{search}\"", return_first=True)
            if not song:
                play_embed = discord.Embed(
                    description=f"No songs found with query `{search}`. Try searching for another song.",
                    color=anemo_color
                )
                await ctx.respond(embed=play_embed, delete_after=15)
            if len(self.song_queue) == 0: # if queue is empty
                self.song_queue.append(song) # put song in queue
                await vc.resume()
                await vc.play(self.song_queue[0], replace=False) # play it
                play_embed = discord.Embed(
                    description=f"Now playing: `{self.song_queue[0].title}` **`({self.format_song_length(song.length)})`**.",
                    color=anemo_color
                )
                await ctx.respond(embed=play_embed)
            elif len(self.song_queue) > 0 or vc.is_playing():
                self.song_queue.append(song)
                play_embed = discord.Embed(
                    description=f"`{song.title}` added to the queue **`({self.format_song_length(song.length)})`**.",
                    color=anemo_color
                )
                await ctx.respond(embed=play_embed, delete_after=15)

    @bot.bridge_command(aliases=["next", "kip", "slip", "n", "s", "fuck_off"])
    async def skip(self, ctx):
        """Skips current song and plays the next song in queue."""
        vc = ctx.voice_client
        if not vc:
            vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        if ctx.author.voice.channel.id != vc.channel.id:
            skip_embed = discord.Embed(
                description="You must be in the same voice channel as the bot.",
                color=anemo_color
            )
            await ctx.respond(embed=skip_embed, delete_after=15)
        if len(self.song_queue) > 1: # if there is at least 1 song in the queue
            await vc.pause() # done for technical reasons. looks fucking stupid though.
            await vc.resume()
            await vc.play(self.song_queue[1], replace=True) # play it
            skip_embed = discord.Embed(
                description=f"Skipped `{self.song_queue[0]}` **`({self.format_song_length(self.song_queue[0].length)})`**. Now playing: `{self.song_queue[1]}` **`({self.format_song_length(self.song_queue[1].length)})`**",
                color=anemo_color
            )
            await ctx.respond(embed=skip_embed, delete_after=15)
        elif len(self.song_queue) == 1: # if queue has only one song
            try:
                song_length = self.format_song_length(self.song_queue[0].length)
                await vc.pause()
                skip_embed = discord.Embed(
                    description=f"Now playing the last song on the queue: `{self.song_queue[0]}` **`({song_length})`**",
                    color=anemo_color
                )
                await ctx.respond(embed=skip_embed, delete_after=15)
                if len(self.song_queue) == 1:
                    await vc.stop()
                    await vc.resume()
                    self.song_queue.pop(0)
            except Exception:
                pass
        elif len(self.song_queue) <= 0:
            await vc.stop()
            skip_embed = discord.Embed(
                description="Queue is empty.",
                color=anemo_color
            )
            await ctx.respond(embed=skip_embed, delete_after=15)

    @bot.bridge_command(aliases=["top", "halt", "shutup", "stfu", "tigil", "hinto", "yamero", "やめろ", "damare", "だまれ"])
    async def stop(self, ctx):
        """Stops the current song. Stopped song cannot be resumed afterwards."""
        vc = ctx.voice_client
        if not vc: # if not in voice channel
            stop_embed = discord.Embed(
                description="You must be in the same voice channel as me to stop the current song.",
                color=anemo_color
            )
            await ctx.respond(embed=stop_embed, delete_after=15)
        if not vc.is_playing():
            stop_embed = discord.Embed(
                description="No song is playing.",
                color=anemo_color
            )
            await ctx.respond(embed=stop_embed, delete_after=15)
        if vc.is_playing():
            song_length = self.format_song_length(self.song_queue[0].length)
            await vc.stop()
            stop_embed = discord.Embed(
                description=f"Stopped playing `{self.song_queue[0]}` **`({song_length})`**.",
                color=anemo_color
            )
            await ctx.respond(embed=stop_embed, delete_after=15)
            self.song_queue = []
            await vc.disconnect()

    @bot.bridge_command(aliases=["ps"])
    async def pause(self, ctx):
        """Pauses the current song. Use s!resume to resume playing the song."""
        vc = ctx.voice_client
        if not vc or not vc.is_playing(): # if not in voice channel
            await vc.pause()
            pause_embed = discord.Embed(
                description="I am currently not playing anything.",
                color=anemo_color
            )
            await ctx.respond(embed=pause_embed, delete_after=15)
        elif vc.is_paused(): # do nothing if song is paused
            return
        if vc.is_playing():
            await vc.pause()
            pause_embed = discord.Embed(
                description=f"Paused `{self.song_queue[0]}`. Type `s!resume` to resume playback.",
                color=anemo_color
            )
            await ctx.respond(embed=pause_embed, delete_after=15)

    @bot.bridge_command(aliases=["res", "rs"])
    async def resume(self, ctx):
        """Resumes the current paused song. Does nothing if the current song is playing."""
        vc = ctx.voice_client
        if not vc or not vc.is_playing():
            resume_embed = discord.Embed(
                description="You must be in the same voice channel as the bot to use this command.",
                color=anemo_color
            )
            await ctx.respond(embed=resume_embed, delete_after=15)
        elif not vc.is_paused(): # do nothing if song is not paused
            return
        elif vc.is_paused():
            await vc.resume()
            resume_embed = discord.Embed(
                description=f"Resuming `{self.song_queue[0]}`.",
                color=anemo_color
            )
            await ctx.respond(embed=resume_embed, delete_after=15)

    @bot.bridge_command(aliases=["q", "list", "playlist"])
    async def queue(self, ctx, page=1):
        """Shows the queue. Can be used with an optional integer parameter to show a specific page."""
        vc = ctx.voice_client
        if not vc:
            queue_embed = discord.Embed(
                description="You must be in a voice channel to use this command.",
                color=anemo_color
            )
            await ctx.respond(embed=queue_embed, delete_after=15)
        if len(self.song_queue) < 1:
            queue_embed = discord.Embed(
                description="There are no songs in the queue.",
                color=anemo_color
            )
            await ctx.respond(embed=queue_embed, delete_after=15)
        else:
            song_queue_chunk_size = 10 # divides the queue into 10 tracks each
            song_queue_chunked  = [self.song_queue[i : i + song_queue_chunk_size] for i in range(0, len(self.song_queue), song_queue_chunk_size)]
            first_track = True # used for the "current track" thing in the queue

            song_queue_length_seconds = 0 # the length of the whole queue
            for song in self.song_queue:
                song_queue_length_seconds += song.length

            queue_embed = discord.Embed(
                title="Music queue",
                description=f"\nType a number to show a specific page. For example, `s!queue 2` will show the second page.\n**Song count:** `{len(self.song_queue)}`, **Total queue duration:** `{self.format_song_length(song_queue_length_seconds)}`\n**Displaying page** `{page}/{len(song_queue_chunked)}`",
                color=anemo_color
            )

            if page < 1 or page > len(song_queue_chunked):
                queue_embed = discord.Embed(
                    description="Invalid page number.",
                    color=anemo_color
                )
                await ctx.respond(embed=queue_embed, delete_after=15)
            else:
                for song in song_queue_chunked[page - 1]:
                    if first_track and page == 1:
                        queue_embed.add_field(name="", value=f"**{self.song_queue.index(song) + 1}.** {song} - **({self.format_song_length(song.length)})** **(CURRENT TRACK)**\n", inline=False)
                        first_track = False
                    else:
                        queue_embed.add_field(name="", value=f"**{self.song_queue.index(song) + 1}.** {song} - **({self.format_song_length(song.length)})**\n", inline=False)
                await ctx.respond(embed=queue_embed, delete_after=30)

    @bot.bridge_command(aliases=["huffle", "mix", "randomize"])
    async def shuffle(self, ctx):
        """Shuffles the queue."""
        vc = ctx.voice_client
        if not vc:
            shuffle_embed = discord.Embed(
                description="You must be in a voice channel to use this command.",
                color=anemo_color
            )
            await ctx.respond(embed=shuffle_embed, delete_after=15)
        temp_queue = self.song_queue[1:]
        for _ in range(1, len(self.song_queue)):
            self.song_queue.pop()
        random.shuffle(temp_queue)
        self.song_queue += temp_queue
        shuffle_embed = discord.Embed(
            description="Shuffled the queue.",
            color=anemo_color
        )
        await ctx.respond(embed=shuffle_embed, delete_after=15)

    @bot.bridge_command(aliases=["now_playing", "current", "info"])
    async def nowplaying(self, ctx):
        """Gives information about the current track."""
        vc = ctx.voice_client
        if not vc:
            now_playing_embed = discord.Embed(
                description="You must be in a voice channel to use this command.",
                color=anemo_color
            )
            await ctx.respond(embed=now_playing_embed, delete_after=15)
        now_playing_embed = discord.Embed(
            title="Now playing",
            description=f"Song title: {self.song_queue[0]}\nLength: {self.format_song_length(self.song_queue[0].length)}",
            color=anemo_color
        )
        await ctx.respond(embed=now_playing_embed, delete_after=15)

    @bot.bridge_command(aliases=["rem", "r", "rm", "pop"])
    async def remove(self, ctx, index: int):
        """Remove a track at the specified index."""
        vc = ctx.voice_client
        if not vc:
            remove_embed = discord.Embed(
                description="You must be in a voice channel to use this command.",
                color=anemo_color
            )
            await ctx.respond(embed=remove_embed, delete_after=15)
        try:
            if index < 1:
                remove_embed = discord.Embed(
                    description="Invalid index.",
                    color=anemo_color
                )
                await ctx.respond(embed=remove_embed, delete_after=15)
            if index == 1: # removing the current track is equivalent to skipping it
                if len(self.song_queue) == 1: # if queue has only one song, might as well stop the entire queue
                    removed_track = self.song_queue.pop(index - 1)
                    remove_embed = discord.Embed(
                        description=f"Removed `{removed_track}` `({self.format_song_length(removed_track.length)})` from the queue.",
                        color=anemo_color
                    )
                    await vc.stop()
                    await ctx.respond(embed=remove_embed, delete_after=15)
                else:
                    await vc.pause()
                    await vc.resume()
                    await vc.play(self.song_queue[1], replace=True)
                    remove_embed = discord.Embed(
                        description=f"Removed `{self.song_queue[0]}` **`({self.format_song_length(self.song_queue[0].length)})`**. Now playing: `{self.song_queue[1]}` **`({self.format_song_length(self.song_queue[1].length)})`**",
                        color=anemo_color
                    )
                    await ctx.respond(embed=remove_embed, delete_after=15)
            else:
                removed_track = self.song_queue.pop(index - 1)
                remove_embed = discord.Embed(
                    description=f"Removed `{removed_track}` `({self.format_song_length(removed_track.length)})` from the queue.",
                    color=anemo_color
                )
                await ctx.respond(embed=remove_embed, delete_after=15)
        except Exception:
            remove_embed = discord.Embed(
                description="Invalid index.",
                color=anemo_color
            )
            await ctx.respond(embed=remove_embed, delete_after=15)

def setup(bot):
    bot.add_cog(Music(bot))