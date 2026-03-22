from discord import Embed, Color, NotFound, Forbidden
from discord.ext import commands
import requests
import os
import traceback

class Projects(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def parse_project_embed(self, name, description, project_id):
        embed = Embed(
            color=Color.ash_embed(),
            title=name,
            description=description,
        )
        embed.set_footer(text=f"ID: {project_id}")
        
        return embed

    @commands.hybrid_command(name="create")
    async def create_project(self, ctx):
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
        
        # Confirm creation
        await ctx.send(
                f"Please check if the details below is correct\n"
                f"Name: {name}\n"
                f"Description: {description}\n"
                f"Channel: {project_channel.mention}\n\n"
                "To confirm, type `yes`"
            )

        confirm = await self.bot.wait_for("message", check=check)
        if confirm.content != "yes":
            await ctx.send("❌ Creation cancelled. If you think this is a mistake, create again but type `yes` when prompted to confirm.")
            return

        message = await ctx.send("🔄 Creating project...")

        # Create project
        board = await project_channel.send("🔄 Creating project...")

        try:
            response = requests.post(
            os.getenv("API_URL") + 'projects/create-project',
            json={
                'name': name,
                'description': description,
                'server': ctx.message.guild.id,
                'channel': project_channel.id,
                'message': board.id,
                'user': ctx.author.id
                }
            )

            if response.status_code != 201:
                print(response.json())
                await message.edit(content="❌ Cannot create project. Please try again later.")
                await board.delete()
                return
            
            project_id = response.json()['id']

            await board.edit(content="", embed=self.parse_project_embed(name=name, description=description, project_id=project_id))

            await message.edit(content=
                f"✅ Project created!\n"
                f"Name: {name}\n"
                f"Description: {description}\n"
                f"Channel: {project_channel.mention}\n"
                f"Project ID: {project_id}\n\n"
                "Please take note of the project ID for manipulating project's content (e.g. task items, project column, etc.). Project ID can also be found in the project board."
            )
        except:
            await message.edit(content="❌ Cannot create project. Please try again later.")
            await board.delete()
            return

    @commands.hybrid_command(name="list")
    async def list_projects(self, ctx):
        response = requests.get(os.getenv("API_URL") + f'projects/get-project-list/{ctx.message.guild.id}')

        if response.status_code != 200:
            await ctx.send("❌ Cannot obtain list of projects, please try again later.")
            return

        embed = Embed(
            color=Color.ash_embed(),
            title=f"Active Projects for {ctx.message.guild.name}",
        )

        for project in response.json()['projects']:
            embed.add_field(name=project['name'], 
                            value=
                                f"{project['id']}\n"
                                f"Created: {project['created_at']}\n"
                                f"```{project['description']}```\n",
                            inline=False
                            )

        await ctx.send("Only first 25 projects are displayed", embed=embed)
        return
    
    @commands.hybrid_command(name="details")
    async def project_details(self, ctx, id):
        try:
            response = requests.get(os.getenv("API_URL") + f'projects/get-project/{id}')

            if response.status_code == 404:
                await ctx.send("❌ Project not found, please double check if your ID does have any typos.")
                return
                
            if response.status_code == 500:
                await ctx.send("❌ Unknown Error Occured, please try again later.")
                return

            data = response.json()['project']

            embed = Embed(
                color=Color.ash_embed(),
                title=data['name'],
                description=data['description'],
            )
            embed.set_footer(text=data['id'])

            await ctx.send(f"Project Details for {data['name']}", embed=embed)
        except:
            await ctx.send("❌ Unknown Error Occured, please try again later.")
            return

    @project_details.error
    async def project_details_err(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Project ID is required.\n\nFormat: `?list [project-id]`")
            return
        
        print(error)

    @commands.hybrid_command(name="edit")
    async def edit_project(self, ctx, id):
        """
        Edits a project and automatically updates the project board if available.

        Usage: ?edit <project_id>
        """
        
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        response = requests.get(os.getenv("API_URL") + f'projects/get-project/{id}')

        if response.status_code == 404:
            await ctx.send("❌ Project not found, please double check if your ID does have any typos.")
            return
                
        if response.status_code == 500:
            await ctx.send("❌ Unknown Error Occured, please try again later.")
            return

        data = response.json()['project']

        embed = Embed(
            color=Color.ash_embed(),
            title=data['name'],
            description=data['description'],
        )
        embed.set_footer(text=data['id'])

        olddata = await ctx.send(f"Here is the project you want to edit. Type `yes` to continue.", embed=embed)
        confirm = await self.bot.wait_for("message", check=check)
        if confirm.content != "yes":
            await ctx.send("❌ Edit cancelled. If you think this is a mistake, edit again but type `yes` when prompted to confirm.")
            await olddata.delete()
            await confirm.delete()
            return
    
        await confirm.delete()
        
        name = data['name']
        description = data['description']

        while True:
            editmenu = await ctx.send(
                "Which field you want to edit?\n\n"
                "`name` for project name\n"
                "`desc` for project description\n"
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

                    await editmenu.delete()
                    await name_msg.delete()

                    await menu.edit(content="New name changed")

                case "desc":
                    await selection.delete()

                    menu = await ctx.send("New description of the project?")
                    desc_msg = await self.bot.wait_for("message", check=check)
                    description = desc_msg.content

                    await editmenu.delete()
                    await desc_msg.delete()

                    await menu.edit(content="New description changed")
                
                case "done":
                    await editmenu.delete()
                    await selection.delete()

                    embed = Embed(
                        color=Color.ash_embed(),
                        title=name,
                        description=description,
                    )
                    embed.set_footer(text=data['id'])
                    menu = await ctx.send("Please confirm the edited project. To apply changes, type `yes`.", embed=embed)
                    edit_confirm = ""
                    edit_confirm = await self.bot.wait_for("message", check=check)
                    if edit_confirm.content == "yes":
                        await menu.edit(content="🔄 Applying changes...", embeds=[])
                        await olddata.delete()
                        await edit_confirm.delete()

                        # Sends the changes to the API first
                        response = requests.patch(
                        os.getenv("API_URL") + f'projects/edit-project/{id}',
                        json={
                            'name': name,
                            'description': description,
                            'user': ctx.author.id
                            }
                        )
                        if response.status_code == 500:
                            await ctx.send("❌ Unknown Error Occured, please try again later.")
                            return
                        
                        # Attempting to edit the project board
                        try:
                            new_data = response.json()['project']
                            
                            channel_id = int(new_data['channel_id'])
                            message_id = int(new_data['message_id'])
 
                            board_channel = self.bot.get_channel(channel_id)

                            if board_channel is None:
                                board_channel = await self.bot.fetch_channel(channel_id)

                            board = await board_channel.fetch_message(message_id)

                            embeds = [self.parse_project_embed(name=new_data['name'], description=new_data['description'], project_id=new_data['id'])]
                            await board.edit(embeds=embeds)
                        except NotFound:
                            await ctx.send("⚠️ I cannot update the project board because the channel or the message where the project board is seems to be deleted. Please try to send the project board again to get automatic updates.")
                        except Forbidden:
                            await ctx.send("⚠️ I cannot update the project board because I do not have permission to access the channel or message where the project board lives. Double check my permissions and update the project board manually.")
                        except Exception as e:
                            traceback.print_exc()
                            await ctx.send("⚠️ An unknown error preventing me to edit the project board. Please try updating the board manually later.")

                        await menu.edit(content="✅ Changes applied!")

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

    @edit_project.error
    async def project_details_err(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Project ID is required.\n\nFormat: `?edit [project-id]`")
            return
        
        print(error)



async def setup(bot):
    await bot.add_cog(Projects(bot))