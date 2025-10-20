import discord
from discord.ext import commands
from discord import app_commands
import datetime

# Constantes des ID
ROLE_IDS_AUTORISES = [1401313791509266521, 1401313791509266520, 1401313791509266519]
CHANNEL_VALIDATED_ID = 1402014226519953550  # Salon pour suggestions approuvées
CHANNEL_SUGGESTIONS_ID = 1401313792154927184 # Salon où les suggestions sont postées

class VoteView(discord.ui.View):
    ROLES_AUTORISES = ROLE_IDS_AUTORISES
    CHANNEL_VALIDATED_ID = CHANNEL_VALIDATED_ID

    def __init__(self, author: discord.User):
        super().__init__(timeout=None)
        self.votes = {"up": set(), "down": set()}
        self.author = author
        self.message = None

    async def update_message(self):
        total = len(self.votes["up"]) + len(self.votes["down"])
        up_pct = (len(self.votes["up"]) / total * 100) if total else 0
        down_pct = (len(self.votes["down"]) / total * 100) if total else 0

        bar_length = 20
        up_len = int((len(self.votes["up"]) / total) * bar_length) if total else 0
        down_len = bar_length - up_len
        progress_bar = f"{'🟩' * up_len}{'🟥' * down_len}"

        embed = self.message.embeds[0]
        embed.set_field_at(
            2,
            name="📊 Votes",
            value=f"👍 {len(self.votes['up'])} ({up_pct:.1f}%) • 👎 {len(self.votes['down'])} ({down_pct:.1f}%)\n`{progress_bar}`",
            inline=False,
        )
        await self.message.edit(embed=embed, view=self)

    def has_permission(self, user: discord.Member):
        return any(role.id in self.ROLES_AUTORISES for role in user.roles)

    @discord.ui.button(label="👍 Voter Pour", style=discord.ButtonStyle.blurple) # Traduit
    async def pour(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.votes["down"].discard(interaction.user.id)
        self.votes["up"].add(interaction.user.id)
        await interaction.response.defer()
        await self.update_message()

    @discord.ui.button(label="👎 Voter Contre", style=discord.ButtonStyle.blurple) # Traduit
    async def contre(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.votes["up"].discard(interaction.user.id)
        self.votes["down"].add(interaction.user.id)
        await interaction.response.defer()
        await self.update_message()

    @discord.ui.button(label="✅ Approuver", style=discord.ButtonStyle.success) # Traduit
    async def approuver(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.has_permission(interaction.user):
            await interaction.response.send_message("❌ Vous n'avez pas la permission d'approuver.", ephemeral=True) # Traduit
            return

        embed = self.message.embeds[0]
        embed.set_field_at(1, name="🕐 Statut", value="✅ Approuvée", inline=False) # Traduit
        await interaction.response.edit_message(embed=embed, view=None)

        # Créer et envoyer dans le salon des approuvées
        total = len(self.votes["up"]) + len(self.votes["down"])
        up_pct = (len(self.votes["up"]) / total * 100) if total else 0
        down_pct = (len(self.votes["down"]) / total * 100) if total else 0

        validated_embed = discord.Embed(
            title="✅ Suggestion Approuvée", # Traduit
            description=embed.description,
            color=discord.Color.green()
        )
        validated_embed.set_author(name=f"Proposée par : {self.author}") # Traduit
        validated_embed.add_field(name="📊 Résultat", value=f"👍 {up_pct:.1f}% • 👎 {down_pct:.1f}%", inline=False) # Traduit
        validated_embed.add_field(name="👤 Approuvée par", value=interaction.user.mention, inline=False) # Traduit
        validated_embed.set_footer(text=f"{datetime.datetime.now():%d/%m/%Y à %H:%M}") # Format de date FR

        if embed.image:
            validated_embed.set_image(url=embed.image.url)

        channel = interaction.client.get_channel(self.CHANNEL_VALIDATED_ID)
        if channel:
            await channel.send(embed=validated_embed)

    @discord.ui.button(label="❌ Rejeter", style=discord.ButtonStyle.danger) # Traduit
    async def rejeter(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.has_permission(interaction.user):
            await interaction.response.send_message("❌ Vous n'avez pas la permission de rejeter.", ephemeral=True) # Traduit
            return
        embed = self.message.embeds[0]
        embed.set_field_at(1, name="🕐 Statut", value="❌ Rejetée", inline=False) # Traduit
        await interaction.response.edit_message(embed=embed, view=None)

class Suggestions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="suggerer", description="Soumettre une nouvelle suggestion.") # Traduit
    async def suggest(self, interaction: discord.Interaction, texte: str, image: str = None):
        embed = discord.Embed(title="💡 Suggestion", description=texte, color=discord.Color.orange())
        embed.add_field(name="🕐 Statut", value="⏳ En attente", inline=False) # Traduit
        embed.add_field(name="📊 Votes", value="👍 0 (0.0%) • 👎 0 (0.0%)\n`🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥`", inline=False)
        embed.set_footer(text=f"Par {interaction.user} • {datetime.datetime.now():%d/%m/%Y à %H:%M}") # Format de date FR
        if image:
            embed.set_image(url=image)

        view = VoteView(author=interaction.user)

        # Envoi dans le salon des suggestions
        channel = interaction.client.get_channel(CHANNEL_SUGGESTIONS_ID) # Utilisation de la constante
        if channel is None:
            await interaction.response.send_message("❌ Impossible de trouver le salon de suggestions.", ephemeral=True) # Traduit
            return

        msg = await channel.send(embed=embed, view=view)
        view.message = msg

        await interaction.response.send_message("✅ Votre suggestion a été envoyée avec succès dans le salon dédié !", ephemeral=True) # Traduit

async def setup(bot):
    await bot.add_cog(Suggestions(bot))