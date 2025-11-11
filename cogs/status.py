from discord.ext import commands
from discord import app_commands
import discord
import datetime

ROLE_ID_AUTORISE = 1401313791509266521
STATUS_CHANNEL_ID = 1401313792368840805

# Palette de couleurs moderne
COLORS = {
    "active": 0x57F287,      # Vert vibrant
    "inactive": 0xED4245,    # Rouge vibrant
    "maintenance": 0xFEE75C, # Jaune
    "info": 0x5865F2         # Bleu Discord
}

class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _send_status_update(
        self, 
        interaction: discord.Interaction, 
        title: str, 
        description: str, 
        color: int,
        status_message: str,
        icon: str,
        details: str = None
    ):
        # 1. Confirmation éphémère immédiate
        confirm_embed = discord.Embed(
            description=f"{icon} **{status_message}**\n\nStatus update has been broadcast to the team.",
            color=color
        )
        await interaction.response.send_message(embed=confirm_embed, ephemeral=True) 
        
        # 2. Récupérer le salon cible
        target_channel = self.bot.get_channel(STATUS_CHANNEL_ID)
        if not target_channel:
            return

        # 3. Créer l'embed principal avec design moderne
        embed = discord.Embed(
            title="",
            description=f"## {icon} {title}\n\n{description}",
            color=color,
            timestamp=datetime.datetime.now()
        )
        
        # Informations additionnelles
        if details:
            embed.add_field(
                name="📋 Details",
                value=details,
                inline=False
            )
        
        # Informations sur l'action
        embed.add_field(
            name="👤 Updated by",
            value=f"{interaction.user.mention}\n`{interaction.user.name}`",
            inline=True
        )
        
        embed.add_field(
            name="🕐 Timestamp",
            value=f"<t:{int(datetime.datetime.now().timestamp())}:F>",
            inline=True
        )
        
        embed.set_footer(
            text=f"Status Update System",
            icon_url=interaction.user.display_avatar.url
        )
        
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        # 4. Envoyer avec un séparateur visuel
        await target_channel.send("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        await target_channel.send(embed=embed)

    @app_commands.command(name="statopen", description="🟢 Set the bot status to active and operational")
    async def statopen(self, interaction: discord.Interaction):
        if not any(role.id == ROLE_ID_AUTORISE for role in interaction.user.roles):
            await interaction.response.send_message(
                "🚫 **Access Denied** • You don't have permission to update the bot status.",
                ephemeral=True
            )
            return
        
        await self._send_status_update(
            interaction,
            title="System Operational",
            description="All bot systems are **fully operational** and ready to serve.",
            color=COLORS["active"],
            status_message="System Status: ACTIVE",
            icon="🟢",
            details="```diff\n+ All services running normally\n+ Full functionality available\n+ No issues detected\n```"
        )

    @app_commands.command(name="statuclose", description="🔴 Set the bot status to inactive or maintenance mode")
    async def statuclose(self, interaction: discord.Interaction):
        if not any(role.id == ROLE_ID_AUTORISE for role in interaction.user.roles):
            await interaction.response.send_message(
                "🚫 **Access Denied** • You don't have permission to update the bot status.",
                ephemeral=True
            )
            return
        
        await self._send_status_update(
            interaction,
            title="System Disabled",
            description="Bot systems have been **temporarily disabled**. Only core functions remain active.",
            color=COLORS["inactive"],
            status_message="System Status: INACTIVE",
            icon="🔴",
            details="```diff\n- Most services temporarily unavailable\n- Essential functions only\n- Normal operations suspended\n```"
        )

    @app_commands.command(name="statmaintenance", description="🟡 Set the bot to maintenance mode")
    async def statmaintenance(self, interaction: discord.Interaction):
        if not any(role.id == ROLE_ID_AUTORISE for role in interaction.user.roles):
            await interaction.response.send_message(
                "🚫 **Access Denied** • You don't have permission to update the bot status.",
                ephemeral=True
            )
            return
        
        await self._send_status_update(
            interaction,
            title="Maintenance Mode",
            description="Bot is currently under **scheduled maintenance**. Services will be restored shortly.",
            color=COLORS["maintenance"],
            status_message="System Status: MAINTENANCE",
            icon="🟡",
            details="```yaml\nStatus: Performing system updates\nExpected: Service restoration soon\nImpact: Limited functionality\n```"
        )

    @app_commands.command(name="statinfo", description="ℹ️ Post a custom status information message")
    @app_commands.describe(message="The information message to broadcast")
    async def statinfo(self, interaction: discord.Interaction, message: str):
        if not any(role.id == ROLE_ID_AUTORISE for role in interaction.user.roles):
            await interaction.response.send_message(
                "🚫 **Access Denied** • You don't have permission to post status updates.",
                ephemeral=True
            )
            return
        
        await self._send_status_update(
            interaction,
            title="Status Information",
            description=message,
            color=COLORS["info"],
            status_message="Information posted successfully",
            icon="ℹ️"
        )

async def setup(bot):
    await bot.add_cog(Status(bot))