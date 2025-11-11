import discord
from discord.ext import commands
from discord import app_commands
import datetime

SALON_DESTINATION = 1401313792154927182
ROLE_ID_AUTORISE = 1401313791509266521

# Palette de couleurs moderne
COLORS = {
    "update": 0x5865F2,      # Bleu Discord
    "new": 0x57F287,         # Vert vibrant
    "fix": 0xFEE75C,         # Jaune
    "breaking": 0xED4245,    # Rouge vibrant
    "success": 0x57F287,     # Vert
    "info": 0x00D9FF         # Cyan
}

class UpdateForm(discord.ui.Modal, title="📦 Create Update Announcement"):
    version_input = discord.ui.TextInput(
        label="📌 Version Number",
        placeholder="e.g., v2.5.0, 1.0.3, 2024.11.1",
        max_length=50,
        required=True
    )
    
    whats_new_input = discord.ui.TextInput(
        label="✨ What's New",
        placeholder="• New feature 1\n• New feature 2\n• Improvement...",
        style=discord.TextStyle.paragraph,
        max_length=1000,
        required=True
    )
    
    bugs_fixed_input = discord.ui.TextInput(
        label="🐛 Bugs Fixed",
        placeholder="• Fixed bug 1\n• Fixed bug 2\n• Performance improvements...",
        style=discord.TextStyle.paragraph,
        max_length=1000,
        required=False
    )
    
    breaking_changes_input = discord.ui.TextInput(
        label="⚠️ Breaking Changes (Optional)",
        placeholder="• Breaking change 1\n• Breaking change 2...",
        style=discord.TextStyle.paragraph,
        max_length=500,
        required=False
    )
    
    notes_input = discord.ui.TextInput(
        label="📝 Additional Notes (Optional)",
        placeholder="Any additional information, credits, or notes...",
        style=discord.TextStyle.paragraph,
        max_length=500,
        required=False
    )

    def __init__(self, message=None, view=None):
        super().__init__()
        self.message = message
        self.view = view

    async def on_submit(self, interaction: discord.Interaction):
        channel = interaction.guild.get_channel(SALON_DESTINATION)
        if channel is None:
            error_embed = discord.Embed(
                description="❌ **Error** • Update channel not found. Please contact an administrator.",
                color=COLORS["breaking"]
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
            return

        # Confirmation immédiate
        processing_embed = discord.Embed(
            description="⏳ **Processing...**\n\nYour update announcement is being published.",
            color=COLORS["info"]
        )
        await interaction.response.send_message(embed=processing_embed, ephemeral=True)

        # Créer l'embed principal avec design moderne
        main_embed = discord.Embed(
            title="",
            description=f"## 📦 Update {self.version_input.value}\n\nA new update has been released! Check out what's new below.",
            color=COLORS["update"],
            timestamp=datetime.datetime.now()
        )
        
        # Champ What's New
        whats_new_formatted = self._format_list(self.whats_new_input.value)
        main_embed.add_field(
            name="✨ What's New",
            value=whats_new_formatted,
            inline=False
        )
        
        # Champ Bugs Fixed (si rempli)
        if self.bugs_fixed_input.value.strip():
            bugs_fixed_formatted = self._format_list(self.bugs_fixed_input.value)
            main_embed.add_field(
                name="🐛 Bugs Fixed",
                value=bugs_fixed_formatted,
                inline=False
            )
        
        # Champ Breaking Changes (si rempli)
        if self.breaking_changes_input.value.strip():
            breaking_formatted = self._format_list(self.breaking_changes_input.value)
            main_embed.add_field(
                name="⚠️ Breaking Changes",
                value=f"```diff\n- {breaking_formatted}\n```",
                inline=False
            )
        
        # Notes additionnelles (si rempli)
        if self.notes_input.value.strip():
            main_embed.add_field(
                name="📝 Additional Notes",
                value=self.notes_input.value,
                inline=False
            )
        
        # Informations sur le release
        main_embed.add_field(
            name="👤 Released by",
            value=f"{interaction.user.mention}\n`{interaction.user.name}`",
            inline=True
        )
        
        main_embed.add_field(
            name="📅 Release Date",
            value=f"<t:{int(datetime.datetime.now().timestamp())}:D>",
            inline=True
        )
        
        main_embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
        main_embed.set_footer(
            text=f"Update System • {self.version_input.value}",
            icon_url=interaction.user.display_avatar.url
        )

        # Bouton de réaction
        class UpdateReactionView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)
            
            @discord.ui.button(label="Acknowledged", style=discord.ButtonStyle.success, emoji="✅", custom_id="ack_update")
            async def acknowledge(self, interaction_button: discord.Interaction, button: discord.ui.Button):
                ack_embed = discord.Embed(
                    description=f"✅ {interaction_button.user.mention} acknowledged this update!",
                    color=COLORS["success"]
                )
                await interaction_button.response.send_message(embed=ack_embed, ephemeral=True)

        view = UpdateReactionView()

        # Enlever la vue du message original si applicable
        if self.message:
            try:
                await self.message.edit(view=None)
            except Exception:
                pass

        # Envoyer l'annonce avec style
        await channel.send("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        await channel.send("@everyone 🔔 **New Update Available!**")  # Ping everyone
        update_message = await channel.send(embed=main_embed, view=view)
        await channel.send("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        # Réaction automatique
        try:
            await update_message.add_reaction("🎉")
            await update_message.add_reaction("❤️")
        except:
            pass

        # Confirmation finale
        success_embed = discord.Embed(
            description=f"✅ **Update Published Successfully!**\n\nYour update announcement for **{self.version_input.value}** has been posted in {channel.mention}",
            color=COLORS["success"]
        )
        await interaction.edit_original_response(embed=success_embed)

    def _format_list(self, text: str) -> str:
        """Formate le texte en liste avec des emojis si ce n'est pas déjà fait"""
        lines = text.strip().split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Si la ligne ne commence pas par un bullet point ou emoji, en ajouter un
            if not line.startswith(('•', '-', '*', '→', '▸', '🔹', '✓')):
                line = f"• {line}"
            formatted_lines.append(line)
        
        return '\n'.join(formatted_lines) if formatted_lines else text


class Update(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="update", description="📦 Create and publish a new update announcement")
    async def update_slash(self, interaction: discord.Interaction):
        if not any(role.id == ROLE_ID_AUTORISE for role in interaction.user.roles):
            deny_embed = discord.Embed(
                description="🚫 **Access Denied**\n\nYou don't have permission to create update announcements.",
                color=COLORS["breaking"]
            )
            await interaction.response.send_message(embed=deny_embed, ephemeral=True)
            return

        # Ouvre directement le modal
        modal = UpdateForm()
        await interaction.response.send_modal(modal)

    @app_commands.command(name="updatetemplate", description="📋 Show an update announcement template")
    async def update_template(self, interaction: discord.Interaction):
        template_embed = discord.Embed(
            title="📋 Update Announcement Template",
            description=(
                "Use this template as a guide when creating update announcements:\n\n"
                "**What's New:**\n"
                "```\n"
                "• Added new dashboard feature\n"
                "• Improved performance by 40%\n"
                "• New dark mode theme\n"
                "• Enhanced mobile experience\n"
                "```\n"
                "**Bugs Fixed:**\n"
                "```\n"
                "• Fixed login issues on mobile\n"
                "• Resolved memory leak in chat\n"
                "• Fixed broken image uploads\n"
                "```\n"
                "**Breaking Changes:**\n"
                "```\n"
                "• Old API endpoints deprecated\n"
                "• Database migration required\n"
                "```"
            ),
            color=COLORS["info"]
        )
        template_embed.set_footer(text="Tip: Use bullet points for better readability")
        await interaction.response.send_message(embed=template_embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Update(bot))