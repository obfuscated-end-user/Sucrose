# uses pycord
# don't enable the legacy text shit on discord settings, it will fuck up the bot
import discord
import os
import random
import math
import wavelink
from dotenv import load_dotenv
from discord.ext import commands, bridge, tasks
from discord.ext.pages import Paginator, PaginatorButton, Page

load_dotenv()
bot = bridge.Bot(intents=discord.Intents.all(), command_prefix="d!")
# bot = discord.Bot(intents=discord.Intents.all(), command_prefix="d!")
guilds = [guild.id for guild in bot.guilds]
TOKEN = os.getenv("TESTING_TOKEN")

# customizing help
""" class Help(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            emby = discord.Embed(description=page)
            await destination.send(embed=emby) """
# more detailed way of doing this
class Help(commands.HelpCommand):
    """ async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Help")
        for cog, commands in mapping.items():
            command_signatures = [self.get_command_signature(c) for c in commands]
            if command_signatures:
                cog_name = getattr(cog, "qualified_name", "No Category")
                embed.add_field(name=cog_name, value="\n".join(command_signatures), inline=False)
        channel = self.get_destination()
        await channel.send(embed=embed) """
    def get_command_signature(self, command):
        # self.context.clean_prefix - the fucking prefix (d! in this case)
        # command.qualified_name - the name of the command without the prefix
        # command.signature - parameters (if any)
        return "%s%s %s" % (self.context.clean_prefix, command.qualified_name, command.signature)

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Help", color=discord.Color.blurple())

        for cog, commands in mapping.items():
            print(cog, commands)
            filtered = await self.filter_commands(commands, sort=True)
            command_signatures = [self.get_command_signature(c) for c in filtered]

            if command_signatures:
                cog_name = getattr(cog, "qualified_name", "No Category")
                embed.add_field(name=cog_name, value="\n".join(command_signatures), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_command_help(self, command):
        embed = discord.Embed(title=self.get_command_signature(command), color=discord.Color.random())
        if command.help:
            embed.description = command.help
        if alias := command.aliases:
            print("fuck ass", alias)
            embed.add_field(name="Aliases", value=", ".join(alias), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_error_message(self, error):
        embed = discord.Embed(title="Error", description=error, color=discord.Color.red())
        channel = self.get_destination()
        await channel.send(embed=embed)

bot.help_command = Help()

# EVENTS
# things that happen in the server. includes things like people joining, sending messages, joining voice chats, etc.
@bot.event
async def on_ready():
    print(f"{bot.user.name} is ready and online!")
    # bot.add_view(MyView())

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.respond("You do not have enough privileges to do this shit, cunt.")

@bot.event
async def on_member_join(member):
    # this sends a direct message (DM) to the person who joined
    await member.send(f"Welcome to the server, {member.mention}! Enjoy your stay here.")

# SLASH COMMANDS
# slash-prefixed commands that users type on the chat for the bot to receive, usually for doing something the user wants.
# USE ctx.respond() not ctx.send() YOU DUMB FUCK!
@bot.command(name="hello", description="Greets you back.")
async def hello(ctx):
    hello_quotes = [
        "Hello!",
        "Nice to meet you!",
        "Hi!",
        "sup bro you good",
    ]
    response = random.choice(hello_quotes)
    await ctx.respond(response)

@bot.slash_command(name="say", description="Says something random in the current channel.")
async def say(ctx):
    responses = [
        "Anemo test 6308!",
        "Adsorption test.",
        "死ね！",
        f"{ctx.author.name} is a faggot!",
        "はじめまして、スクロースと申します。えっと。。。あたし、頑張る！"
    ]
    response = random.choice(responses)
    await ctx.respond(response)

@bot.slash_command(name="roll_dice", description="Simulates rolling dice. Accepts two numbers as inputs.")
async def roll_dice(ctx, number_of_dice: int, number_of_sides: int):
    dice = [str(random.choice(range(1, number_of_sides + 1))) for _ in range(number_of_dice)]
    await ctx.respond(", ".join(dice))

@bot.slash_command(name="gtn", description="Guess a number from 1-10.")
async def gtn(ctx):
    """A slash command to play a guess-the-number game."""
    await ctx.respond("Guess a number between 1 and 10.")
    numbers = [number for number in range(1, 11)]
    answer = random.choice(numbers)
    guess_count = 0
    while guess_count < 3:
        # the lambda returns a boolean if the author of the message is the same as the one who used the command in chat
        guess = await bot.wait_for("message", check=lambda message: message.author == ctx.author)
        if int(guess.content) == answer:
            await ctx.send("You guessed it!")
        else:
            await ctx.send("Nope, try again")
            guess_count += 1
            if guess_count >= 3:
                await ctx.send(f"You dumb piece of shit. The number was {answer}.")

@bot.slash_command(name="embed_test", description="Test how the embed feature works on Discord.")
async def embed_test(ctx):
    embed = discord.Embed(
        title="Embed test",
        description="This is a test.",
        color=discord.Colour.red()  # a strip of color on the side of the embed, not the whole fucking box
    )
    embed.add_field(name="Normal Field 1", value="This is a normal field. Embeds also *support* **markdown**.")
    embed.add_field(name="Link test", value="[横浜's Twitter](https://twitter.com/y__k__h__m__)")

    # inline fields
    embed.add_field(name="Inline Field 1", value="Inline Field 1", inline=True)
    embed.add_field(name="Inline Field 2", value="Inline Field 2", inline=True)
    embed.add_field(name="Inline Field 3", value="Inline Field 3", inline=True)

    # misc shit
    # text below the embed. ignores markdown. supports icons.
    embed.set_footer(text="Footer. Markdown not supported here. **See?**")
    # small icon on top left
    embed.set_author(name="横浜", icon_url="https://pbs.twimg.com/profile_images/1515910444501794816/Kupakmo4_400x400.jpg")
    # large icon on top right
    embed.set_thumbnail(url="https://cdn.iconscout.com/icon/free/png-256/python-3521655-2945099.png")
    # can't see this one
    embed.set_image(url="https://icons-for-free.com/download-icon-python-1324440218937256285_256.ico")

    # the message above the embed. like, a normal user message.
    await ctx.respond("Here's an example of an embed.", embed=embed)

@bot.slash_command(name="create_channel", description="Creates a new channel from the specified name. Must have admin role in order for this to work.")
@commands.has_role("admin")
async def create_channel(ctx, channel_name="new-channel"):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if not existing_channel:
        print(f"Creating a new channel: {channel_name}")
        await guild.create_text_channel(channel_name)
        await ctx.respond(f"Created channel: {channel_name}")

# you should do bot.slash_command(), not bot.command() or some shit like that
@bot.slash_command(name="ping", description="Sends the bot's latency.")
async def ping(ctx):
    await ctx.respond(f"Ping: {int(bot.latency * 1000)}ms")

@bot.slash_command(name="add", description="Adds two numbers together.")
async def add(ctx, first: int, second: int):
    sum = first + second
    await ctx.respond(f"The sum of {first} and {second} is {sum}.")

# grouping commands
# create a group
greetings = bot.create_group("greetings", "Greet people")

# alternative way of doing this
# greetings = discord.SlashCommandGroup("greetings", "Greet people")

# notice the decorator says the name of the group instead of "bot"
@greetings.command()
async def greetings_hello(ctx):
    await ctx.respond(f"Hello, {ctx.author}")
@greetings.command()
async def greetings_bye(ctx):
    await ctx.respond(f"Bye, {ctx.author}")

# if you're using the discord.SlashCommandGroup() approach, you have to call this
# bot.add_application_command(greetings)

# USER COMMANDS
# , guild_ids=[...]
# 1066733737091530823
# @bot.user_command(name="Account Creation Date", guild_ids=[...])
# @bot.user_command(name="Account Creation Date", guild_ids=[1066733737091530823])
# @bot.user_command(name="Account Creation Date")
@bot.user_command(name="Account Creation Date", guild_ids=guilds)
async def account_creation_date(ctx, member: discord.Member):
    await ctx.respond(f"{member.name}'s account was created on {member.created_at}")

# MESSAGE COMMANDS
@bot.message_command(name="Get Message ID")
async def get_message(ctx, message: discord.Message):
    await ctx.respond(f"Message ID {message.id}")

# BUTTONS
# basic button syntax
# a class that contains all your buttons
# think of a View as some kind of container that handles all that buttons and shit, separate from plaintext messages
class MyView1(discord.ui.View):
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
    await ctx.respond("these are buttons", view=MyView1())
    # await ctx.send(f"Press the button! View persistence status: {MyView.is_persistent(MyView())}", view=MyView())


# DROPDOWNS/SELECT MENUS
class MyView2(discord.ui.View):
    # this decorator adds a select menu to the View
    @discord.ui.select(
        placeholder = "Choose a Flavor!",
        min_values = 1,
        max_values = 1,
        options = [
            discord.SelectOption (
                label = "Vanilla",
                description = "Pick this if you like vanilla!"
            ),
            discord.SelectOption (
                label = "Chocolate",
                description = "Pick this if you like chocolate!"
            ),
            discord.SelectOption (
                label = "Strawberry",
                description = "Pick this if you like strawberry!"
            ),
        ]
    )
    async def select_callback(self, select, interaction):
        # select.values[0] is the first value on the dropdown
        await interaction.response.send_message(f"Awesome, I like {select.values[0]} too!")

@bot.command()
async def flavor(ctx):
    """flavors n shit"""
    await ctx.send("Choose a flavor!", view=MyView2())

# MODAL DIALOGS
# this makes some pop out window appear on the screen and have you type inputs in it
class MyModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # the textboxes
        # default is short, 1 line only, no newlines
        self.add_item(discord.ui.InputText(label="Short input"))
        # long text style supports multiple lines, up to 4000 characters
        self.add_item(discord.ui.InputText(label="Long input", style=discord.InputTextStyle.long))

    async def callback(self, interaction: discord.Interaction):
        # after interaction with modal, use all the data gathered for an embed
        embed = discord.Embed(title="Modal results")
        # self.children returns an iterable with the textboxes you specified, and can be accessed like how you'd access a list
        embed.add_field(name="Short input", value=self.children[0].value)
        embed.add_field(name="Long input", value=self.children[1].value)
        await interaction.response.send_message(embeds=[embed])

@bot.slash_command()
async def modal_slash(ctx: discord.ApplicationContext):
    """Shows an exampke of a modal dialog being invoked from a slash command."""
    modal = MyModal(title="Modal via Slash Command")
    await ctx.send_modal(modal)

@bot.event
async def on_ready():
    very_useful_task.start()

@tasks.loop(seconds=5)
async def very_useful_task():
    print('doing very useful stuff.')

bot.run(TOKEN)