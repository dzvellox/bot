import discord
from discord.ext import commands
from discord import app_commands

SALON_DESTINATION = 1401313792154927182
ROLE_ID_AUTORISE = 1401313791509266521  # Seul ce rôle peut utiliser la commande

class MonFormulaire(discord.ui.Modal, title="Mise à jour"):
    sujet = discord.ui.TextInput(label="Version", max_length=100)
    new = discord.ui.TextInput(label="What's new", style=discord.TextStyle.paragraph, max_length=500)
    bug = discord.ui.TextInput(label="Bugs fixed", style=discord.TextStyle.paragraph, max_length=500)

    def __init__(self, message=None, view=None):
        super().__init__()
        self.message = message
        self.view = view

    async def on_submit(self, interaction: discord.Interaction):
        channel = interaction.guild.get_channel(SALON_DESTINATION)
        if channel is None:
            await interaction.response.send_message("❌ Room not found.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"📦 Update {self.sujet.value}",
            color=discord.Color.orange()
        )
        embed.add_field(name="🆕 What's new", value=self.new.value, inline=False)
        embed.add_field(name="🛠️ Bugs fixed", value=self.bug.value, inline=False)
        embed.set_footer(text=f"Posted by {interaction.user}", icon_url=interaction.user.display_avatar.url)

        # Si le message et la vue existent (mode bouton), on enlève la vue du message
        if self.message:
            try:
                await self.message.edit(view=None)
            except Exception:
                pass

        await channel.send(embed=embed)
        await interaction.response.send_message("✅ Update sent successfully!", ephemeral=True)


class Update(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="update", description="Créer une nouvelle mise à jour.")
    async def update_slash(self, interaction: discord.Interaction):
        if not any(role.id == ROLE_ID_AUTORISE for role in interaction.user.roles):
            await interaction.response.send_message("❌ Tu n'as pas la permission d'utiliser cette commande.", ephemeral=True)
            return

        # Ouvre directement le modal
        modal = MonFormulaire()
        await interaction.response.send_modal(modal)


async def setup(bot):
    await bot.add_cog(Update(bot))
