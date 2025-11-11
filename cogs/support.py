import discord
from discord.ext import commands
from discord import app_commands
import datetime

ID_CATEGORIE = 1401319148361089196
ROLE_IDS_AUTORISES = [1401313791509266521, 222222222222222222]

# Palette de couleurs moderne
COLORS = {
    "primary": 0x5865F2,     # Bleu Discord
    "success": 0x57F287,     # Vert vibrant
    "warning": 0xFEE75C,     # Jaune
    "danger": 0xED4245,      # Rouge vibrant
    "info": 0x00D9FF         # Cyan
}

class MonFormulaire(discord.ui.Modal, title="🎫 Create Support Ticket"):
    sujet = discord.ui.TextInput(
        label="📧 Your Email",
        placeholder="example@email.com",
        max_length=100,
        required=True
    )
    description = discord.ui.TextInput(
        label="❓ Describe Your Issue",
        placeholder="Please provide as much detail as possible...",
        style=discord.TextStyle.paragraph,
        max_length=1000,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        category = interaction.guild.get_channel(ID_CATEGORIE)
        if category is None:
            error_embed = discord.Embed(
                description="❌ **Error** • Support category not found. Please contact an administrator.",
                color=COLORS["danger"]
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
            return

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        # Ajouter les rôles autorisés aux overwrites
        for role_id in ROLE_IDS_AUTORISES:
            role = interaction.guild.get_role(role_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        channel_name = f"ticket-{interaction.user.name}".lower().replace(" ", "-")

        existing_channel = discord.utils.get(interaction.guild.channels, name=channel_name)
        if existing_channel:
            already_open_embed = discord.Embed(
                description=f"⚠️ **Ticket Already Open**\n\nYou already have an active ticket: {existing_channel.mention}",
                color=COLORS["warning"]
            )
            await interaction.response.send_message(embed=already_open_embed, ephemeral=True)
            return

        # Message de confirmation immédiat
        creating_embed = discord.Embed(
            description="⏳ **Creating your ticket...**\n\nPlease wait a moment.",
            color=COLORS["info"]
        )
        await interaction.response.send_message(embed=creating_embed, ephemeral=True)

        # Création du channel
        channel = await category.create_text_channel(
            channel_name, 
            overwrites=overwrites, 
            topic=f"Support ticket • Created by {interaction.user.name} • {datetime.datetime.now():%m/%d/%Y}"
        )

        # Embed principal du ticket avec design moderne
        ticket_embed = discord.Embed(
            title="",
            description=f"## 🎫 Support Ticket Opened\n\nHello {interaction.user.mention}! Thank you for reaching out.\n\nA staff member will assist you shortly. Please be patient and provide any additional information that might help us resolve your issue.",
            color=COLORS["success"],
            timestamp=datetime.datetime.now()
        )
        
        ticket_embed.add_field(
            name="👤 Ticket Creator",
            value=f"{interaction.user.mention}\n`{interaction.user.name}`",
            inline=True
        )
        
        ticket_embed.add_field(
            name="🆔 User ID",
            value=f"`{interaction.user.id}`",
            inline=True
        )
        
        ticket_embed.add_field(
            name="📧 Contact Email",
            value=f"```\n{self.sujet.value}```",
            inline=False
        )
        
        ticket_embed.add_field(
            name="📋 Issue Description",
            value=f"```\n{self.description.value}```",
            inline=False
        )
        
        ticket_embed.set_thumbnail(url=interaction.user.display_avatar.url)
        ticket_embed.set_footer(
            text=f"Ticket created at",
            icon_url=interaction.guild.icon.url if interaction.guild.icon else None
        )

        class TicketControlView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)

            @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, emoji="🔒")
            async def close_ticket(self, interaction_button: discord.Interaction, button: discord.ui.Button):
                author_roles = [role.id for role in interaction_button.user.roles]
                if not any(role_id in ROLE_IDS_AUTORISES for role_id in author_roles):
                    deny_embed = discord.Embed(
                        description="🚫 **Access Denied**\n\nYou don't have permission to close this ticket.",
                        color=COLORS["danger"]
                    )
                    await interaction_button.response.send_message(embed=deny_embed, ephemeral=True)
                    return
                
                # Embed de fermeture
                closing_embed = discord.Embed(
                    description=f"## 🔒 Ticket Closing\n\nThis ticket is being closed by {interaction_button.user.mention}.\n\n**Channel will be deleted in 5 seconds...**",
                    color=COLORS["danger"],
                    timestamp=datetime.datetime.now()
                )
                closing_embed.set_footer(text="Thank you for using our support system")
                
                await interaction_button.response.send_message(embed=closing_embed)
                await discord.utils.sleep_until(discord.utils.utcnow() + datetime.timedelta(seconds=5))
                
                try:
                    await interaction_button.channel.delete()
                except:
                    pass

            @discord.ui.button(label="Claim Ticket", style=discord.ButtonStyle.success, emoji="✋")
            async def claim_ticket(self, interaction_button: discord.Interaction, button: discord.ui.Button):
                author_roles = [role.id for role in interaction_button.user.roles]
                if not any(role_id in ROLE_IDS_AUTORISES for role_id in author_roles):
                    deny_embed = discord.Embed(
                        description="🚫 **Access Denied**\n\nYou don't have permission to claim this ticket.",
                        color=COLORS["danger"]
                    )
                    await interaction_button.response.send_message(embed=deny_embed, ephemeral=True)
                    return
                
                claim_embed = discord.Embed(
                    description=f"✋ **Ticket Claimed**\n\n{interaction_button.user.mention} is now handling this ticket.",
                    color=COLORS["success"]
                )
                await interaction_button.response.send_message(embed=claim_embed)
                
                # Désactiver le bouton après claim
                button.disabled = True
                button.label = f"Claimed by {interaction_button.user.name}"
                button.style = discord.ButtonStyle.secondary
                await interaction_button.message.edit(view=self)

        view = TicketControlView()
        
        # Message de séparation
        await channel.send("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        await channel.send(embed=ticket_embed, view=view)
        await channel.send("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        # Ping du staff
        staff_mentions = " ".join([f"<@&{role_id}>" for role_id in ROLE_IDS_AUTORISES])
        await channel.send(f"📢 {staff_mentions} New ticket requires attention!")

        # Éditer la confirmation
        success_embed = discord.Embed(
            description=f"✅ **Ticket Created Successfully!**\n\nYour ticket has been opened: {channel.mention}\n\nPlease head there to continue.",
            color=COLORS["success"]
        )
        await interaction.edit_original_response(embed=success_embed)

class SupportPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Open Ticket", style=discord.ButtonStyle.primary, emoji="🎫")
    async def open_ticket_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = MonFormulaire()
        await interaction.response.send_modal(modal)

class Support(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="support", description="🎫 Display the support ticket panel")
    async def support(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="",
            description=(
                "## 🎫 Support Center\n\n"
                "Need assistance? Our support team is here to help!\n\n"
                "**How to get support:**\n"
                "• Click the button below to open a ticket\n"
                "• Fill out the form with your email and issue details\n"
                "• Wait for a staff member to assist you\n\n"
                "**Response time:** Usually within a few hours\n"
                "**Available:** 24/7"
            ),
            color=COLORS["primary"]
        )
        
        embed.add_field(
            name="📋 What to Include",
            value=(
                "```\n"
                "• Your contact email\n"
                "• Clear description of your issue\n"
                "• Any relevant screenshots or details\n"
                "• Steps to reproduce (if applicable)\n"
                "```"
            ),
            inline=False
        )
        
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text="Support Ticket System", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        
        view = SupportPanelView()
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Support(bot))