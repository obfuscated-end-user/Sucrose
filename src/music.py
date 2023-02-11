# uses pycord
import random
import wavelink
import time
import os
from dotenv import load_dotenv
from discord.ext import bridge, commands
from wavelink.ext import spotify

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

load_dotenv()
bot = bridge.Bot()

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = []
        self.bot.loop.create_task(self.connect_nodes())

    def format_song_length(self, seconds):
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
        pass

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
        vc = ctx.voice_client
        if not vc:
            vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        if ctx.author.voice.channel.id != vc.channel.id:
            await ctx.respond("You must be in the same voice channel as the bot.")

        # the idea is to check the search query for certain conditions when the user tries to play something. if it matches with one of the conditions, do something appropriate.
        # YOUTUBE PLAYLIST OR YOUTUBE MUSIC PLAYLIST
        # bootleg ass regex
        if "https://www.youtube.com/playlist?list=" in search or "https://music.youtube.com/playlist?list=" in search:
            youtube_playlist = await wavelink.YouTubePlaylist.search(query=search)
            await ctx.respond(f"Loading YouTube playlist: `{youtube_playlist}`")
            if not youtube_playlist:
                await ctx.respond(f"Playlist `{search}` not found. Try searching for another playlist.")
            if len(self.song_queue) == 0:
                temp_playlist = []
                for track in youtube_playlist.tracks:
                    temp_playlist.append(track)
                self.song_queue += temp_playlist
                await vc.resume()
                await vc.play(self.song_queue[0], replace=False)
                await ctx.respond(f"Added {len(temp_playlist)} tracks to the queue.")
                await ctx.respond(f"Now playing: `{self.song_queue[0].title}` **`({self.format_song_length(self.song_queue[0].length)})`**.")
                temp_playlist = []
            elif len(self.song_queue) > 0 or vc.is_playing():
                temp_playlist = []
                for track in youtube_playlist.tracks:
                    temp_playlist.append(track)
                self.song_queue += temp_playlist
                await ctx.respond(f"Added {len(temp_playlist)} tracks to the queue.")
                temp_playlist = []
        # SPOTIFY
        elif "https://open.spotify.com/" in search:
            # single track
            if "track" in search:
                spotify_track = await spotify.SpotifyTrack.search(query=search, return_first=True)
                if len(self.song_queue) == 0:
                    self.song_queue.append(spotify_track)
                    await vc.resume()
                    await vc.play(self.song_queue[0], replace=False) # play it
                    await ctx.respond(f"Now playing: `{self.song_queue[0].title}` **`({self.format_song_length(spotify_track.length)})`**.")
                elif len(self.song_queue) > 0 or vc.is_playing():
                    self.song_queue.append(spotify_track)
                    await ctx.respond(f"`{spotify_track.title}` added to the queue **`({self.format_song_length(spotify_track.length)})`**.")
            # album or playlist
            elif "album" in search or "playlist" in search:
                await ctx.send(f"Loading Spotify playlist/album...")
                spotify_tracks = await spotify.SpotifyTrack.search(query=search, type=spotify.SpotifySearchType.album)
                if not spotify_tracks:
                    await ctx.respond(f"`{search}` not found. Try searching for another playlist or album.")
                if len(self.song_queue) == 0:
                    temp_playlist = []
                    for track in spotify_tracks:
                        temp_playlist.append(track)
                    self.song_queue += temp_playlist
                    await vc.resume()
                    await vc.play(self.song_queue[0], replace=False)
                    await ctx.respond(f"Added {len(temp_playlist)} tracks to the queue.")
                    await ctx.respond(f"Now playing: `{self.song_queue[0].title}` **`({self.format_song_length(self.song_queue[0].length)})`**.")
                    temp_playlist = []
                elif len(self.song_queue) > 0 or vc.is_playing():
                    temp_playlist = []
                    for track in spotify_tracks:
                        temp_playlist.append(track)
                    self.song_queue += temp_playlist
                    await ctx.respond(f"Added {len(temp_playlist)} tracks to the queue.")
                    temp_playlist = []
        # defaults to youtube if everything else fails
        else:
            song = await wavelink.YouTubeTrack.search(query=f"\"{search}\"", return_first=True)
            if not song:
                await ctx.respond(f"No songs found with query `{search}`. Try searching for another song.")
            if len(self.song_queue) == 0: # if queue is empty
                self.song_queue.append(song) # put song in queue
                await vc.resume()
                await vc.play(self.song_queue[0], replace=False) # play it
                await ctx.respond(f"Now playing: `{self.song_queue[0].title}` **`({self.format_song_length(song.length)})`**.")
            elif len(self.song_queue) > 0 or vc.is_playing():
                self.song_queue.append(song)
                await ctx.respond(f"`{song.title}` added to the queue **`({self.format_song_length(song.length)})`**.")

    @bot.bridge_command(aliases=["next", "kip", "slip", "n", "s", "fuck_off"])
    async def skip(self, ctx):
        """Skips current song and plays the next song in queue."""
        vc = ctx.voice_client
        if not vc:
            vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        if ctx.author.voice.channel.id != vc.channel.id:
            await ctx.respond("You must be in the same voice channel as the bot.")
        if len(self.song_queue) > 1: # if there is at least 1 song in the queue
            await vc.pause() # done for technical reasons. looks fucking stupid though.
            await vc.resume()
            await vc.play(self.song_queue[1], replace=True) # play it
            await ctx.respond(f"Skipped `{self.song_queue[0]}` **`({self.format_song_length(self.song_queue[0].length)})`**. Now playing: `{self.song_queue[1]}` **`({self.format_song_length(self.song_queue[1].length)})`**")
        elif len(self.song_queue) == 1: # if queue has only one song
            try:
                song_length = self.format_song_length(self.song_queue[0].length)
                await vc.pause()
                await vc.play(self.song_queue[0], replace=True)
                await ctx.respond(f"Now playing the last song on the queue: `{self.song_queue[0]}` **`({song_length})`**")
                if len(self.song_queue) == 1:
                    await vc.stop()
                    await vc.resume()
                    self.song_queue.pop(0)
            except Exception:
                pass
        elif len(self.song_queue) <= 0:
            await vc.stop()
            await ctx.respond("Queue is empty.")

    @bot.bridge_command(aliases=["top", "halt", "shutup", "stfu", "tigil", "hinto", "yamero", "やめろ"])
    async def stop(self, ctx):
        """Stops the current song. Stopped song cannot be resumed afterwards."""
        vc = ctx.voice_client
        if not vc: # if not in voice channel
            await ctx.respond("You must be in the same voice channel as me to stop the current song.")
        if not vc.is_playing():
            await ctx.respond("No song is playing.")
        if vc.is_playing():
            song_length = self.format_song_length(self.song_queue[0].length)
            await vc.stop()
            await ctx.respond(f"Stopped playing `{self.song_queue[0]}` **`({song_length})`**.")
            self.song_queue = []
            await vc.disconnect()

    @bot.bridge_command(aliases=["ps"])
    async def pause(self, ctx):
        """Pauses the current song. Use s!resume to resume playing the song."""
        vc = ctx.voice_client
        if not vc or not vc.is_playing(): # if not in voice channel
            await ctx.respond("I am currently not playing anything.")
        elif vc.is_paused(): # do nothing if song is paused
            return
        if vc.is_playing():
            await vc.pause()
            await ctx.respond(f"Paused `{self.song_queue[0]}`. Type `s!resume` to resume playback.")

    @bot.bridge_command(aliases=["res", "rs"])
    async def resume(self, ctx):
        """Resumes the current paused song. Does nothing if the current song is playing."""
        vc = ctx.voice_client
        if not vc or not vc.is_playing():
            await ctx.respond("You must be in the same voice channel as the bot to use this command.")
        elif not vc.is_paused(): # do nothing if song is not paused
            return
        elif vc.is_paused():
            await vc.resume()
            await ctx.respond(f"Resuming `{self.song_queue[0]}`.")

    @bot.bridge_command(aliases=["q", "list", "playlist"])
    async def queue(self, ctx, page=1):
        """Shows the queue. Can be used with an optional integer parameter to show a specific page."""
        vc = ctx.voice_client
        if not vc:
            await ctx.respond("You must be in a voice channel to use this command.")
        if len(self.song_queue) < 1:
            await ctx.respond("There are no songs in the queue.")
        else:
            song_queue_chunk_size = 10 # divides the queue into 10 tracks each
            song_queue_chunked  = [self.song_queue[i : i + song_queue_chunk_size] for i in range(0, len(self.song_queue), song_queue_chunk_size)]
            first_track = True # used for the "current track" thing in the queue
            if page < 1 or page > len(song_queue_chunked):
                await ctx.respond("Invalid page number.")
            else:
                queue_string = f"```diff\nType a number to show a specific page. For example, \"s!queue 2\" will show the second page.\nDisplaying page {page}/{len(song_queue_chunked)}\n"
                for song in song_queue_chunked[page - 1]:
                    if first_track and page == 1:
                        queue_string += f"-> {self.song_queue.index(song) + 1}. {song} - ({self.format_song_length(song.length)}) (current track)\n"
                        first_track = False
                    else:
                        queue_string += f"   {self.song_queue.index(song) + 1}. {song} - ({self.format_song_length(song.length)})\n"
                queue_string += "```"
                await ctx.respond(queue_string)

    @bot.bridge_command(aliases=["huffle", "mix", "randomize"])
    async def shuffle(self, ctx):
        """Shuffles the queue."""
        vc = ctx.voice_client
        if not vc:
            await ctx.respond("You must be in a voice channel to use this command.")
        temp_queue = self.song_queue[1:]
        for _ in range(1, len(self.song_queue)):
            self.song_queue.pop()
        random.shuffle(temp_queue)
        self.song_queue += temp_queue
        await ctx.respond("Shuffled the queue.")

    @bot.bridge_command(aliases=["nowplaying", "current", "info"])
    async def now_playing(self, ctx):
        """Gives information about the current track."""
        vc = ctx.voice_client
        if not vc:
            await ctx.respond("You must be in a voice channel to use this command.")
        info = f"```Song title: {self.song_queue[0]}\nLength: {self.format_song_length(self.song_queue[0].length)}```"
        await ctx.respond(info)

    @bot.bridge_command(aliases=["rem", "r", "rm"])
    async def remove(self, ctx, index: int):
        """Remove a track at the specified index."""
        vc = ctx.voice_client
        if not vc:
            await ctx.respond("You must be in a voice channel to use this command.")
        try:
            if index < 1:
                await ctx.respond("Invalid index.")
            if index == 1:
                # removing the current track is equivalent to skipping it
                await vc.pause()
                await vc.resume()
                await vc.play(self.song_queue[1], replace=True)
                await ctx.respond(f"Removed `{self.song_queue[0]}` **`({self.format_song_length(self.song_queue[0].length)})`**. Now playing: `{self.song_queue[1]}` **`({self.format_song_length(self.song_queue[1].length)})`**")
            else:
                removed_track = self.song_queue.pop(index - 1)
                await ctx.respond(f"Removed {removed_track} ({self.format_song_length(removed_track.length)}) from the queue.")
        except Exception:
            await ctx.respond("Invalid index.")

def setup(bot):
    bot.add_cog(Music(bot))
