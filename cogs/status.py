# cogs/status.py 
from discord.ext import commands
from discord import app_commands
import discord

# Authorized Role ID (internal value remains the same)
ROLE_ID_AUTORISE = 1401313791509266521

class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="statopen", description="Sets the bot status to active.")
    async def statopen(self, interaction: discord.Interaction):
        if not any(role.id == ROLE_ID_AUTORISE for role in interaction.user.roles):
            await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
            return

        embed = discord.Embed(
            title="✅ Bot is Active",
            description="All bot systems are operational.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="statuclose", description="Sets the bot status to inactive.")
    async def statuclose(self, interaction: discord.Interaction):
        if not any(role.id == ROLE_ID_AUTORISE for role in interaction.user.roles):
            await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
            return

        embed = discord.Embed(
            title="⛔ Bot is Disabled",
            description="Only core systems and support functions remain active.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Status(bot))