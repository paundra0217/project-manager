from discord import NotFound, Forbidden
from discord.ext import commands
from utils import get_project, parse_project_embed
import traceback
import requests
import os

"""
Contains the commands relating to updating the project board on the Discord side, not in the entire application.
"""
class ProjectBoard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="update", description="Updats the project board. For editing the project, use edit command")
    async def update_project_board(self, ctx, id):
        """
        Updates the project board data by syncing it to their latest version. For editing, use the edit command. Usage: ?update <project_id>
        """
        data = await get_project(ctx=ctx, id=id)
        if data is None:
            return
            
        prompt = await ctx.send("🔄 Updating project board...")
        
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

    @commands.hybrid_command(name="resend", description="Resends the project board if the board is accidentally deleted")
    async def resend_project_board(self, ctx, id):
        """
        Resends the project board data to an existing channel. Usage: ?resend <project_id>
        """
        data = await get_project(ctx=ctx, id=id)
        if data is None:
            return
        
        prompt = await ctx.send("🔄 Resending project board...")

        channel_id = int(data['channel_id'])
        message_id = int(data['message_id'])
        board_channel = None

        # locate existing board channel
        try: 
            print("locating board message")
            board_channel = self.bot.get_channel(channel_id)
            if board_channel is None:
                board_channel = await self.bot.fetch_channel(channel_id)
        except NotFound:
            await prompt.edit(content="❌ I cannot resend the project board because the channel of project board is seems to be deleted. Please edit the channel of the project by using `?project edit <project_id>` command.")
        except Forbidden:
            await prompt.edit(content="❌ I cannot resend the project board because I do not have permission to access the channel of the project board. Double check my permissions and resend the project board again, or edit the channel of the project by using `?project edit <project_id>` command.")
        except Exception as e:
            traceback.print_exc()
            await prompt.edit(content="❌ An unknown error preventing me to resend the project board. Please try resending the board later.")

        # locate existing board message
        try:
            print("locating board message")
            board = await board_channel.fetch_message(message_id)
            if board is not None:
                await prompt.edit(content="⚠️ Project Board already existed! If you are looking to update, use the `?update <project_id>` command instead.")
                return
        except NotFound:
            pass # this is intended, because resending require the project board to be non-existant.
        except Forbidden:
            await prompt.edit(content="❌ I cannot resend the project board because I do not have permission to access the channel of the project board. Double check my permissions and resend the project board again, or edit the channel of the project by using `?project edit <project_id>` command.")
        except Exception as e:
            traceback.print_exc()
            await prompt.edit(content="❌ An unknown error preventing me to resend the project board. Please try resending the board later. If you are looking to edit the channel of the project, use the `?project edit <project_id>` command instead.")

        # attemping resend project board
        try:
            print("resending project board")
            board = await board_channel.send("🔄 Resending project board...")

            response = requests.patch(
                os.getenv("API_URL") + f'projects/{id}',
                json={
                    'message': board.id,
                    'user': ctx.author.id
                    }
                )
            
            if response.status_code != 200:
                await ctx.send("❌ Unknown Error Occured, please try again later.")
                await board.delete()
                return
            
            embeds = [parse_project_embed(name=data['name'], description=data['description'], project_id=data['id'])]
            await board.edit(content="", embeds=embeds)
            await prompt.edit(content="✅ Project Board Resent! If you are looking to edit the channel of the project, use the `?project edit <project_id>` command instead.")
        except Exception as e:
            traceback.print_exc()
            await prompt.send(content="❌ An unknown error preventing me to resend the project board. Please try resending the board later. If you are looking to edit the channel of the project, use the `?project edit <project_id>` command instead.")
            await board.delete()
    
    @resend_project_board.error
    async def resend_project_board_err(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Project ID is required. Format: `?resend <project-id>`")
            return
        
        print(error)


    async def locate_project_board(self, ctx, id):
        data = await get_project(ctx=ctx, id=id)
        if data is None:
            return
        
        prompt = await ctx.send("🔄 Locating project board...")

        guild_id = int(data['guild_id'])
        channel_id = int(data['channel_id'])
        message_id = int(data['message_id'])

        try: 
            print("locating board message")
            board_channel = self.bot.get_channel(channel_id)
            if board_channel is None:
                board_channel = await self.bot.fetch_channel(channel_id)

            board = await board_channel.fetch_message(message_id)
            board_url = f"https://discord.com/channels/{guild_id}/{channel_id}/{message_id}"

            await prompt.edit(content=f"✅ Project Board located, it is located here: {board_url}")
        except NotFound:
            await prompt.edit(content="❌ I cannot locate the project board because the message of the project board is seems to be deleted. Please resend the project board by using `?resend <project_id>` command.")
        except Forbidden:
            await prompt.edit(content="❌ I cannot locate the project board because I do not have permission to access the channel of the project board. Double check my permissions and locate the project board again.")
        except Exception as e:
            traceback.print_exc()
            await prompt.edit(content="❌ An unknown error preventing me to locate the project board. Please try locating the board later.")

        return


async def setup(bot):
    await bot.add_cog(ProjectBoard(bot))