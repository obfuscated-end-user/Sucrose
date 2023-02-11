# uses pycord
# don't enable the legacy text shit on discord settings, it will fuck up the bot
import discord
import os
import random
import math
from dotenv import load_dotenv
from discord.ext import commands
from discord.ext import bridge  # for both slash and text-based command support

load_dotenv()
bot = bridge.Bot(intents=discord.Intents.all(), command_prefix="s!")
guilds = [guild.id for guild in bot.guilds]
TOKEN = os.getenv("TESTING_TOKEN")

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
@bot.bridge_command(name="hello", description="Greets you back.")
async def hello(ctx):
    hello_quotes = [
        "Hello!",
        "Nice to meet you!",
        "Hi!",
        "sup bro you good",
    ]
    response = random.choice(hello_quotes)
    await ctx.respond(response)

@bot.bridge_command(name="say", description="Says something random in the current channel.")
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

@bot.bridge_command(name="roll_dice", description="Simulates rolling dice. Accepts two numbers as inputs.")
async def roll_dice(ctx, number_of_dice: int, number_of_sides: int):
    dice = [str(random.choice(range(1, number_of_sides + 1))) for _ in range(number_of_dice)]
    await ctx.respond(", ".join(dice))

@bot.bridge_command(name="gtn", description="Guess a number from 1-10.")
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

@bot.bridge_command(name="embed_test", description="Test how the embed feature works on Discord.")
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

@bot.bridge_command(name="create_channel", description="Creates a new channel from the specified name. Must have admin role in order for this to work.")
@commands.has_role("admin")
async def create_channel(ctx, channel_name="new-channel"):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if not existing_channel:
        print(f"Creating a new channel: {channel_name}")
        await guild.create_text_channel(channel_name)
        await ctx.respond(f"Created channel: {channel_name}")

@bot.bridge_command(name="ping", description="Sends the bot's latency.")
async def ping(ctx):
    await ctx.respond(f"Ping: {int(bot.latency * 1000)}ms")

@bot.slash_command(name="add", description="Adds two numbers together.")
async def add(ctx, first: int, second: int):
    sum = first + second
    await ctx.respond(f"The sum of {first} and {second} is {sum}.")

greetings = bot.create_group("greetings", "Greet people")
@greetings.command()
async def greetings_hello(ctx):
    await ctx.respond(f"Hello, {ctx.author}")
@greetings.command()
async def greetings_bye(ctx):
    await ctx.respond(f"Bye, {ctx.author}")

# USER COMMANDS
@bot.user_command(name="Account Creation Date", guild_ids=guilds)
async def account_creation_date(ctx, member: discord.Member):
    await ctx.respond(f"{member.name}'s account was created on {member.created_at}")

# MESSAGE COMMANDS
@bot.message_command(name="Get Message ID")
async def get_message(ctx, message: discord.Message):
    await ctx.respond(f"Message ID {message.id}")

# BUTTONS
class MyView(discord.ui.View):
    def __init__(self):
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

    @discord.ui.button(label="button 5", style=discord.ButtonStyle.blurple, emoji="😎")
    async def button_callback5(self, button, interaction):
        button.disabled = True
        button.label = "disabled"
        await interaction.response.edit_message(view=self)

@bot.slash_command(name="button")
async def button(ctx):
    await ctx.respond("these are buttons", view=MyView())

bot.run(TOKEN)