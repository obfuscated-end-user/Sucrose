import asyncio
import functools
import time

import discord
import yt_dlp

from random import shuffle
from discord.ext import bridge, commands
from sucrose import make_embed

class VoiceError(Exception):
    pass

class YTDLSource(discord.PCMVolumeTransformer):
    YTDL_OPTIONS = {
        "format": "bestaudio/best",
        "extractaudio": True,
        "audioformat": "mp3",
        "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
        "restrictfilenames": True,
        "cookies_from_browser": "firefox",
        # "noplaylist": True,
        # "playlist_items": "1",
        "nocheckcertificate": True,
        "ignoreerrors": False,
        "logtostderr": False,
        "quiet": True,
        "no_warnings": True,
        "default_search": "ytsearch",
        "source_address": "0.0.0.0",
    }

    FFMPEG_OPTIONS = {
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        "options": "-vn",
    }

    ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

    def __init__(self, ctx: commands.Context, source: discord.FFmpegPCMAudio, *, data: dict, volume: float=0.5):
        super().__init__(source, volume)

        self.requester = ctx.author
        self.channel = ctx.channel
        self.data = data

        self.uploader = data.get("uploader")
        self.uploader_url = data.get("uploader_url")
        date = data.get("upload_date")
        self.upload_date = date[6:8] + "." + date[4:6] + "." + date[0:4] if date else "Unknown"
        self.title = data.get("title")
        self.thumbnail = data.get("thumbnail")
        self.description = data.get("description")
        self.duration_sec = int(data.get("duration", 0))
        self.duration = self.format_track_length(self.duration_sec)
        self.tags = data.get("tags")
        self.url = data.get("webpage_url")
        self.views = data.get("view_count")
        self.likes = data.get("like_count")
        self.dislikes = data.get("dislike_count")
        self.stream_url = data.get("url")

    def __str__(self):
        return f"**{self.title}** by **{self.uploader}**"


    @classmethod
    async def create_source(cls, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop=None):
        """I think this can be combined (seamlessly?) with the function directly below."""
        loop = loop or asyncio.get_event_loop()
        async def extract_info(url: str, download: bool=False, process: bool=True):
            partial = functools.partial(cls.ytdl.extract_info, url, download=download, process=process)
            return await loop.run_in_executor(None, partial)

        data = await extract_info(search, download=False, process=False)
        if data is None:
            raise VoiceError(f"Couldn't find anything that matches `{search}`")

        if "entries" in data:
            process_info = next((entry for entry in data["entries"] if entry), None)
            if process_info is None:
                raise VoiceError(f"Couldn't find anything that matches `{search}`")
        else:
            process_info = data

        webpage_url = process_info["webpage_url"]
        processed_info = await extract_info(webpage_url, download=False, process=True)
        if processed_info is None:
            raise VoiceError(f"Couldn't fetch `{webpage_url}`")

        if "entries" in processed_info:
            info = None
            while info is None:
                try:
                    info = processed_info["entries"].pop(0)
                except IndexError:
                    raise VoiceError(f"Couldn't retrieve any matches for `{webpage_url}`")
        else:
            info = processed_info

        return cls(ctx, discord.FFmpegPCMAudio(info["url"], **cls.FFMPEG_OPTIONS), data=info)


    @classmethod
    async def create_sources_from_playlist(cls, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop=None):
        """Rewrite this whole thing."""
        loop = loop or asyncio.get_event_loop()

        def extract_playlist(url):
            return cls.ytdl.extract_info(url, download=False, process=True)
        
        def extract_video(url):
            return cls.ytdl.extract_info(url, download=False, process=True)

        playlist_data = await loop.run_in_executor(None, functools.partial(extract_playlist, search))

        if playlist_data is None:
            raise VoiceError(f"Couldn't find anything that matches `{search}`")

        if "entries" not in playlist_data or not playlist_data["entries"]:
            raise VoiceError(f"No entries found in the playlist `{search}`")

        sources = []

        for entry in playlist_data["entries"]:
            if entry is None:
                continue

            video_data = await loop.run_in_executor(None, functools.partial(extract_video, entry["webpage_url"]))

            if video_data is None:
                continue

            if "entries" in video_data:
                video_data = video_data["entries"][0]

            source = cls(ctx, discord.FFmpegPCMAudio(video_data["url"], **cls.FFMPEG_OPTIONS), data=video_data)
            sources.append(source)

        if not sources:
            raise VoiceError(f"Couldn't retrieve any playable videos from the playlist `{search}`")

        return sources
        
    
    @staticmethod
    def format_track_length(seconds) -> str:
        """Formats the length of a track in HH:MM:SS."""
        if seconds < 3600: # 3600 seconds is equal to 1 hour
            return time.strftime("%M:%S", time.gmtime(seconds))
        else:
            return time.strftime("%H:%M:%S", time.gmtime(seconds))

bot = bridge.Bot()

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.track_queue = []
        self.stop_track = None
        self.current_track = None


    @bridge.bridge_command(aliases=["p", "push"])
    async def play(self, ctx, *, search: str):
        """Play a track or playlist. Accepts YouTube links."""
        vc = ctx.voice_client
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.respond(embed=make_embed("You need to be in a voice channel to play music."))

        if not vc:
            try:
                vc = await ctx.author.voice.channel.connect()
            except discord.Forbidden:
                return await ctx.respond(embed=make_embed("I don't have permission to join that voice channel."))
            except discord.ClientException:
                return await ctx.respond(embed=make_embed("I am already connected to a voice channel."))

        if ctx.author.voice.channel.id != vc.channel.id:
            return await ctx.respond(embed=make_embed("You must be in the same voice channel as the bot."), delete_after=15)

        else:
            if "https://www.youtube.com/playlist?list=" in search or "https://music.youtube.com/playlist?list=" in search:
                await ctx.respond(embed=make_embed(f"Loading playlist..."), delete_after=60)
                sources = await YTDLSource.create_sources_from_playlist(ctx, search, loop=self.bot.loop)

                for source in sources:
                    self.track_queue.append(source)

                await ctx.respond(embed=make_embed(f"Added {len(sources)} tracks to the queue."), delete_after=15)
            else:
                await ctx.respond(embed=make_embed(f"🔍 Searching for **\"{search}\"**..."), delete_after=15)
                source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop)
                self.track_queue.append(source)

            if not vc.is_playing():
                self.current_track = self.track_queue[0]
                self.stop_track = source
                vc.play(self.current_track, after=lambda e: self.bot.loop.create_task(self.play_next(ctx)))
                await ctx.respond(embed=make_embed(
                    f"▶️ Now playing: **[{self.current_track.title}]({self.current_track.url})** "
                    f"**`({self.current_track.duration})`**."), delete_after=15)
            else:
                await ctx.respond(embed=make_embed(
                    f"👌 **[{source.title}]({source.url})** "
                    f"added to the queue **`({source.duration})`**."), delete_after=15)
        print("PLAY", self.track_queue) # for debug, remove print statements like this in the future


    async def play_next(self, ctx):
        """Called when a track ends."""
        vc = ctx.voice_client
        if len(self.track_queue) > 0:
            print(f"\nPLAY NEXT\n{self.track_queue}\n")
            self.track_queue.pop(0)
            self.current_track = self.track_queue[0]
            vc.stop()
            vc.play(self.current_track, after=lambda e: self.bot.loop.create_task(self.play_next(ctx)))
            await ctx.respond(embed=make_embed(
                    f"▶️ Now playing: **[{self.current_track.title}]({self.current_track.url})** "
                    f"**`({self.current_track.duration})`**."), delete_after=15)
        else:
            self.current_track = None
            # await ctx.send(embed=make_embed("The queue is empty."))


    @bridge.bridge_command(aliases=["next", "kip", "slip", "n", "s"])
    async def skip(self, ctx):
        """Skips the current track and plays the next track in the queue."""
        vc = ctx.voice_client
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.respond(embed=make_embed(
                "You must be connected to a voice channel to use this command."), delete_after=15)
            return

        if not vc:
            vc = await ctx.author.voice.channel.connect()
            self.voice_client = vc
        else:
            self.voice_client = vc

        if ctx.author.voice.channel.id != vc.channel.id:
            await ctx.respond(embed=make_embed("You must be in the same voice channel as the bot."), delete_after=15)
            return

        if not vc.is_playing():
            await ctx.respond(embed=make_embed("Nothing is playing right now."), delete_after=15)
            return

        if len(self.track_queue) > 1:
            print(f"\nSKIP > 1\n{self.track_queue}\n")
            skipped_track = self.track_queue[0]
            next_track = self.track_queue[1]
            vc.stop()
            # , after=lambda e: self.bot.loop.create_task(self.play_next(ctx))
            # vc.play(next_track)
            await self.play_next(ctx)
            self.current_track = next_track
            # self.track_queue.pop(0)
            await ctx.respond(embed=make_embed(
                f"⏭️ Skipped **[{skipped_track.title}]({skipped_track.url})** "
                f"**`({skipped_track.duration})`**.\n"
                f"▶️ Now playing: **[{next_track.title}]({next_track.url})** "
                f"**`({next_track.duration})`**."), delete_after=15)
        elif len(self.track_queue) == 1:
            print(f"\nSKIP == 1\n{self.track_queue}\n")
            skipped_track = self.track_queue.pop()
            vc.stop()
            await ctx.respond(embed=make_embed(
                f"⏭️  Skipped the last track: **[{skipped_track.title}]({skipped_track.url})** "
                f"**`({skipped_track.duration})`**.\n"
                "❌️ Queue is now empty."), delete_after=15)
            self.track_queue = []
            self.is_playing = False
            self.current_track = None
        else:
            print(f"\nSKIP STOP\n{self.track_queue}\n")
            vc.stop()
            await ctx.respond(embed=make_embed("❌️ Queue is now empty. Playback stopped."), delete_after=15)

        print("SKIP", self.track_queue)


    @bot.bridge_command(aliases=["x", "halt", "top"])
    async def stop(self, ctx):
        """Stops the current track. Stopped track cannot be resumed afterwards."""
        vc = ctx.voice_client
        if not vc: # if not in voice channel
            await ctx.respond(embed=make_embed(
                "You must be in the same voice channel as me to stop the current track."), delete_after=15)
        if not vc.is_playing():
            await ctx.respond(embed=make_embed("No track is playing."), delete_after=15)
        if vc.is_playing():
            # await vc.stop()
            await ctx.respond(embed=make_embed(
                f"⏹️ Stopped playing **{self.stop_track.title}** "
                f"**`({self.stop_track.duration})`**."), delete_after=15)
            self.track_queue = []
            self.stop_track = ""
            await vc.disconnect()


    @bot.bridge_command(aliases=["ps"])
    async def pause(self, ctx):
        """Pauses the current track. Use s!resume to resume playing the track."""
        vc = ctx.voice_client
        if not vc or not vc.is_playing(): # if not in voice channel
            vc.pause()
            await ctx.respond(embed=make_embed("I am currently not playing anything."), delete_after=15)
        elif vc.is_paused(): # do nothing if track is paused
            return
        if vc.is_playing():
            vc.pause()
            await ctx.respond(embed=make_embed(
                f"⏸️ Paused **[{self.track_queue[0].title}]({self.track_queue[0].url})**. "
                "Type `s!resume` to resume playback."), delete_after=15)


    @bot.bridge_command(aliases=["res", "rs"])
    async def resume(self, ctx):
        """Resumes the current paused track. Does nothing if the track is currently playing."""
        vc = ctx.voice_client
        if vc.is_paused():
            vc.resume()
            await ctx.respond(embed=make_embed(
                f"▶️ Resuming **[{self.track_queue[0].title}]({self.track_queue[0].url})**."), delete_after=15)
        else:
            await ctx.respond(embed=make_embed(
                "You must be in the same voice channel as the bot to use this command."), delete_after=15)


    @bot.bridge_command(aliases=["q", "pl", "list", "playlist"])
    async def queue(self, ctx, page=1):
        """Shows the queue. Can be used with an optional integer parameter to show a specific page."""
        vc = ctx.voice_client
        if not vc:
            await ctx.respond(embed=make_embed("You must be in a voice channel to use this command."), delete_after=15)
        if len(self.track_queue) < 1:
            await ctx.respond(embed=make_embed("There are no tracks in the queue."), delete_after=15)
        else:
            track_queue_chunk_size = 10 # divides the queue into 10 tracks each
            track_queue_chunked  = [self.track_queue[i : i + track_queue_chunk_size] for i in range(0, len(self.track_queue), track_queue_chunk_size)]
            first_track = True # used for the "current track" thing in the queue

            track_queue_length_seconds = 0 # the length of the whole queue
            for track in self.track_queue:
                track_queue_length_seconds += track.duration_sec

            queue_embed = discord.Embed(
                title="🎶 Queue 🎶",
                description=(f"\nType a number to show a specific page, e.g. `s!queue 2` will show the second page.\n"
                f"**track count:** `{len(self.track_queue)}`, **Total queue duration:** "
                f"`{YTDLSource.format_track_length(track_queue_length_seconds)}`\n"
                f"**Displaying page** `{page}/{len(track_queue_chunked)}`"),
                color=discord.Colour.from_rgb(84, 220, 179)
            )

            if page < 1 or page > len(track_queue_chunked):
                await ctx.respond(embed=make_embed("Invalid page number."), delete_after=15)
            else:
                print("\nQUEUE\n", track_queue_chunked)
                for track in track_queue_chunked[page - 1]:
                    if first_track and page == 1:
                        queue_embed.add_field(
                            name="", value=f"**{self.track_queue.index(track) + 1}.** "
                            f"**[{self.current_track.title}]({self.current_track.url})** - "
                            f"**`({self.current_track.duration})`** 🎶\n", inline=False)
                        first_track = False
                    else:
                        queue_embed.add_field(
                            name="", value=f"**{self.track_queue.index(track) + 1}.** "
                            f"[{track.title}]({track.url}) - **`({track.duration})`**\n", inline=False)
                await ctx.respond(embed=queue_embed, delete_after=60)


    @bot.bridge_command(aliases=["sf", "huffle", "mix", "randomize"])
    async def shuffle(self, ctx):
        """Shuffles the queue."""
        vc = ctx.voice_client
        if not vc:
            await ctx.respond(embed=make_embed("You must be in a voice channel to use this command."), delete_after=15)
        temp_queue = self.track_queue[1:]    # shuffle the entire queue BUT the current track
        for _ in range(1, len(self.track_queue)):
            self.track_queue.pop()
        shuffle(temp_queue)
        self.track_queue += temp_queue
        await ctx.respond(embed=make_embed("🔀 Shuffled the queue."), delete_after=15)


    @bot.bridge_command(aliases=["np", "now_playing", "current", "info"])
    async def nowplaying(self, ctx):
        """Gives information about the current track."""
        vc = ctx.voice_client
        if not vc:
            await ctx.respond(embed=make_embed("You must be in a voice channel to use this command."), delete_after=15)
        now_playing_embed = discord.Embed(
            title="🎶 Now playing 🎶",
            # deal with titles that have asterisks or whatever markdown syntax it can have
            description=f"**[{self.current_track.title}]({self.current_track.url})**\n"
                        f"**`{self.current_track.duration}`**",
            color=discord.Colour.from_rgb(84, 220, 179)
        )
        await ctx.respond(embed=now_playing_embed, delete_after=15)


    @bot.bridge_command(aliases=["r", "rm", "rem", "pop"])
    async def remove(self, ctx, index: int):
        """Remove a track at the specified index."""
        vc = ctx.voice_client
        if not vc:
            await ctx.respond(embed=make_embed("❌ You must be in a voice channel to use this command."), delete_after=15)
        try:
            if index < 1:
                await ctx.respond(embed=make_embed("❌ Invalid index."), delete_after=15)
            if index == 1: # removing the current track is equivalent to skipping it
                if len(self.track_queue) == 1: # if queue has only one track, might as well stop the entire queue
                    removed_track = self.track_queue.pop(index - 1)
                    await vc.stop()
                    await ctx.respond(embed=make_embed(
                        f"❌ Removed **[{removed_track.title}]({removed_track.url})** "
                        f"**`({removed_track.duration})`** from the queue."), delete_after=15)
                else:
                    await vc.pause()
                    await vc.resume()
                    await vc.play(self.track_queue[1], replace=True)
                    await ctx.respond(embed=make_embed(
                        f"❌ Removed **[{self.track_queue[0].title}]({self.track_queue[0].url})** "
                        f"**`({self.track_queue[0].duration})`**. "
                        f"Now playing: **[{self.track_queue[1].title}]({self.track_queue[1].url})** "
                        f"**`({self.track_queue[1].duration})`**"), delete_after=15)
            else:
                removed_track = self.track_queue.pop(index - 1)
                await ctx.respond(embed=make_embed(
                    f"❌  Removed **[{removed_track.title}]({removed_track.url})** "
                    f"**`({removed_track.duration})`** from the queue."), delete_after=15)
        except Exception:
            await ctx.respond(embed=make_embed("❌ Invalid index."), delete_after=15)


def setup(bot):
    bot.add_cog(Music(bot))
