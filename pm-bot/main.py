# This example requires the 'message_content' intent.
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

# Load the variables from .env file
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='?', intents=intents)

@bot.event
async def on_ready():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
            
    print(f'Logged on as {bot.user}!')

@bot.hybrid_command()
async def hi(ctx):
    await ctx.send("Hello!")

bot.run(os.getenv("DISCORD_TOKEN"))