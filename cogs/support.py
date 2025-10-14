import discord
from discord.ext import commands
from discord import app_commands
import datetime

ID_CATEGORIE = 1401319148361089196
ROLE_IDS_AUTORISES = [1401313791509266521, 222222222222222222]

class MonFormulaire(discord.ui.Modal, title="Support"):
    sujet = discord.ui.TextInput(label="Your Email", max_length=100)
    description = discord.ui.TextInput(label="What is your problem", style=discord.TextStyle.paragraph, max_length=500)

    async def on_submit(self, interaction: discord.Interaction):
        category = interaction.guild.get_channel(ID_CATEGORIE)
        if category is None:
            await interaction.response.send_message("Error: Category not found.", ephemeral=True)
            return

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True)
        }
        channel_name = f"ticket-{interaction.user.name}".lower()

        existing_channel = discord.utils.get(interaction.guild.channels, name=channel_name)
        if existing_channel:
            await interaction.response.send_message(f"You already have an open ticket here : {existing_channel.mention}", ephemeral=True)
            return

        channel = await category.create_text_channel(channel_name, overwrites=overwrites, topic=f"Ticket created by {interaction.user}")

        embed = discord.Embed(
            title="Open ticket",
            description=f"{interaction.user.mention} Thank you for opening a ticket. A staff member will come and help you.",
            color=discord.Color.green()
        )
        embed.add_field(name="Email : ", value=self.sujet.value, inline=False)
        embed.add_field(name="The problem", value=self.description.value, inline=False)

        class FermerTicketView(discord.ui.View):
            @discord.ui.button(label="Close ticket", style=discord.ButtonStyle.danger)
            async def fermer(self, interaction_button: discord.Interaction, button: discord.ui.Button):
                author_roles = [role.id for role in interaction_button.user.roles]
                if not any(role_id in ROLE_IDS_AUTORISES for role_id in author_roles):
                    await interaction_button.response.send_message("❌ You do not have permission to close this ticket.", ephemeral=True)
                    return
                await interaction_button.response.send_message("The ticket will be closed in 3 seconds...", ephemeral=True)
                await discord.utils.sleep_until(discord.utils.utcnow() + datetime.timedelta(seconds=3))
                await interaction_button.channel.delete()

        view = FermerTicketView()
        await channel.send(embed=embed, view=view)
        await interaction.response.send_message(f"Your ticket has been created : {channel.mention}", ephemeral=True)

class MonView(discord.ui.View):
    @discord.ui.button(label="Open form", style=discord.ButtonStyle.primary)
    async def bouton_formulaire(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = MonFormulaire()
        await interaction.response.send_modal(modal)

class Support(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="support", description="Open a support ticket form.")
    async def support(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📩 Need help?",
            description="If you have any questions or issues, feel free to open a ticket.",
            color=discord.Color.blue()
        )
        view = MonView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=False)

async def setup(bot):
    await bot.add_cog(Support(bot))