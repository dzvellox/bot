import discord
from discord.ext import commands
from discord import app_commands, Embed

ROLE_ID_AUTORISE = 1401313791509266521
MEGA_LINK = "https://mega.nz/file/hYhUwa4a#dXaaLcitSzUbR80rBRV2-ees06DUxUbnZBmuN0gZpZA"

class MegaDownload(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="apk", description="Send the MEGA link of the APK.")
    async def apk_mega(self, interaction: discord.Interaction):
        # Vérifier si l'utilisateur a le rôle autorisé
        if not any(role.id == ROLE_ID_AUTORISE for role in interaction.user.roles):
            await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
            return

        embed = Embed(
            title="📦 APK Download",
            description=f"[Click here to download the app on Android]({MEGA_LINK})",
            color=discord.Color.orange()
        )
        embed.set_footer(text=f"Send by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=False)

async def setup(bot):
    await bot.add_cog(MegaDownload(bot))
