# put the quotes with swearing in this file and the search redirect shit you want to do later.
# for example:
# s!p https://open.spotify.com/track/4z1O8W35JfmFjPlD9KYvid?si=68a50816a7dc40d7
# should be substituted with
# s!p zIghUDfX2RY
"""
songs:
the song mentioned above
anything by dots tokyo
"""

import discord

ctx = discord.ext.bridge.context.BridgeApplicationContext

sucrose_greetings = [
    "Hello!",
    "Nice to meet you!",
    "Hi!",
    "sup bro you good"
]

sucrose_random = [
    # "Anemo test 6308!",
    # "Adsorption test.",
    # "死ね！",
    f"{ctx.author.name} is a faggot!",
    # "はじめまして、スクロースと申します。えっと。。。あたし、頑張る！",
    # "wala kang tite",
    # "putang ina mo",
    f"tang ina mo {ctx.author.name}"
]

sucrose_search_redirect = {
    
}