# uses pycord
import random
import discord
from discord.ext import bridge, commands

bot = bridge.Bot()

class Other(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # HIDDEN COMMANDS
    # hidden because of excessive swearing. if some dumbfuck found your code on github by chance, you're shit outta luck.

    @bot.bridge_command()
    async def say(self, ctx: discord.ext.bridge.context.BridgeApplicationContext):
        """Says something random in the current channel."""
        responses = [
            # "Anemo test 6308!",
            # "Adsorption test.",
            # "死ね！",
            # f"{ctx.author.mention} is a faggot!",
            f"{ctx.author.mention} is a motherfucking faggot!",
            # "はじめまして、スクロースと申します。えっと。。。あたし、頑張る！",
            # "wala kang tite",
            # "putang ina mo",
            # f"tang ina mo {ctx.author.mention}",
            f"@everyone, bagong tuli si {ctx.author.mention}"
        ]
        await ctx.respond(random.choice(responses))

def setup(bot):
    bot.add_cog(Other(bot))
