from discord import Embed, Color
import requests
import os

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