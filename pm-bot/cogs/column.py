from discord import NotFound, Forbidden
from discord.ext import commands
from utils import get_project, parse_project_embed, parse_column_embed, get_board_channel, get_list_columns
import traceback
import requests
import os

class ProjectColumn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="column", description="main command for all related to managing project column within a board")
    async def column_command_entry(self, ctx, type, id):
        match type:
            case "add":
                await self.add_column(ctx=ctx, project_id=id)
            case "edit":
                await self.edit_column(ctx=ctx, column_id=id)
            case "delete":
                await self.delete_column(ctx=ctx, column_id=id)
            case _:
                await ctx.send("❌ Invalid argument. Format: `?column <add|edit|delete> <project-id|column-id>`\n\n"
                           "`?column` command guide:\n"
                           "`?column add <project-id>` - Adds a new column to a project.\n"
                           "`?column edit <column-id>` - Edits a column.\n"
                           "`?column delete <column-id>` - Deletes the column, and move the task items inside the project to other column.\n")

    @column_command_entry.error
    async def column_command_err(self, ctx, err):
        if isinstance(err, commands.MissingRequiredArgument):
            await ctx.send("❌ Missing required argument. Format: `?column <add|edit|delete> <project-id|column-id>`\n\n"
                           "`?column` command guide:\n"
                           "`?column add <project-id>` - Adds a new column to a project.\n"
                           "`?column edit <column-id>` - Edits a column.\n"
                           "`?column delete <column-id>` - Deletes the column, and move the task items inside the project to other column.\n")
            return
        
        print(err)
        return
    
    async def add_column(self, ctx, project_id):
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
    
        data = await get_project(ctx=ctx, id=project_id)
        if data is None:
            return
        
        columns = await get_list_columns(ctx=ctx, id=project_id)
        if columns is None:
            return

        embed = parse_project_embed(name=data['name'], description=data['description'], project_id=data['id'])
        channel = await get_board_channel(bot=self.bot, ctx=ctx, channel_id=int(data['channel_id']))
        if channel is not None:
            embed.add_field(name="Project Board Channel", value=f"{channel.mention}")

        if columns is not None and columns["count"] >= 9:
            await ctx.send("❌ Due to Discord Embed Limitation, columns is capped at 9. Please delete existing column first before adding more.")
            return

        if columns is not None and columns["count"] > 0:
            col_value = ""
            for col in columns["columns"]:
                col_value += f"{col["name"]}\n"

            embed.add_field(name=f"Columns {columns["count"]}", value=col_value)

        olddata = await ctx.send(f"Here is the project you add a new column. Type `yes` to continue.\n"
                                 f"Note: Due to Discord Embed Limitation, columns is capped at 9. You can add {9 - columns["count"]} more column(s).", embed=embed)
        confirm = await self.bot.wait_for("message", check=check)
        if confirm.content != "yes":
            await ctx.send("❌ Adding column cancelled. If you think this is a mistake, add new column again but type `yes` when prompted to confirm.")
            await olddata.delete()
            await confirm.delete()
            return

        await ctx.send("Name of the column?")
        name_msg = await self.bot.wait_for("message", check=check)
        name = name_msg.content

        await ctx.send("Color of the column in Hexadecimal format (e.g. ABC123)?")
        desc_msg = await self.bot.wait_for("message", check=check)
        color = desc_msg.content

        message = await ctx.send("🔄 Adding column...")

        response = requests.post(
            os.getenv("API_URL") + f'guilds/{ctx.message.guild.id}/projects/{data['id']}/columns',
            json={
                'name': name,
                'color': color,
                'user': ctx.author.id
                }
            )

        if response.status_code != 201:
            await message.edit(content="❌ Cannot add column. Please try again later.")
            print(response.json())
            return
        
        columns = response.json()

        try:
            project_name = data['name']
            project_desc = data['description']
            board = await channel.fetch_message(int(data['message_id']))

            mainboard = parse_project_embed(name=project_name, description=project_desc, project_id=project_id)

            embeds = [mainboard]
            
            if columns['count'] > 0:
                for col in columns['columns']:
                    col_embed = parse_column_embed(col['name'], col['color'])
                    embeds.append(col_embed)

            await board.edit(content="", embeds=embeds)
            
        except Exception as e:
            print(e)
            traceback.print_exc()
            await ctx.send("⚠️ Unable to render project column.")

        await message.edit(
                content=f"✅ Column added."
            )
    
    async def edit_column(self, ctx, column_id):
        return
    
    async def delete_column(self, ctx, column_id):
        return

async def setup(bot):
    await bot.add_cog(ProjectColumn(bot))