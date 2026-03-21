from discord import Intents, Colour, Embed, Object
import logging
from discord.ext import commands
from dotenv import load_dotenv
import os

# Load the variables from .env file
load_dotenv()

intents = Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='?', intents=intents)

@bot.event
async def on_ready():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
            
    guild = Object(id=os.getenv("DEV_GUILD_ID"))
    await bot.tree.sync(guild=guild)
    print(f'Logged on as {bot.user}!')

# Test command to make sure the bot is online
@bot.hybrid_command()
async def hi(ctx):
    await ctx.send("Hello!")

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

bot.run(os.getenv("DISCORD_TOKEN"), log_handler=handler)