from discord import NotFound, Forbidden
from discord.ext import commands
from utils import get_project, parse_project_embed
import traceback

"""
Contains the commands relating to updating the project board on the Discord side, not in the entire application.
"""
class ProjectBoard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="update", description="Updats the project board. For editing the project, use edit command")
    async def update_project_board(self, ctx, id):
        """
        Updates the project board data by syncing it to their latest version. For editing, use the edit command

        Usage: ?update <project_id>
        """
        data = await get_project(ctx=ctx, id=id)
        if data is None:
            return
            

        prompt = await ctx.send("🔄 Updating project...")
        
        try: 
            channel_id = int(data['channel_id'])
            message_id = int(data['message_id'])
 
            board_channel = self.bot.get_channel(channel_id)

            if board_channel is None:
                board_channel = await self.bot.fetch_channel(channel_id)

            board = await board_channel.fetch_message(message_id)

            embeds = [parse_project_embed(name=data['name'], description=data['description'], project_id=data['id'])]
            await board.edit(embeds=embeds)
            await prompt.edit(content="✅ Project Board Updated! If you are looking to edit, use the `?edit <project_id>` command instead.")
        except NotFound:
            await prompt.send(content="❌ I cannot update the project board because the channel or the message where the project board is seems to be deleted. Please try to send the project board again to get automatic updates.")
        except Forbidden:
            await prompt.send(content="❌ I cannot update the project board because I do not have permission to access the channel or message where the project board lives. Double check my permissions and update the project board manually.")
        except Exception as e:
            traceback.print_exc()
            await prompt.send(content="❌ An unknown error preventing me to edit the project board. Please try updating the board manually later.")

    @update_project_board.error
    async def update_project_board_err(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Project ID is required. Format: `?update <project-id>`")
            return
        
        print(error)

async def setup(bot):
    await bot.add_cog(ProjectBoard(bot))