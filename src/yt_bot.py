import discord
import random
import os
from discord.ext import bridge, commands
from sucrose import make_embed

dir_path = os.path.dirname(os.path.realpath(__file__))
bot = bridge.Bot()

yt_link_formats = [
    "https://www.youtube.com/watch?v=",
    "https://youtu.be/",
    "http://y2u.be/",
]

unavailable = [
    "vMld3hM_n1c", "5WheryGqKb0", "aQIc8f5-zQY", "whsL8BdpVSQ", "icU8HSij1Z4", "V-lt-5Bqu90",
    "Jf_VnYfRKWc", "DmHx1LoD90k", "3YPmjRi3-n0", "KgRRb0vk0Gw", "yKHzXeno_ng", "QGzpkHqIwLk",
    "fo1qIzoXS94", "IsAmCwk8xhE", "XRGpLkMGDF8", "6krdDHGlgZk", "KTzyUhLriuA", "ElTPEMkkTmI",
    "MmrjZCj1hHs", "aRHk8ol0vTw", "K80rlQDc8vA", "TPAWpHG3RWY", "FQmr4wu9oVk", "gFmv82RGGsg",
    "gHyOL1RAihw", "5tA4-hu6ztQ", "Nl0nZK6usLc", "lqieaQY5hMU", "jj2aNVP8MbU", "GtcSIucyoFI",
    "4DXTbgEaHKc", "fbXp2Ov68-I", "C6WZ3Y7MQU0", "hnMYIYQu93g", "lQZVbPHFsyA", "XnQP3YMd4hU",
    "MDmBLRjDYHw", "3bNITQR4Uso", "agbdQruOweg", "io5JT40rOKY", "JRjyCmYV4M0", "IhSAzSlmkQU",
    "vkUDG-ku1tE", "yuLR8Z065y8", "ViOpchopGvQ", "wMzUIZpAIYI", "UTagsKq9cdE", "YoU3r6ZK8xQ",
    "uxxsN9V4qeE", "wSca4bQbxbY", "j02JOCjXrTU", "cxhhY2OTKYI", "2ULnCjlzcSI", "V8XTpCwicwE",
    "OKyhgOQvZ9A", "JQPrlLvesGA", "Km-YY1KvvTo", "surm5Fp946k", "HtvIYRrgZ04", "zLaKTjeg4L4",
    "uRNytga750U", "5_h2EFvliTA", "64-QEzeOt4w", "j12FTNJGesY", "VtQ2-tGshgQ", "ngE5Fhlktw8",
    "fO3J7ExZAro", "zEB3eEsAp0g", "g4NDQXPxjRg", "-nHWlVtPTew", "wECifChYMw4", "PmMY02L1iSA",
    "TZNpQYyCppo", "pOzgWz8UsRM", "O0JlxD-uz8E", "95G0cAhHnwU", "sSk1e8SnYLA", "cdWgoHbC7XA",
    "2IZAf9O7548", "1FHtIzLtlX8", "RnvIOzvn-iQ", "OVmZdExnsyI", "V3jsSMxKnXY", "-UQSzB6iwBg",
    "vz2SRI1mF1M", "OTQ2Z6gEa0Q", "9Gj47G2e1Jc", "CdrxzP-N1Y8", "tfmDF8PmUzk", "WHFWJ0T4zLk",
    "ksZW8mE1lug", "sLGnQiaCBfE", "3dqvHMFboak", "p_LMzX9cFqo", "nou8sehOU48", "cBRehsr_1h8",
]

class Yt_Bot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @bot.bridge_command(aliases=["ytlink", "ytl", "youtube", "randomvideo", "randvid"])
    async def yt(self, ctx: discord.ext.bridge.context.BridgeApplicationContext):
        """(NSFW WARNING) Returns a random YouTube link. May sometimes return deleted/privated videos."""
        yt_vid_ids_file = open(f"{dir_path}/yt_ids.txt", "r")
        yt_vid_ids_file_list = [id for [id] in [line.strip().split("\n") for line in yt_vid_ids_file.readlines()]]
        yt_vid_ids_file.close()

        for deleted_id in unavailable:
            if deleted_id in yt_vid_ids_file_list:
                yt_vid_ids_file_list.remove(deleted_id)

        id = random.choice(yt_vid_ids_file_list)
        # link = random.choice(yt_link_formats) + id # DO NOT USE
        link = yt_link_formats[1] + id
        await ctx.respond(embed=make_embed(f"# ⚠️ POTENTIAL NSFW/NSFL WARNING! ⚠️\n* Sucrose can't control what YouTube IDs will be generated, much less the content inside it.\n* If the embed does not show up, the video may be deleted or was set to private. Unlisted videos are not affected.\n* Archive links before they get 404'd at the [Wayback Machine](https://archive.org/web)!\n* If the video is deleted/not available, you can try viewing it [here](https://web.archive.org/web/https://www.youtube.com/watch?v={id}).\n* Do take note that this only views the webpage as it was archived during that time, and video playback is not guaranteed to work."))
        await ctx.respond(link)

    @bot.bridge_command()
    async def ytdebug(self, ctx: discord.ext.bridge.context.BridgeApplicationContext):
        """debug yt command"""
        yt_vid_ids_file = open(f"{dir_path}/yt_ids.txt", "r")
        yt_vid_ids_file_list = [line.strip().split("\n") for line in yt_vid_ids_file.readlines()]
        yt_vid_ids_file_list = [id for [id] in yt_vid_ids_file_list]
        yt_vid_ids_file.close()

        for deleted_id in unavailable:
            if deleted_id in yt_vid_ids_file_list:
                yt_vid_ids_file_list.remove(deleted_id)

        random_links = []
        for _ in range(5):
            random_links.append(random.choice(yt_link_formats) + random.choice(yt_vid_ids_file_list))
        
        # await ctx.respond(f"```⚠️ POTENTIAL NSFW/NSFL WARNING ⚠️\nSucrose can't control what YouTube IDs will be generated, much less the content inside it.\nIf the embed does not show up, the video may be deleted or was set to private. Unlisted videos are not affected.\nArchive links before it gets 404'd at https://archive.org/web```\n{link}\n```If the link is deleted/not available, you can try viewing it here:\nhttps://web.archive.org/web/https://www.youtube.com/watch?v={id}\nDo take note that this only views the webpage as it was archived during that time, and video playback is not guaranteed to work.```")
        # ```⚠️ POTENTIAL NSFW/NSFL WARNING ⚠️\nSucrose can't control what YouTube IDs will be generated, much less the content inside it.\nIf the embed does not show up, the video may be deleted or was set to private. Unlisted videos are not affected.\nArchive links before it gets 404'd at https://archive.org/web```\n

        await ctx.respond(f"{random_links[0][-11:]} {random_links[1][-11:]} {random_links[2][-11:]} {random_links[3][-11:]} {random_links[4][-11:]}\n{random_links[0]}\n{random_links[1]}\n{random_links[2]}\n{random_links[3]}\n{random_links[4]}")

def setup(bot):
    bot.add_cog(Yt_Bot(bot))
