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

@bot.hybrid_command()
async def hi(ctx):
    await ctx.send("Hello!")

@bot.hybrid_command()
async def test(ctx):
    embed1 = Embed(
            colour=Colour.ash_embed(),
            title="Project Title",
            description="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin sagittis aliquam vehicula. Nullam viverra condimentum mi blandit suscipit. Pellentesque ut elementum arcu, at commodo ante. Curabitur dolor ex, iaculis non fringilla sed, porta et massa. Nullam justo justo, rutrum in tortor sed, congue tempor diam. Mauris iaculis, sem vitae dictum."
        )
    
    embed2 = Embed(
        color=Colour.green(),
        title="Backlog (3)"
    )
    embed2.add_field(
        name="Task 1 (<@1484116579812905072>, <@1426131795405180989>)", 
        value="```Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin sagittis aliquam vehicula. Nullam viverra condimentum mi blandit suscipit. Pellentesque ut elementum arcu, at commodo ante. Curabitur dolor ex, iaculis non fringilla sed, porta et massa. Nullam justo justo, rutrum in tortor sed, congue tempor diam. Mauris iaculis, sem vitae dictum.```", 
        inline=False
        )
    embed2.add_field(
        name="Task 2 (<@1484116579812905072>, <@1426131795405180989>)", 
        value="```Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin sagittis aliquam vehicula. Nullam viverra condimentum mi blandit suscipit. Pellentesque ut elementum arcu, at commodo ante. Curabitur dolor ex, iaculis non fringilla sed, porta et massa. Nullam justo justo, rutrum in tortor sed, congue tempor diam. Mauris iaculis, sem vitae dictum.```", 
        inline=False
        )
    embed2.add_field(
        name="Task 3 (<@1484116579812905072>, <@1426131795405180989>)", 
        value="```Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin sagittis aliquam vehicula. Nullam viverra condimentum mi blandit suscipit. Pellentesque ut elementum arcu, at commodo ante. Curabitur dolor ex, iaculis non fringilla sed, porta et massa. Nullam justo justo, rutrum in tortor sed, congue tempor diam. Mauris iaculis, sem vitae dictum.```", 
        inline=False
        )

    embed3 = Embed(
        color=Colour.yellow(),
        title="In Development (1)"
    )
    embed3.add_field(
        name="Task 4 (<@1484116579812905072>, <@1426131795405180989>)", 
        value="```Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin sagittis aliquam vehicula. Nullam viverra condimentum mi blandit suscipit. Pellentesque ut elementum arcu, at commodo ante. Curabitur dolor ex, iaculis non fringilla sed, porta et massa. Nullam justo justo, rutrum in tortor sed, congue tempor diam. Mauris iaculis, sem vitae dictum.```", 
        inline=False
        )
    
    embed4 = Embed(
        color=Colour.blue(),
        title="Completed (2)"
    )
    embed4.add_field(
        name="Task 5 (<@1484116579812905072>, <@1426131795405180989>)", 
        value="```Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin sagittis aliquam vehicula. Nullam viverra condimentum mi blandit suscipit. Pellentesque ut elementum arcu, at commodo ante. Curabitur dolor ex, iaculis non fringilla sed, porta et massa. Nullam justo justo, rutrum in tortor sed, congue tempor diam. Mauris iaculis, sem vitae dictum.```", 
        inline=False
        )
    embed4.add_field(
        name="Task 6 (<@1484116579812905072>, <@1426131795405180989>)", 
        value="```Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin sagittis aliquam vehicula. Nullam viverra condimentum mi blandit suscipit. Pellentesque ut elementum arcu, at commodo ante. Curabitur dolor ex, iaculis non fringilla sed, porta et massa. Nullam justo justo, rutrum in tortor sed, congue tempor diam. Mauris iaculis, sem vitae dictum.```", 
        inline=False
        )


    await ctx.send(embeds=[embed1, embed2, embed3, embed4])

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

bot.run(os.getenv("DISCORD_TOKEN"), log_handler=handler)