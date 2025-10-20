# cogs/status.py 
from discord.ext import commands
from discord import app_commands
import discord

ROLE_ID_AUTORISE = 1401313791509266521
STATUS_CHANNEL_ID = 1401313792368840805 

class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _send_status_update(self, interaction: discord.Interaction, title: str, description: str, color: discord.Color, status_message: str):
        
        # 1. Accuser réception immédiatement (dans les 3 secondes)
        await interaction.response.send_message(status_message, ephemeral=True) 

        # 2. Récupérer le salon cible
        target_channel = self.bot.get_channel(STATUS_CHANNEL_ID)
        if not target_channel:
            # Si le canal n'est pas trouvé, le message éphémère a déjà été envoyé, c'est suffisant.
            return

        embed = discord.Embed(
            title=title,
            description=f"{description} (Action by {interaction.user.mention})",
            color=color
        )
        
        # 3. Envoyer l'embed dans le salon cible
        await target_channel.send(embed=embed)


    @app_commands.command(name="statopen", description="Sets the bot status to active.")
    async def statopen(self, interaction: discord.Interaction):
        if not any(role.id == ROLE_ID_AUTORISE for role in interaction.user.roles):
            await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
            return

        await self._send_status_update(
            interaction,
            title="✅ Bot is Active",
            description="All bot systems are operational.",
            color=discord.Color.green(),
            status_message="✅ Status set to Active. Notification sent to the status channel."
        )


    @app_commands.command(name="statuclose", description="Sets the bot status to inactive.")
    async def statuclose(self, interaction: discord.Interaction):
        if not any(role.id == ROLE_ID_AUTORISE for role in interaction.user.roles):
            await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
            return

        await self._send_status_update(
            interaction,
            title="⛔ Bot is Disabled",
            description="Only core systems and support functions remain active.",
            color=discord.Color.red(),
            status_message="⛔ Status set to Disabled. Notification sent to the status channel."
        )


async def setup(bot):
    await bot.add_cog(Status(bot))