# uses pycord
# import discord
# import os
# import random
# import time
import typing
import wavelink
from discord.ext import bridge, commands
# from sucrose import make_embed
# from wavelink.ext import spotify

# SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
# SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

bot = bridge.Bot()

# Massive rewrite in progress...
class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = []
        self.bot.loop.create_task(self.connect_nodes())

    async def connect_nodes(self):
        """Connect to our Lavalink nodes."""
        await self.bot.wait_until_ready() # wait until the bot is ready

        nodes = [
            wavelink.Node(
            identifier="Node1", # This identifier must be unique for all the nodes you are going to use
            uri="http://localhost:2333", # Protocol (http/s) is required, port must be 443 as it is the one lavalink uses
            # uri="https://eu-lavalink.lexnet.cc:443", # Protocol (http/s) is required, port must be 443 as it is the one lavalink uses
            password="aac6308"
            )
        ]

        await wavelink.Pool.connect(nodes=nodes, client=self.bot) # Connect our nodes

    @bot.bridge_command(aliases=["p", "pl"])
    async def play(self, ctx, *, search: str):
        vc = typing.cast(wavelink.Player, ctx.voice_client)
        # vc = ctx.voice_client

        if not vc:
            vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)

        if ctx.author.voice.channel.id != vc.channel.id:
            return await ctx.respond("must be same VC as bot")
    
        song = (await wavelink.Playable.search(search, source=wavelink.TrackSource.YouTube))[0]

        if not song:
            return await ctx.respond("no song found")
        
        print(F"\n7234723456775677\n{song}\n")
        
        # https://github.com/lavalink-devs/Lavalink/issues/1091
        # https://github.com/lavalink-devs/Lavalink/issues/1085
        # https://github.com/lavalink-devs/Lavalink/discussions/1080
        # https://github.com/lavalink-devs/youtube-source - look into this?
        await vc.play(song, paused=False)
        await ctx.respond(f"now playing: `{song.title}`")

    """ @commands.Cog.listener()
    async def on_ready(self):
        await self.connect_nodes() """

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, payload: wavelink.NodeReadyEventPayload):
        print(f"Node with ID {payload.session_id} has connected")
        print(f"Resumed session: {payload.resumed}")

def setup(bot):
    bot.add_cog(Music(bot))
