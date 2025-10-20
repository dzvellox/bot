import discord
from discord.ext import commands
from discord import app_commands

SALON_DESTINATION = 1401313792154927182
ROLE_ID_AUTORISE = 1401313791509266521  # Seul ce rôle peut utiliser la commande

class UpdateForm(discord.ui.Modal, title="Update"): # Translated 'MonFormulaire' to 'UpdateForm' and title
    version_input = discord.ui.TextInput(label="Version", max_length=100) # Translated 'sujet' to 'version_input'
    whats_new_input = discord.ui.TextInput(label="What's new", style=discord.TextStyle.paragraph, max_length=500) # Translated 'new' to 'whats_new_input'
    bugs_fixed_input = discord.ui.TextInput(label="Bugs fixed", style=discord.TextStyle.paragraph, max_length=500) # Translated 'bug' to 'bugs_fixed_input'

    def __init__(self, message=None, view=None):
        super().__init__()
        self.message = message
        self.view = view

    async def on_submit(self, interaction: discord.Interaction):
        channel = interaction.guild.get_channel(SALON_DESTINATION)
        if channel is None:
            await interaction.response.send_message("❌ Error: Update channel not found.", ephemeral=True) # Translated 'Room not found.'
            return

        embed = discord.Embed(
            title=f"📦 Update {self.version_input.value}", # Using new variable name
            color=discord.Color.orange()
        )
        embed.add_field(name="🆕 What's new", value=self.whats_new_input.value, inline=False) # Using new variable name
        embed.add_field(name="🛠️ Bugs fixed", value=self.bugs_fixed_input.value, inline=False) # Using new variable name
        embed.set_footer(text=f"Posted by {interaction.user}", icon_url=interaction.user.display_avatar.url)

        # Si le message et la vue existent (mode bouton), on enlève la vue du message
        if self.message:
            try:
                await self.message.edit(view=None)
            except Exception:
                pass

        await channel.send(embed=embed)
        await interaction.response.send_message("✅ Update sent successfully!", ephemeral=True) # Translated


class Update(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="update", description="Create a new bot update announcement.") # Translated description
    async def update_slash(self, interaction: discord.Interaction):
        if not any(role.id == ROLE_ID_AUTORISE for role in interaction.user.roles):
            await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True) # Translated permission error
            return

        # Ouvre directement le modal
        modal = UpdateForm() # Using new class name
        await interaction.response.send_modal(modal)


async def setup(bot):
    await bot.add_cog(Update(bot))