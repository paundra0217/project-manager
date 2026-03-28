from discord import Embed, Color, NotFound, Forbidden
import requests
import os
import traceback

async def get_project(ctx, id):
    try:
        response = requests.get(os.getenv("API_URL") + f'guilds/{ctx.message.guild.id}/projects/{id}')

        if response.status_code == 404:
            await ctx.send("❌ Project not found, please double check if your ID does have any typos.")
            return None
                    
        if response.status_code != 200:
            await ctx.send("❌ Unknown Error Occured, please try again later.")
            return None
            
        return response.json()['project']
    except Exception as e:
        print(e)
        traceback.print_exc()
        await ctx.send("❌ Unknown Error Occured, please try again later.")
        return None
    
async def get_list_columns(ctx, id):
    try:
        response = requests.get(os.getenv("API_URL") + f'guilds/{ctx.message.guild.id}/projects/{id}/columns')

        if response.status_code == 404:
            await ctx.send("❌ Project not found, please double check if your ID does have any typos.")
            return None
                    
        if response.status_code != 200:
            await ctx.send("❌ Unknown Error Occured, please try again later.")
            return None
            
        return response.json()
    except Exception as e:
        print(e)
        traceback.print_exc()
        await ctx.send("❌ Unknown Error Occured, please try again later.")
        return None
    
def parse_project_embed(name, description, project_id):
    embed = Embed(
        color=Color.ash_embed(),
        title=name,
        description=description,
    )
    embed.set_footer(text=f"ID: {project_id}")
        
    return embed

def parse_column_embed(name, embed_color, tasks = []):
    embed = Embed(
        title=name,
        color=int(embed_color, 16),
    )

    # TODO: Add task render here

    return embed

async def get_board_channel(bot, ctx, channel_id):
    try:
        channel = bot.get_channel(channel_id)

        if channel is None:
            channel = await bot.fetch_channel(channel_id)

        return channel
    except NotFound:
        return None
    except Forbidden:
        await ctx.send("⚠️ It looks like I do not have permission to access the channel or message where the project board lives. Double check my permissions, or change the project board channel if needed.")
        return None
    except Exception as e:
        print(e)
        traceback.print_exc()
        await ctx.send("⚠️ Cannot get channel of the project due to an unknown Error Occured.")
        return None