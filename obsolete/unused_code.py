# DO NOT RUN
# the imports and variables are here for compatibility reasons
import discord
import os
import random
import math
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
bot = discord.Bot(intents=discord.Intents.all())
guilds = [guild.id for guild in bot.guilds]
TOKEN = os.getenv("TOKEN")


# HUGE CHUNK OF SHIT
# https://guide.pycord.dev/interactions/application-commands/localizations
@bot.slash_command(
    name="ping",
    name_localizations={
        "en-GB": "British_Ping"
    },
    description="Ping the bot",
    description_localizations={
        "en-GB": "British ping the bot"
    },
    options=[
        Option(
            name="Example",
            name_localizations={
                "en-GB": "British Example"
            },
            description="Example option that does nothing",
            description_localizations={
                "en-GB": "British example option that does nothing"
            }
        )
    ]
)
async def ping(ctx, example):
    responses = {"en-US": "Pong!",
                 "en-GB": "British Pong!"}
    await ctx.respond(responses.get(ctx.interaction.locale, responses["en-US"]))

@bot.slash_command(
    name="ping2",
    name_localizations={
        "en-GB": "British_Ping"
    },
    description="Ping the bot",
    description_localizations={
        "en-GB": "British ping the bot"
    }
)
async def ping2(ctx, example: Option(str, "example", name_localizations={"en-GB": "British Example"}, description="Example option that does nothing", description_localization={"en-GB": "British example option that does nothing"})):
    responses = {"en-US": "Pong2!",
                 "en-GB": "British Pong2!"}
    await ctx.respond(responses.get(ctx.interaction.locale, responses["en-US"]))

# subgroup example
math_group = discord.SlashCommandGroup("math", "Math-related commands")
advanced_math = math_group.create_subgroup("advanced", "Advanced math commands")

advanced_math.command()
async def square_root(ctx, x: int):
    await ctx.respond(math.sqrt(x))

bot.add_application_command(math_group)

# autocomplete
async def get_animal_types(ctx: discord.AutocompleteContext):
    """
    Here we will check if 'ctx.options['animal_type']' is and check if it's a marine or land animal and return specific option choices
    """
    animal_type = ctx.options['animal_type']
    if animal_type == 'Marine':
        return ['Whale', 'Shark', 'Fish', 'Octopus', 'Turtle']
    else: # is land animal
        return ['Snake', 'Wolf', 'Lizard', 'Lion', 'Bird']

@bot.slash_command(name="animal")
async def animal_command(ctx: discord.ApplicationContext, animal_type: discord.Option(str, choices=['Marine', 'Land']), animal: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_animals)):
    await ctx.respond(f'You picked an animal type of `{animal_type}` that led you to pick `{animal}`!')
""" async def get_animal_types(ctx: discord.AutocompleteContext):
    animal_type = ctx.options["animal_type"]
    if animal_type == "Marine":
        return ["whale", "shark", "fish", "octopus", "turtle"]
    else:
        return ["snake", "wolf", "lizard", "lion", "bird"]
@bot.slash_command(name="animal")
async def animal(ctx: discord.ApplicationContext, animal_type: discord.Option(str, choices=["Marine", "Land"]), animal: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_animals))): """

@bot.bridge_command(name="help", description="Help.")
async def help(ctx):
    embed = discord.Embed(title="Help", description="Commands.", color=discord.Colour.blurple())
    embed.add_field(name="hello", value=str(hello.__doc__))
    await ctx.respond("", embed=embed)

# BUTTONS
# basic button syntax
# a class that contains all your buttons
# think of a View as some kind of container that handles all that buttons and shit, separate from plaintext messages
class MyView(discord.ui.View):
    def __init__(self):
        # if you want a persistent View (buttons still work even if bot is offline):
        # set timeout to None
        # set a custom_id for each button
        # spoiled alert: doens't do shit for me
        super().__init__(timeout=None)

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        await self.message.edit(content="you yook to long. disabled all the components", view=self)

    @discord.ui.button(label="button 1", custom_id="button-1", style=discord.ButtonStyle.red, emoji="😎")
    async def button_callback1(self, button, interaction):
        await interaction.response.send_message(("you clicked the first button"))

    @discord.ui.button(label="button 2", style=discord.ButtonStyle.green, emoji="😎")
    async def button_callback2(self, button, interaction):
        await interaction.response.send_message(("you clicked the second button"))
    
    @discord.ui.button(label="button 3", style=discord.ButtonStyle.blurple, emoji="😎")
    async def button_callback3(self, button, interaction):
        await interaction.response.send_message(("you clicked the third button"))
    
    @discord.ui.button(label="button 4", style=discord.ButtonStyle.blurple, disabled=True, emoji="😎")
    async def button_callback4(self, button, interaction):
        await interaction.response.send_message(("how the fuck did you make this show up"))

    # disables on press
    @discord.ui.button(label="button 5", style=discord.ButtonStyle.blurple, emoji="😎")
    async def button_callback5(self, button, interaction):
        # await interaction.response.send_message(("you clicked the fifth button"))
        button.disabled = True
        button.label = "disabled"
        await interaction.response.edit_message(view=self)

# this command will show all the buttons
@bot.slash_command(name="button")
async def button(ctx):
    await ctx.respond("these are buttons", view=MyView())
    # await ctx.send(f"Press the button! View persistence status: {MyView.is_persistent(MyView())}", view=MyView())

# PAGINATOR
my_pages = [
    Page(
        content="First page. Has a message and an embed.",
        embeds=[
            discord.Embed(title="first embed"),
            discord.Embed(title="second embed")
        ]
    ),
    Page(
        content="Second page. Only contains a message."
    ),
    Page(
        embeds=[
            discord.Embed(
                title="Third page. Only contains an embed.",
                description="No message content."
            )
        ]
    ),
]

paginator_buttons = [
    PaginatorButton("first", label="<<", style=discord.ButtonStyle.green),
    PaginatorButton("prev", label="<", style=discord.ButtonStyle.green),
    PaginatorButton("page_indicator", style=discord.ButtonStyle.gray, disabled=True),
    PaginatorButton("next", label=">", style=discord.ButtonStyle.green),
    PaginatorButton("last", label=">>", style=discord.ButtonStyle.green),
]

paginator = Paginator(
                pages=my_pages,
                show_indicator=True,
                use_default_buttons=False,
                custom_buttons=paginator_buttons
            )

@bot.command()
async def send_paginator(ctx, paginator):
    await ctx.respond(paginator)

@bot.bridge_command()
async def stop(ctx):
    """Stops the current song. Stopped song cannot be resumed afterwards."""
    vc = ctx.voice_client
    if not vc: # if not in voice channel
        print(f"{ctx.author.name} ran stop but they're not in a voice channel")
        await ctx.respond("You must be in the same voice channel as the bot to stop the current song.")
    if not vc.is_playing(): # if song is not playing
        print(f"{ctx.author.name} ran stop but no song is playing.")
        await ctx.respond("No song is playing.")
    if vc.is_playing(): # if song is playing, stop
        await vc.stop()
        await ctx.respond(f"Stopped playing `{song_title}`.")
        print(f"{ctx.author.name} ran stop\nsong stopped: {song_title}\nsong state: {vc.is_playing()}")

@bot.bridge_command()
async def pause(ctx):
    """Pauses the current song. Use s!resume to resume playing the song."""
    vc = ctx.voice_client
    if not vc: # if not in voice channel
        print(f"{ctx.author.name} ran pause but they're not in a voice channel")
        await ctx.respond("Nothing to pause if you're not in a voice channel.")
    if vc.is_paused(): # if song is paused
        print(f"{ctx.author.name} ran pause but song is already paused.")
        return
        # await ctx.respond("Song is already paused. Type `s!resume` to resume playback.")
    if not vc.is_playing(): # if song is not playing
        print(f"{ctx.author.name} ran pause but the bot is not playing anything.")
        await ctx.respond("Bot is not playing anything.")
    if vc.is_playing(): # if song is playing, pause
        await vc.pause()
        await ctx.respond(f"Paused `{vc.source.title}`.")
        print(f"{ctx.author.name} ran stop\npaused song: {vc.source.title}\nsong state: {vc.is_playing()}")

@bot.bridge_command()
async def resume(ctx):
    """Resumes the current paused song. Does nothing if the current song is playing."""
    vc = ctx.voice_client
    if not vc: # if not in voice channel
        print(f"{ctx.author.name} ran resume but they're not in a voice channel")
        await ctx.respond("You must be in the same voice channel as the bot to use this command.")
    if vc.is_paused(): # if song is paused, resume
        await vc.resume()
        await ctx.respond(f"Resumed playing `{vc.source.title}`.")
        print(f"{ctx.author.name} ran resume\nsong resumed: {vc.source.title}\nsong state: {vc.is_playing()}")
    if vc.is_playing(): # if song is playing
        print(f"{ctx.author.name} ran resume but song is already playing.")
        return
        # await ctx.respond("Song is already playing.")
    if not vc.is_playing(): # if song is not playing
        print(f"{ctx.author.name} ran resume but no song is playing.")
        await ctx.respond("No song is playing.")
    """ elif not vc.is_playing(): # if song is not playing, resume
        await vc.resume()
        await ctx.respond(f"Resumed playing `{vc.source.title}`.")
        print(f"{ctx.author.name} ran resume\nsong resumed: {vc.source.title}\nsong state: {vc.is_playing()}") """

        @bot.bridge_command(aliases=["connect", "enter", "join"])
    async def voice_connect(self, ctx):
        """Joins your voice channel."""
        vc = ctx.voice_clients
        if not vc:
            vc = await ctx.author.voice.channel.connect()
        
    @bot.bridge_command(aliases=["disconnect", "out", "leave"])
    async def voice_disconnect(self, ctx):
        """Leaves your voice channel."""
        vc = ctx.voice_clients
        for v in vc:
            return await v.disconnect()
        # await ctx.voice_clients.disconnect()
        if vc:
            return await ctx.author.voice.channel.disconnect()

    @bot.bridge_command(aliases=["connect", "enter", "join"])
    async def voice_connect(self, ctx):
        """Joins your voice channel."""
        vc = ctx.guild.voice_client
        if not vc:
            # print("cunt ass")
            await vc.connect()

song = ""
        if "https://www.youtube.com/playlist?list=" in search:
            # FUCKING REMEMBER THAT SONG IS A LIST IN THIS CONTEXT
            song = await wavelink.YouTubePlaylist.search(query=f"\"{search}\"")
            print("Do nothing:")
            print(type(song))
            """ for track in song:
                self.song_queue.append(track) """
        else:
            song = await wavelink.YouTubeTrack.search(query=f"\"{search}\"", return_first=True)