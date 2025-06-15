import asyncio
import functools
import time

import discord
import morefunc as m
import requests
import yt_dlp

from bs4 import BeautifulSoup
from discord.ext import bridge, commands
from random import shuffle
from sucrose import make_embed

class VoiceError(Exception):
    pass

class YTDLSource(discord.PCMVolumeTransformer):
    YTDL_OPTIONS = {
        "format": "bestaudio/best",
        "extractaudio": True,
        "audioformat": "m4a", # mp3 m4a aac
        "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
        "restrictfilenames": True,
        "cookies_from_browser": "firefox",
        # "noplaylist": True,
        # "playlist_items": "1",
        "nocheckcertificate": True,
        "ignoreerrors": True,   # needed to deal with unavailable videos
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

        # self.uploader = data.get("uploader")
        # self.uploader_url = data.get("uploader_url")
        date = data.get("upload_date")
        # self.upload_date = date[6:8] + "." + date[4:6] + "." + date[0:4] if date else "unknown"
        self.title = m.escape_markdown(rf"{data.get('title')}")
        self.thumbnail = data.get("thumbnail")
        # self.description = data.get("description")
        self.duration_sec = int(data.get("duration", 0))
        self.duration = m.format_duration(self.duration_sec)
        # self.tags = data.get("tags")
        self.url = data.get("webpage_url")
        # self.views = data.get("view_count")
        # self.likes = data.get("like_count")
        # self.dislikes = data.get("dislike_count")
        # self.stream_url = data.get("url")

    def __str__(self):
        return f"{m.bcolors.OKCYAN}{self.title}{m.bcolors.ENDC} - {m.bcolors.WARNING}({self.duration}){m.bcolors.ENDC}"


    @classmethod
    async def create_sources(cls, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop = None, get_playlist: bool=False):
        start = time.time()
        loop = loop or asyncio.get_event_loop()

        async def extract_info(url: str, download: bool=False, process: bool=True):
            partial = functools.partial(cls.ytdl.extract_info, url, download=download, process=process)
            return await loop.run_in_executor(None, partial)

        if get_playlist:    # if user queries a playlist
            playlist_data = await extract_info(search, download=False, process=True)
            if not playlist_data or "entries" not in playlist_data or not playlist_data["entries"]:
                raise VoiceError(f"Couldn't find any entries in the playlist `{search}`")

            sources = []
            for entry in playlist_data["entries"]:
                if entry is None:
                    continue

                video_data = await extract_info(entry["webpage_url"], download=False, process=True)
                if not video_data:
                    continue

                if "entries" in video_data:
                    video_data = video_data["entries"][0]

                if video_data.get("age_limit", 0) > 0:
                    m.print_with_timestamp(f"skipped age-restricted video: {video_data['title']}")
                    continue

                source = cls(ctx, discord.FFmpegPCMAudio(video_data["url"], **cls.FFMPEG_OPTIONS), data=video_data)
                sources.append(source)

            if not sources:
                raise VoiceError(f"Couldn't retrieve any playable videos from the playlist `{search}`")
            
            end = time.time()
            m.print_with_timestamp(f"{m.bcolors.WARNING}Time taken to process create_sources(): {end - start}{m.bcolors.ENDC}")

            print("CREATE SOURCES - PLAYLIST", source)
            return sources

        else:   # if user queries a single track
            data = await extract_info(search, download=False, process=False)
            if not data:
                raise VoiceError(f"Couldn't find anything that matches `{search}`")

            if "entries" in data:   # if data contains multiple entries, pick the first valid one
                process_info = next((entry for entry in data["entries"] if entry), None)
                if not process_info:
                    raise VoiceError(f"Couldn't find any valid entries for `{search}`")
            else:
                process_info = data

            webpage_url = process_info["webpage_url"]
            if not webpage_url:
                raise VoiceError(f"Couldn't find a valid URL for `{search}`")

            processed_info = await extract_info(webpage_url, download=False, process=True)
            if not processed_info:
                raise VoiceError(f"Couldn't fetch `{webpage_url}`")

            if "entries" in processed_info: # if processed_info is a playlist, pop the first valid entry
                info = None
                while info is None:
                    try:
                        info = processed_info["entries"].pop(0)
                    except IndexError:
                        raise VoiceError(f"Couldn't retrieve any matches for `{webpage_url}`")
            else:
                info = processed_info
            
            end = time.time()
            m.print_with_timestamp(f"{m.bcolors.WARNING}Time taken to process create_sources(): {end - start}{m.bcolors.ENDC}")

            source = cls(ctx, discord.FFmpegPCMAudio(info["url"], **cls.FFMPEG_OPTIONS), data=info)
            print("CREATE SOURCES - SINGLE TRACK", source)

            return source


bot = bridge.Bot()

class Music(commands.Cog):
    def __init__(self, bot: discord.ext.bridge.Bot):
        self.bot = bot
        self.track_queue = []
        self.stop_track = None
        self.current_track = None
        self.looping = False


    @bridge.bridge_command(aliases=["p", "push"])
    async def play(self, ctx: discord.ext.bridge.context.BridgeApplicationContext, *, search: str) -> None:
        """
        Play a track or playlist. 
        ### Supported
        * Bandcamp track links
        * SoundCloud
        * Spotify track links
        * YouTube
        * YouTube Music

        ### Not supported
        * Apple Music
        * Deezer
        * MySpace
        * Spotify album and playlist links
        * Tidal
        """
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
            try:
                if "https://www.youtube.com/playlist?list=" in search or "https://music.youtube.com/playlist?list=" in search:
                    await ctx.respond(embed=make_embed(f"⏳️ Loading YouTube playlist..."), delete_after=60)
                    sources = await YTDLSource.create_sources(ctx, search, loop=self.bot.loop, get_playlist=True)
                    for source in sources:
                        self.track_queue.append(source)
                    await ctx.respond(embed=make_embed(f"Added {len(sources)} tracks to the queue."), delete_after=15)
                elif "https://open.spotify.com/t" in search:
                    await ctx.respond(embed=make_embed(f"⏳️ Loading Spotify track link..."), delete_after=15)
                    # what the fuck?
                    # string manipulation spoofing
                    soup = BeautifulSoup(requests.get(search).text, "html.parser")
                    units = soup.find("title").string.split(" - song and lyrics by ")
                    track_name = units[0]
                    artist_name = units[-1].split(" | ")[0]
                    # meta_tag = soup.find("meta", property="og:description").get("content").split(" · ")
                    # album = meta_tag[1]
                    # year = meta_tag[-1]

                    source = await YTDLSource.create_sources(ctx, f"{track_name} {artist_name}", loop=self.bot.loop)
                    self.track_queue.append(source)
                elif "https://open.spotify.com/a" in search or "https://open.spotify.com/p" in search:
                    await ctx.respond(embed=make_embed(f"Spotify album/playlist links are currently not supported."), delete_after=15)
                else:
                    await ctx.respond(embed=make_embed(f"🔍 Searching for **\"{search}\"**..."), delete_after=15)
                    source = await YTDLSource.create_sources(ctx, search, loop=self.bot.loop)
                    self.track_queue.append(source)

                if not vc.is_playing():
                    self.current_track = self.track_queue[0]
                    self.stop_track = source
                    vc.play(self.current_track, after=lambda e: self.bot.loop.create_task(self.play_next(ctx)))
                    await ctx.respond(embed=make_embed(
                        f"▶️ Now playing: **[{self.current_track.title}]({self.current_track.url})** "
                        f"**`({self.current_track.duration})`**."), delete_after=15)
                else:
                    if "https://www.youtube.com/playlist?list=" in search or "https://music.youtube.com/playlist?list=" in search:
                        pass
                    else:
                        await ctx.respond(embed=make_embed(
                            f"👌 **[{source.title}]({source.url})** "
                            f"added to the queue **`({source.duration})`**."), delete_after=15)
            except Exception as e:
                await ctx.respond(embed=make_embed(
                    f"**No results found for: \"{search}\".**\n"
                    f"**Details:** {e}"
                ), delete_after=15)

        m.print_with_timestamp( # line feed, tab, track name, duration
            f"{m.bcolors.OKBLUE}@{ctx.author.name}{m.bcolors.ENDC} in {m.bcolors.OKGREEN}{ctx.guild.name}{m.bcolors.ENDC} - PLAY"
            f"\n\t{f'{chr(10)}{chr(9)}'.join(song.__str__() for song in self.track_queue)}"
        )


    async def play_next(self, ctx: discord.ext.bridge.context.BridgeApplicationContext) -> None:
        """Called when a track ends."""
        vc = ctx.voice_client
        try:
            # looks stupid but it works
            if len(self.track_queue) > 0 and not vc.is_playing():
                self.track_queue.pop(0)
                self.current_track = self.track_queue[0]
                vc.stop()
                vc.play(self.current_track, after=lambda e: self.bot.loop.create_task(self.play_next(ctx)))
                await ctx.respond(embed=make_embed(
                    f"▶️ Now playing: **[{self.current_track.title}]({self.current_track.url})** "
                    f"**`({self.current_track.duration})`**."), delete_after=15)
            else:
                self.current_track = None
        except Exception as e:
            m.print_with_timestamp(f"PLAY NEXT: {e}")


    @bridge.bridge_command(aliases=["next", "kip", "slip", "n", "s"])
    async def skip(self, ctx: discord.ext.bridge.context.BridgeApplicationContext) -> None:
        """
        Skips the current track and plays the next track in the queue.
        If there is only one track left in the queue, stop playing the current track.
        You can't play back a skipped track, you need to queue it again.
        """
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
            m.print_with_timestamp(
                f"{m.bcolors.OKBLUE}@{ctx.author.name}{m.bcolors.ENDC} in {m.bcolors.OKGREEN}{ctx.guild.name}{m.bcolors.ENDC} - SKIP > 1"
                f"\n\t{f'{chr(10)}{chr(9)}'.join(song.__str__() for song in self.track_queue)}"
            )
            skipped_track = self.track_queue[0]
            next_track = self.track_queue[1]
            vc.stop()
            await self.play_next(ctx)
            self.current_track = next_track
            await ctx.respond(embed=make_embed(
                f"⏭️ Skipped **[{skipped_track.title}]({skipped_track.url})** "
                f"**`({skipped_track.duration})`**."), delete_after=15)
        elif len(self.track_queue) == 1:
            m.print_with_timestamp(
                f"{m.bcolors.OKBLUE}@{ctx.author.name}{m.bcolors.ENDC} in {m.bcolors.OKGREEN}{ctx.guild.name}{m.bcolors.ENDC} - SKIP == 1"
                f"\n\t{f'{chr(10)}{chr(9)}'.join(song.__str__() for song in self.track_queue)}"
            )
            skipped_track = self.track_queue.pop()
            vc.stop()
            self.track_queue.clear()
            self.stop_track = None
            self.current_track = None
            self.looping = False
            await ctx.respond(embed=make_embed(
                f"⏭️ Skipped the last track: **[{skipped_track.title}]({skipped_track.url})** "
                f"**`({skipped_track.duration})`**.\n"
                "❌️ Queue is now empty."), delete_after=15)
        else:
            m.print_with_timestamp(
                f"{m.bcolors.OKBLUE}@{ctx.author.name}{m.bcolors.ENDC} in {m.bcolors.OKGREEN}{ctx.guild.name}{m.bcolors.ENDC} - SKIP STOP"
                f"\n\t{f'{chr(10)}{chr(9)}'.join(song.__str__() for song in self.track_queue)}"
            )
            vc.stop()
            self.track_queue.clear()
            self.stop_track = None
            self.current_track = None
            self.looping = False
            await ctx.respond(embed=make_embed("❌️ Queue is now empty. Playback stopped."), delete_after=15)

        m.print_with_timestamp(
            f"{m.bcolors.OKBLUE}@{ctx.author.name}{m.bcolors.ENDC} in {m.bcolors.OKGREEN}{ctx.guild.name}{m.bcolors.ENDC} - SKIP"
            f"\n\t{f'{chr(10)}{chr(9)}'.join(song.__str__() for song in self.track_queue)}"
        )


    @bot.bridge_command(aliases=["x", "st", "halt", "top"])
    async def stop(self, ctx: discord.ext.bridge.context.BridgeApplicationContext) -> None:
        """
        Stops the current track. Stopped track cannot be resumed afterwards.
        Also clears the queue.
        """
        vc = ctx.voice_client
        if not vc: # if not in voice channel
            await ctx.respond(embed=make_embed(
                "You must be in the same voice channel as me to stop the current track."), delete_after=15)
        if not vc.is_playing():
            await ctx.respond(embed=make_embed("No track is playing."), delete_after=15)
        if vc.is_playing():
            vc.pause()
            vc.stop()
            await ctx.respond(embed=make_embed(
                f"⏹️ Stopped playing **[{self.stop_track.title}]({self.stop_track.url})** "
                f"**`({self.stop_track.duration})`**."), delete_after=15)
            self.track_queue.clear()
            self.stop_track = None
            self.current_track = None
            self.looping = False
            await vc.disconnect()

        m.print_with_timestamp(
            f"{m.bcolors.OKBLUE}@{ctx.author.name}{m.bcolors.ENDC} in {m.bcolors.OKGREEN}{ctx.guild.name}{m.bcolors.ENDC} - STOP"
            f"\n\t{f'{chr(10)}{chr(9)}'.join(song.__str__() for song in self.track_queue)}"
        )


    @bot.bridge_command(aliases=["ps"])
    async def pause(self, ctx: discord.ext.bridge.context.BridgeApplicationContext) -> None:
        """Pauses the current track. Use `s!resume` to resume playing the track."""
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
        m.print_with_timestamp(f"{m.bcolors.OKBLUE}@{ctx.author.name}{m.bcolors.ENDC} in {m.bcolors.OKGREEN}{ctx.guild.name}{m.bcolors.ENDC} - PAUSE")


    @bot.bridge_command(aliases=["res", "rs"])
    async def resume(self, ctx: discord.ext.bridge.context.BridgeApplicationContext) -> None:
        """Resumes the current paused track. Does nothing if the track is currently playing."""
        vc = ctx.voice_client
        if vc.is_paused():
            vc.resume()
            await ctx.respond(embed=make_embed(
                f"▶️ Resuming **[{self.track_queue[0].title}]({self.track_queue[0].url})**."), delete_after=15)
        else:
            await ctx.respond(embed=make_embed(
                "You must be in the same voice channel as the bot to use this command."), delete_after=15)
        m.print_with_timestamp(f"{m.bcolors.OKBLUE}@{ctx.author.name}{m.bcolors.ENDC} in {m.bcolors.OKGREEN}{ctx.guild.name}{m.bcolors.ENDC} - RESUME")


    @bot.bridge_command(aliases=["q", "pl", "list", "playlist"])
    async def queue(self, ctx: discord.ext.bridge.context.BridgeApplicationContext, page: str="1") -> None:
        """
        Shows the tracks queued by Sucrose.
        Can be used with an optional integer parameter to show a specific page (e.g. `s!queue 2`), if applicable. 
        """
        try:
            page = int(page)
            vc = ctx.voice_client
            if not vc:
                await ctx.respond(embed=make_embed("You must be in a voice channel to use this command."), delete_after=15)
            if len(self.track_queue) < 1:
                await ctx.respond(embed=make_embed("There are no tracks in the queue."), delete_after=15)
            else:
                tq_chunk_size = 10  # tq = track queue, divides the queue into 10 tracks each
                tq_chunked  = [self.track_queue[i : i + tq_chunk_size] for i in range(0, len(self.track_queue), tq_chunk_size)]
                first_track = True  # used for the "current track" thing in the queue

                tq_duration_sec = 0 # the length of the whole queue
                for track in self.track_queue:
                    tq_duration_sec += track.duration_sec

                queue_embed = discord.Embed(
                    title="🎶 Queue 🎶",
                    description=(f"\nType a number to show a specific page, e.g. `s!queue 2` will show the second page.\n"
                    f"**Track count:** `{len(self.track_queue)}`, **Total queue duration:** "
                    f"`{m.format_duration(tq_duration_sec)}`\n"
                    f"**Displaying page** `{page}/{len(tq_chunked)}`"),
                    color=discord.Colour.from_rgb(84, 220, 179)
                )

                if page < 1 or page > len(tq_chunked):
                    await ctx.respond(embed=make_embed("Invalid page number."), delete_after=15)
                else:
                    m.print_with_timestamp(
                        f"{m.bcolors.OKBLUE}@{ctx.author.name}{m.bcolors.ENDC} in {m.bcolors.OKGREEN}{ctx.guild.name}{m.bcolors.ENDC} - QUEUE"
                        f"\n\t{f'{chr(10)}{chr(9)}'.join(f'{chr(10)}{chr(9)}'.join(song.__str__() for song in chunk) for chunk in tq_chunked)}"
                    )
                    for track in tq_chunked[page - 1]:
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
        except ValueError:
            await ctx.respond(embed=make_embed("⚠️ Usage: `s!queue page_number`."), delete_after=15)



    @bot.bridge_command(aliases=["sf", "huffle", "mix", "randomize"])
    async def shuffle(self, ctx: discord.ext.bridge.context.BridgeApplicationContext) -> None:
        """Shuffles the queue."""
        vc = ctx.voice_client
        if not vc:
            await ctx.respond(embed=make_embed("You must be in a voice channel to use this command."), delete_after=15)
        temp = self.track_queue[1:] # shuffle the entire queue BUT the current track
        for _ in range(1, len(self.track_queue)):
            self.track_queue.pop()
        shuffle(temp)
        self.track_queue += temp
        await ctx.respond(embed=make_embed("🔀 Shuffled the queue."), delete_after=15)
        m.print_with_timestamp(
            f"{m.bcolors.OKBLUE}@{ctx.author.name}{m.bcolors.ENDC} in {m.bcolors.OKGREEN}{ctx.guild.name}{m.bcolors.ENDC} - SHUFFLE"
            f"\n\t{f'{chr(10)}{chr(9)}'.join(song.__str__() for song in self.track_queue)}"
        )


    @bot.bridge_command(aliases=["np", "nowplaying", "current", "info"])
    async def now_playing(self, ctx: discord.ext.bridge.context.BridgeApplicationContext) -> None:
        """Gives information about the current track."""
        vc = ctx.voice_client
        if not vc:
            await ctx.respond(embed=make_embed("❌ You must be in a voice channel to use this command."), delete_after=15)
        if self.current_track:
            now_playing_embed = discord.Embed(
                title="🎶 Now playing 🎶",
                description=f"**[{self.current_track.title}]({self.current_track.url})**\n"
                            f"**`{self.current_track.duration}`**",
                color=discord.Colour.from_rgb(84, 220, 179)
            )
            await ctx.respond(embed=now_playing_embed, delete_after=15)
        else:
            await ctx.respond(embed=make_embed("❌ Nothing is playing right now."), delete_after=15)
        m.print_with_timestamp(
            f"{m.bcolors.OKBLUE}@{ctx.author.name}{m.bcolors.ENDC} in {m.bcolors.OKGREEN}{ctx.guild.name}{m.bcolors.ENDC} - NOWPLAYING "
            f"{self.current_track.__str__()}"
        )


    @bot.bridge_command(aliases=["r", "rm", "rem", "pop"])
    async def remove(self, ctx: discord.ext.bridge.context.BridgeApplicationContext, idx: str) -> None:
        """Remove a track at the specified index."""
        try:
            idx = int(idx)
            vc = ctx.voice_client
            removed_track = None
            if not vc:
                await ctx.respond(embed=make_embed("❌ You must be in a voice channel to use this command."), delete_after=15)
            try:
                if idx < 1:
                    await ctx.respond(embed=make_embed("❌ Invalid index."), delete_after=15)
                if idx == 1: # removing the current track is equivalent to skipping it
                    if len(self.track_queue) == 1: # if queue has only one track, might as well stop the entire queue
                        removed_track = self.track_queue.pop(idx - 1)
                        vc.stop()
                        await ctx.respond(embed=make_embed(
                            f"❌ Removed **[{removed_track.title}]({removed_track.url})** "
                            f"**`({removed_track.duration})`** from the queue."), delete_after=15)
                    else:
                        # await vc.pause()
                        # await vc.resume()
                        vc.stop()
                        vc.play(self.track_queue[1])
                        await ctx.respond(embed=make_embed(
                            f"❌ Removed **[{self.track_queue[0].title}]({self.track_queue[0].url})** "
                            f"**`({self.track_queue[0].duration})`**. "
                            f"Now playing: **[{self.track_queue[1].title}]({self.track_queue[1].url})** "
                            f"**`({self.track_queue[1].duration})`**"), delete_after=15)
                else:
                    removed_track = self.track_queue.pop(idx - 1)
                    await ctx.respond(embed=make_embed(
                        f"❌  Removed **[{removed_track.title}]({removed_track.url})** "
                        f"**`({removed_track.duration})`** from the queue."), delete_after=15)
            except Exception:
                await ctx.respond(embed=make_embed("❌ Invalid index."), delete_after=15)
            m.print_with_timestamp(
                f"{m.bcolors.OKBLUE}@{ctx.author.name}{m.bcolors.ENDC} in {m.bcolors.OKGREEN}{ctx.guild.name}{m.bcolors.ENDC} - REMOVE "
                f"{idx}, {removed_track}"
            )
        except ValueError:
            await ctx.respond(embed=make_embed("⚠️ Usage: `s!remove index`."), delete_after=15)


    @bot.bridge_command(aliases=["l", "lp"])
    async def loop(self, ctx: discord.ext.bridge.context.BridgeApplicationContext) -> None:
        """Loop the current track until this command is invoked again."""
        await ctx.respond(embed=make_embed("❌ Track looping not available at the moment."), delete_after=15)

        if self.looping:
            self.looping = False
        else:
            self.looping = True

        m.print_with_timestamp(
            f"{m.bcolors.OKBLUE}@{ctx.author.name}{m.bcolors.ENDC} in {m.bcolors.OKGREEN}{ctx.guild.name}{m.bcolors.ENDC} - LOOP {self.looping}"
        )


def setup(bot):
    bot.add_cog(Music(bot))
