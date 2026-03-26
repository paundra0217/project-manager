from discord import Embed, Color, NotFound, Forbidden
from discord.ext import commands
from datetime import datetime
from utils import get_project, parse_project_embed
import requests
import os
import traceback

"""
Contains the commands relating to managing project data within the application.
"""
class Projects(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="project", description="main command for all related to managing project data")
    async def project_command_entry(self, ctx, type, id = None):
        match type:
            case "create":
                await self.create_project(ctx=ctx)
            
            case "list":
                await self.list_projects(ctx=ctx)

            case "details":
                if id is None:
                    await ctx.send("❌ Project ID is required for `details` argument. Format: `?project details <project-id>`\n\n")
                    return
                    
                await self.project_details(ctx=ctx, id=id)

            case "edit":
                if id is None:
                    await ctx.send("❌ Project ID is required for `edit` argument. Format: `?project edit <project-id>`\n\n")
                    return
                
                await self.edit_project(ctx=ctx, id=id)

            case "archive":
                if id is None:
                    await ctx.send("❌ Project ID is required for `archive` argument. Format: `?project archive <project-id>`\n\n")
                    return
                
                await self.archive_project(ctx=ctx, id=id)
                
            case "unarchive":
                if id is None:
                    await ctx.send("❌ Project ID is required for `unarchive` argument. Format: `?project unarchive <project-id>`\n\n")
                    return
                
                await self.unarchive_project(ctx=ctx, id=id)

            case "delete":
                if id is None:
                    await ctx.send("❌ Project ID is required for `delete` argument. Format: `?project delete <project-id>`\n\n")
                    return
                
                await self.delete_project(ctx=ctx, id=id)
            
            case _:
                await ctx.send("❌ Invalid argument choice. Format: `?project <create|edit|delete|list|details> [project-id]`\n\n"
                           "`?project` command guide:\n"
                           "`?project create` - creates a new empty project.\n"
                           "`?project list` - list the projects within a server.\n"
                           "`?project details <project-id>` - view the details of the project.\n"
                           "`?project edit <project-id>` - edits a project and attempt to update the board automatically.\n"
                           "`?project archive <project-id>` - archives the project which makes it read-only and unmodifiable state.\n"
                           "`?project unarchive <project-id>` - unarchives the project which returns it to normal modifiable state.\n"
                           "`?project delete <project-id>` - deletes the project and its content, this action cannot be undone.\n")
    
    @project_command_entry.error
    async def project_command_err(self, ctx, err):
        if isinstance(err, commands.MissingRequiredArgument):
            await ctx.send("❌ Missing required argument. Format: `?project <create|edit|delete|list|details> [project-id]`\n\n"
                           "`?project` command guide:\n"
                           "`?project create` - creates a new empty project.\n"
                           "`?project list` - list the projects within a server.\n"
                           "`?project details <project-id>` - view the details of the project.\n"
                           "`?project edit <project-id>` - edits a project and attempt to update the board automatically.\n"
                           "`?project archive <project-id>` - archives the project which makes it read-only and unmodifiable state.\n"
                           "`?project unarchive <project-id>` - unarchives the project which returns it to normal modifiable state.\n"
                           "`?project delete <project-id>` - deletes the project and its content, this action cannot be undone.\n")
            return
        
        print(err)
        return
    
    async def create_project(self, ctx):
        """
        Create a new project. Usage: ?project create
        """

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
    
        await ctx.send("Name of the project?")
        name_msg = await self.bot.wait_for("message", check=check)
        name = name_msg.content

        await ctx.send("Description of the project?")
        desc_msg = await self.bot.wait_for("message", check=check)
        description = desc_msg.content

        await ctx.send("Mention the channel for the project board?")
        channel_msg = await self.bot.wait_for("message", check=check)

        # Try to resolve channel
        if channel_msg.channel_mentions:
            project_channel = channel_msg.channel_mentions[0]
        else:
            await ctx.send("❌ Channel not found or invalid. Please mention the channel by using `#` then select the channel, and not by typing the channel name without the `#`.")
            return

        message = await ctx.send("🔄 Creating project...")

        # Create project
        board = await project_channel.send("🔄 Creating project...")

        try:
            response = requests.post(
            os.getenv("API_URL") + 'projects/',
            json={
                'name': name,
                'description': description,
                'guild_id': ctx.message.guild.id,
                'channel_id': project_channel.id,
                'message_id': board.id,
                'updated_by': ctx.author.id
                }
            )

            if response.status_code == 409:
                await message.edit(content="❌ Channel already used by other project. Please mention other channel that is unused.")
                await board.delete()
                return

            if response.status_code != 201:
                print(response.json())
                await message.edit(content="❌ Cannot create project. Please try again later.")
                await board.delete()
                return
            
            project_id = response.json()['id']

            await board.edit(content="", embed=parse_project_embed(name=name, description=description, project_id=project_id))

            embed = parse_project_embed(name=name, description=description, project_id=project_id)
            embed.add_field(name="Project Board Channel", value=f"{project_channel.mention}")

            await message.edit(
                content=f"✅ Project created! Please take note of the project ID for manipulating project's content (e.g. task items, project column, etc.). Project ID can also be found in the project board.",
                embed=embed
            )
        except:
            await message.edit(content="❌ Cannot create project. Please try again later.")
            await board.delete()
            return

    async def list_projects(self, ctx):
        """
        Lists all the projects within a server. Usage: ?project list
        """
        response = requests.get(os.getenv("API_URL") + f'projects/list/{ctx.message.guild.id}')

        if response.status_code != 200:
            await ctx.send("❌ Cannot obtain list of projects, please try again later.")
            return

        embed = Embed(
            color=Color.ash_embed(),
            title=f"Active Projects for {ctx.message.guild.name}",
        )

        for project in response.json()['projects']:
            iso_time = project['created_at']
            dt = datetime.fromisoformat(iso_time.replace("Z", "+00:00"))
            unix_timestamp = int(dt.timestamp())

            embed.add_field(name=f"{project['name']} ({project['id']})", 
                            value=
                                f"Created: <t:{unix_timestamp}:F>\n"
                                f"```{project['description']}```\n",
                            inline=False
                            )

        await ctx.send("Only first 25 projects are displayed", embed=embed)
        return

    async def project_details(self, ctx, id):
        """
        Get a project details based on the ID. Usage: ?project details <project-id> 
        """
        data = await get_project(ctx=ctx, id=id)
        if data is None:
            return
        
        channel = None
        try:
            old_channel_id = int(data['channel_id'])
            channel = self.bot.get_channel(old_channel_id)

            if channel is None:
                channel = await self.bot.fetch_channel(old_channel_id)
        except NotFound:
            pass
        except Forbidden:
            await ctx.send("⚠️ It looks like I do not have permission to access the channel or message where the project board lives. Double check my permissions, or change the project board channel if needed.")
        except Exception as e:
            traceback.print_exc()
            await ctx.send("⚠️ Cannot get channel of the project due to an unknown Error Occured.")

        embed = parse_project_embed(name=data['name'], description=data['description'], project_id=data['id'])
        if channel is not None:
            embed.add_field(name="Project Channel Board", value=f"{channel.mention}")

        await ctx.send(f"Project Details for {data['name']}", embed=embed)

    async def edit_project(self, ctx, id):
        """
        Edits a project and automatically updates the project board if available. Usage: ?project edit <project_id>
        """
        
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        data = await get_project(ctx=ctx, id=id)
        if data is None:
            return
        
        if data['is_archived']:
            await ctx.send("❌ This project is archived, meaning it is in read-only and unmodifiable state. If you want to edit this project, unarchive first by using `?project unarchive <project-id>` command.")
            return

        name = data['name']
        description = data['description']
        old_board_id = data['message_id']
        channel = None

        try:
            old_channel_id = int(data['channel_id'])
            channel = self.bot.get_channel(old_channel_id)

            if channel is None:
                channel = await self.bot.fetch_channel(old_channel_id)
        except NotFound:
            pass
        except Forbidden:
            await ctx.send("⚠️ It looks like I do not have permission to access the channel or message where the project board lives. Double check my permissions, or change the project board channel instead.")
        except Exception as e:
            traceback.print_exc()
            await ctx.send("⚠️ Cannot get channel of the project due to an unknown Error Occured.")

        embed = parse_project_embed(name=name, description=description, project_id=data['id'])
        if channel is not None:
            embed.add_field(name="Project Board Channel", value=f"{channel.mention}")

        olddata = await ctx.send(f"Here is the project you want to edit. Type `yes` to continue.", embed=embed)
        confirm = await self.bot.wait_for("message", check=check)
        if confirm.content != "yes":
            await ctx.send("❌ Edit cancelled. If you think this is a mistake, edit again but type `yes` when prompted to confirm.")
            await olddata.delete()
            await confirm.delete()
            return
    
        await confirm.delete()

        while True:
            editmenu = await ctx.send(
                "Which project property you want to edit?\n\n"
                "`name` for project name\n"
                "`desc` for project description\n"
                "`chan` for project board channel\n"
                "`done` for apply changes\n"
                "`exit` for cancel edit\n"
                )
            
            selection = await self.bot.wait_for("message", check=check)

            match selection.content:
                case "name":
                    await selection.delete()
                    
                    menu = await ctx.send("New name of the project?")
                    name_msg = await self.bot.wait_for("message", check=check)
                    name = name_msg.content

                    await name_msg.delete()
                    await editmenu.delete()
                    await menu.edit(content="Name changed")

                case "desc":
                    await selection.delete()

                    menu = await ctx.send("New description of the project?")
                    desc_msg = await self.bot.wait_for("message", check=check)
                    description = desc_msg.content

                    await desc_msg.delete()
                    await editmenu.delete()
                    await menu.edit(content="Description changed")

                case "chan":
                    await selection.delete()

                    menu = await ctx.send("Mention the new channel of where the project board located?")
                    channel_msg = await self.bot.wait_for("message", check=check)
                    if channel_msg.channel_mentions:
                        channel = channel_msg.channel_mentions[0]
                        await channel_msg.delete()
                        await menu.edit(content="Channel changed")
                    else:
                        await ctx.send("❌ Channel not found or invalid. Please mention the channel by using `#` then select the channel, and not by typing the channel name without the `#`.")
                    await editmenu.delete()

                case "done":
                    await editmenu.delete()
                    await selection.delete()

                    embed = parse_project_embed(name=name, description=description, project_id=data['id'])
                    if channel is not None:
                        embed.add_field(name="Project Board Channel", value=f"{channel.mention}")

                    menu = await ctx.send("Please confirm the edited project. To apply changes, type `yes`.", embed=embed)
                    edit_confirm = await self.bot.wait_for("message", check=check)
                    if edit_confirm.content == "yes":
                        await menu.edit(content="🔄 Applying changes...", embeds=[])
                        await edit_confirm.delete()

                        new_board = None

                        # Sends the changes to the API first
                        if channel.id == old_channel_id:
                            response = requests.patch(
                            os.getenv("API_URL") + f'projects/{id}',
                            json={
                                'name': name,
                                'description': description,
                                'updated_by': ctx.author.id
                                }
                            )
                        else:
                            new_board = await channel.send(content="🔄 Rendering new Project Board...")
                            response = requests.patch(
                            os.getenv("API_URL") + f'projects/{id}',
                            json={
                                'name': name,
                                'description': description,
                                'channel_id': channel.id,
                                'message_id': new_board.id,
                                'updated_by': ctx.author.id
                                }
                            )
                        if response.status_code == 409:
                            await new_board.delete()
                            await menu.edit(content="❌ The channel is already used by other project. Please mention other channel.")
                            continue

                        if response.status_code != 200:
                            await menu.edit(content="❌ Unknown Error Occured, please try again later.")
                            return
                        
                        await olddata.delete()
                        new_data = response.json()['project']
                        
                        # Attempting to edit or delete and resend the project board
                        if channel.id == old_channel_id:
                            # if the channel is unchanged...
                            try:
                                # if the channel is unchanged...
                                channel_id = int(new_data['channel_id'])
                                message_id = int(new_data['message_id'])
                                    
                                board_channel = self.bot.get_channel(channel_id)

                                if board_channel is None:
                                    board_channel = await self.bot.fetch_channel(channel_id)

                                board = await board_channel.fetch_message(message_id)

                                embeds = [parse_project_embed(name=new_data['name'], description=new_data['description'], project_id=new_data['id'])]
                                await board.edit(embeds=embeds)
                                    
                            except NotFound:
                                await ctx.send("⚠️ I cannot update the project board because the channel or the message where the project board is seems to be deleted. Please try to send the project board again to get automatic updates.")
                            except Forbidden:
                                await ctx.send("⚠️ I cannot update the project board because I do not have permission to access the channel or message where the project board lives. Double check my permissions and update the project board manually.")
                            except Exception as e:
                                traceback.print_exc()
                                await ctx.send("⚠️ An unknown error preventing me to edit the project board. Please try updating the board manually later.")
                        
                            await menu.edit(content="✅ Changes applied and project board updated!")
                        else:
                            #if the channel is changed...
                            try:     
                                # delete the old board                               
                                old_board_channel = self.bot.get_channel(old_channel_id)

                                if old_board_channel is None:
                                    old_board_channel = await self.bot.fetch_channel(old_channel_id)

                                board = await old_board_channel.fetch_message(old_board_id)
                                await board.delete()
                            except NotFound:
                                pass
                            except Forbidden:
                                await ctx.send("⚠️ I cannot delete the old project board because I do not have permission to access the channel where the old project board lives. Double check my permissions and delete the project board in the old channel.")
                            except Exception as e:
                                traceback.print_exc()
                                await ctx.send("⚠️ An unknown error preventing me to edit the project board. Please try updating the board manually later.")
                            # send the new board
                            if new_board is not None:
                                embeds = [parse_project_embed(name=new_data['name'], description=new_data['description'], project_id=new_data['id'])]
                                await new_board.edit(content="", embeds=embeds)

                            await menu.edit(content="✅ Changes applied and project board has been moved to the new channel!")
                        
                        return
                    else:
                        await edit_confirm.delete()
                        await menu.edit(content="❌ Changes unapplied. If you think this is a mistake, apply changes again but type `yes` when prompted to confirm.")

                case "exit":
                    await selection.delete()
                    await olddata.delete()
                    await editmenu.edit(content="Edit cancelled")
                    return

                case _:
                    await selection.delete()
                    await editmenu.edit(content="Invalid selection")

    async def archive_project(self, ctx, id):
        """
        Archives the project. Usage: ?project archive <project_id>
        """
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        data = await get_project(ctx=ctx, id=id)
        if data is None:
            return
        
        if data['is_archived']:
            await ctx.send("❌ Project already archived!")
            return
        
        channel = None
        try:
            old_channel_id = int(data['channel_id'])
            channel = self.bot.get_channel(old_channel_id)

            if channel is None:
                channel = await self.bot.fetch_channel(old_channel_id)
        except NotFound:
            pass
        except Forbidden:
            await ctx.send("⚠️ It looks like I do not have permission to access the channel or message where the project board lives. Double check my permissions, or change the project board channel before archiving.")
        except Exception as e:
            traceback.print_exc()
            await ctx.send("⚠️ Cannot get channel of the project due to an unknown Error Occured.")

        embed = parse_project_embed(name=data['name'], description=data['description'], project_id=data['id'])
        if channel is not None:
            embed.add_field(name="Project Channel Board", value=f"{channel.mention}")

        prompt = await ctx.send(f"You are about to archiving this project, which makes the project in read-only and unmodifiable state, including editing project details and managing tasks. Type `{data['name']}` to continue.", embed=embed)
        confirm = await self.bot.wait_for("message", check=check)
        if confirm.content != data['name']:
            await ctx.send(f"❌ Deletion cancelled. If you think this is a mistake, delete again but type `{data['name']}` when prompted to confirm.")
            await prompt.delete()
            await confirm.delete()
            return
        
        await prompt.edit(content="🔄 Archiving project...", embeds=[])    
        await confirm.delete()

        response = requests.patch(os.getenv("API_URL") + f'projects/{id}', json={
            'user': ctx.author.id,
            "is_archived": True
        })

        if response.status_code != 200:
            await prompt.edit(content="❌ Unknown Error Occured, please try again later.")
            return
        
        await prompt.edit(content="✅ Project archived!")

    async def unarchive_project(self, ctx, id):
        data = await get_project(ctx=ctx, id=id)
        if data is None:
            return
        
        if data['is_archived'] is False:
            await ctx.send("❌ Project is not archived!")
            return

        prompt = await ctx.send("🔄 Unarchiving project...")    

        response = requests.patch(os.getenv("API_URL") + f'projects/{id}', json={
            'user': ctx.author.id,
            "is_archived": False
        })

        if response.status_code != 200:
            await prompt.edit(content="❌ Unknown Error Occured, please try again later.")
            return

        await prompt.edit(content="✅ Project unarchived!")

    async def delete_project(self, ctx, id):
        """
        Deletes the project board and its content. Usage: ?project delete <project_id>
        """
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        data = await get_project(ctx=ctx, id=id)
        if data is None:
            return

        channel = None
        try:
            old_channel_id = int(data['channel_id'])
            channel = self.bot.get_channel(old_channel_id)

            if channel is None:
                channel = await self.bot.fetch_channel(old_channel_id)
        except NotFound:
            pass
        except Forbidden:
            await ctx.send("⚠️ It looks like I do not have permission to access the channel or message where the project board lives. Double check my permissions.")
        except Exception as e:
            traceback.print_exc()
            await ctx.send("⚠️ Cannot get channel of the project due to an unknown Error Occured.")

        embed = parse_project_embed(name=data['name'], description=data['description'], project_id=data['id'])
        if channel is not None:
            embed.add_field(name="Project Channel Board", value=f"{channel.mention}")

        prompt = await ctx.send(f"You are about to delete this project, which means **deleting the project and it's contents including tasks forever and this action cannot be undone!** Consider archiving the project instead. Type `{data['name']}` to continue.", embed=embed)
        confirm = await self.bot.wait_for("message", check=check)
        if confirm.content != data['name']:
            await prompt.edit(content=f"❌ Deletion cancelled. If you think this is a mistake, delete again but type `{data['name']}` when prompted to confirm. You may want to conside archiving the project instead because deletion cannot be undone.", embeds=[])
            await confirm.delete()
            return

        await prompt.edit(content="🔄 Deleting project...", embeds=[])    
        await confirm.delete()

        response = requests.delete(os.getenv("API_URL") + f'projects/{id}')
        if response.status_code != 204:
            await prompt.edit("❌ Unknown Error Occured, please try again later.")
            return

        try:                            
            channel_id = int(data['channel_id'])
            message_id = int(data['message_id'])
 
            board_channel = self.bot.get_channel(channel_id)

            if board_channel is None:
                board_channel = await self.bot.fetch_channel(channel_id)

            board = await board_channel.fetch_message(message_id)

            await board.delete()
        except NotFound:
            await ctx.send("⚠️ I cannot delete the project board because the channel or the message where the project board is seems to be deleted. Search the project board if still available delete the project board manually. If it's deleted manually beforehand, then there's no further action required and you can safely ignore this warning.")
        except Forbidden:
            await ctx.send("⚠️ I cannot delete the project board because I do not have permission to access the channel or message where the project board lives. Double check my permissions and delete the project board manually.")
        except Exception as e:
            traceback.print_exc()
            await ctx.send("⚠️ An unknown error preventing me to delete the project board. Please delete the board manually.")
        
        await prompt.edit(content="✅ Project deleted!")

async def setup(bot):
    await bot.add_cog(Projects(bot))