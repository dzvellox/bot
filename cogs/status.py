# cogs/status.py 
from discord.ext import commands
from discord import app_commands
import discord

ROLE_ID_AUTORISE = 1401313791509266521

class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="statopen", description="Définit le bot comme actif.")
    async def statopen(self, interaction: discord.Interaction):
        if not any(role.id == ROLE_ID_AUTORISE for role in interaction.user.roles):
            await interaction.response.send_message("❌ Tu n'as pas la permission d'utiliser cette commande.", ephemeral=True)
            return

        embed = discord.Embed(
            title="✅ Le bot est actif",
            description="Tous les systèmes du bot fonctionnent.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="statuclose", description="Définit le bot comme inactif.")
    async def statuclose(self, interaction: discord.Interaction):
        if not any(role.id == ROLE_ID_AUTORISE for role in interaction.user.roles):
            await interaction.response.send_message("❌ Tu n'as pas la permission d'utiliser cette commande.", ephemeral=True)
            return

        embed = discord.Embed(
            title="⛔ Le bot est désactivé",
            description="Seuls les systèmes de base et le support sont encore actifs.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Status(bot))
