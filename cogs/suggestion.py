import discord
from discord.ext import commands
from discord import app_commands
import datetime

# Constantes des ID
ROLE_IDS_AUTORISES = [1401313791509266521, 1401313791509266520, 1401313791509266519]
CHANNEL_VALIDATED_ID = 1402014226519953550
CHANNEL_SUGGESTIONS_ID = 1401313792154927184

# Palette de couleurs moderne
COLORS = {
    "pending": 0x5865F2,      # Bleu Discord
    "approved": 0x57F287,     # Vert vibrant
    "rejected": 0xED4245,     # Rouge vibrant
    "neutral": 0x99AAB5       # Gris neutre
}

class VoteView(discord.ui.View):
    ROLES_AUTORISES = ROLE_IDS_AUTORISES
    CHANNEL_VALIDATED_ID = CHANNEL_VALIDATED_ID

    def __init__(self, author: discord.User):
        super().__init__(timeout=None)
        self.votes = {"up": set(), "down": set()}
        self.author = author
        self.message = None

    def create_progress_bar(self, up_votes: int, down_votes: int, length: int = 20) -> str:
        """Crée une barre de progression visuelle avec emojis colorés"""
        total = up_votes + down_votes
        if total == 0:
            return "⬜" * length
        
        up_ratio = up_votes / total
        filled = int(up_ratio * length)
        
        # Barre avec vrais emojis colorés pour un meilleur rendu
        bar = ""
        for i in range(length):
            if i < filled:
                bar += "🟩"  # Carré vert
            else:
                bar += "🟥"  # Carré rouge
        
        return bar

    async def update_message(self):
        up_count = len(self.votes["up"])
        down_count = len(self.votes["down"])
        total = up_count + down_count
        
        up_pct = (up_count / total * 100) if total else 0
        down_pct = (down_count / total * 100) if total else 0

        progress_bar = self.create_progress_bar(up_count, down_count)

        embed = self.message.embeds[0]
        
        # Mise à jour du champ votes avec design amélioré
        vote_display = (
            f"```\n"
            f"┌─────────────────────────┐\n"
            f"│  POUR     │  {up_count:^3}  │ {up_pct:>5.1f}% │\n"
            f"│  CONTRE   │  {down_count:^3}  │ {down_pct:>5.1f}% │\n"
            f"└─────────────────────────┘\n"
            f"```\n"
            f"{progress_bar}\n\n"
            f"**{total}** vote{'s' if total != 1 else ''} au total"
        )
        
        embed.set_field_at(
            1,
            name="📊 Résultats des Votes",
            value=vote_display,
            inline=False,
        )
        await self.message.edit(embed=embed, view=self)

    def has_permission(self, user: discord.Member):
        return any(role.id in self.ROLES_AUTORISES for role in user.roles)

    @discord.ui.button(label="Pour", style=discord.ButtonStyle.success, emoji="👍")
    async def pour(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.votes["down"].discard(interaction.user.id)
        self.votes["up"].add(interaction.user.id)
        await interaction.response.send_message(
            "✅ Votre vote **POUR** a été enregistré !",
            ephemeral=True
        )
        await self.update_message()

    @discord.ui.button(label="Contre", style=discord.ButtonStyle.danger, emoji="👎")
    async def contre(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.votes["up"].discard(interaction.user.id)
        self.votes["down"].add(interaction.user.id)
        await interaction.response.send_message(
            "✅ Votre vote **CONTRE** a été enregistré !",
            ephemeral=True
        )
        await self.update_message()

    @discord.ui.button(label="Approuver", style=discord.ButtonStyle.success, emoji="✅", row=1)
    async def approuver(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.has_permission(interaction.user):
            await interaction.response.send_message(
                "🚫 **Accès refusé** • Vous n'avez pas les permissions nécessaires.",
                ephemeral=True
            )
            return

        embed = self.message.embeds[0]
        
        # Changement visuel du statut
        embed.color = COLORS["approved"]
        embed.set_field_at(
            0,
            name="📌 Statut",
            value="```diff\n+ APPROUVÉE\n```",
            inline=True
        )
        
        # Ajout de l'approbateur
        embed.add_field(
            name="👤 Approuvée par",
            value=f"{interaction.user.mention}",
            inline=True
        )
        
        await interaction.response.edit_message(embed=embed, view=None)

        # Embed pour le salon des validations
        up_count = len(self.votes["up"])
        down_count = len(self.votes["down"])
        total = up_count + down_count
        up_pct = (up_count / total * 100) if total else 0
        down_pct = (down_count / total * 100) if total else 0

        validated_embed = discord.Embed(
            title="",
            description=f"## ✨ Suggestion Approuvée\n\n{embed.description}",
            color=COLORS["approved"]
        )
        
        validated_embed.add_field(
            name="👤 Proposée par",
            value=f"{self.author.mention}\n`{self.author.name}`",
            inline=True
        )
        
        validated_embed.add_field(
            name="✅ Validée par",
            value=f"{interaction.user.mention}\n`{interaction.user.name}`",
            inline=True
        )
        
        validated_embed.add_field(
            name="📊 Score Final",
            value=f"```\n👍 {up_pct:.1f}%  •  👎 {down_pct:.1f}%\n({total} votes)```",
            inline=False
        )
        
        validated_embed.set_footer(
            text=f"Approuvée le {datetime.datetime.now():%d/%m/%Y à %H:%M}",
            icon_url=interaction.user.display_avatar.url
        )
        
        validated_embed.set_thumbnail(url=self.author.display_avatar.url)

        if embed.image:
            validated_embed.set_image(url=embed.image.url)

        channel = interaction.client.get_channel(self.CHANNEL_VALIDATED_ID)
        if channel:
            await channel.send(embed=validated_embed)

    @discord.ui.button(label="Rejeter", style=discord.ButtonStyle.danger, emoji="❌", row=1)
    async def rejeter(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.has_permission(interaction.user):
            await interaction.response.send_message(
                "🚫 **Accès refusé** • Vous n'avez pas les permissions nécessaires.",
                ephemeral=True
            )
            return
        
        embed = self.message.embeds[0]
        embed.color = COLORS["rejected"]
        embed.set_field_at(
            0,
            name="📌 Statut",
            value="```diff\n- REJETÉE\n```",
            inline=True
        )
        
        embed.add_field(
            name="👤 Rejetée par",
            value=f"{interaction.user.mention}",
            inline=True
        )
        
        await interaction.response.edit_message(embed=embed, view=None)

class Suggestions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="suggest", description="✨ Soumettre une nouvelle suggestion")
    @app_commands.describe(
        texte="Décrivez votre suggestion en détail",
        image="URL d'une image à joindre (optionnel)"
    )
    async def suggest(self, interaction: discord.Interaction, texte: str, image: str = None):
        # Embed principal avec design moderne
        embed = discord.Embed(
            title="",
            description=f"## 💡 Nouvelle Suggestion\n\n{texte}",
            color=COLORS["pending"]
        )
        
        # Statut avec style
        embed.add_field(
            name="📌 Statut",
            value="```yaml\nEn attente de votes```",
            inline=True
        )
        
        # Votes initiaux
        embed.add_field(
            name="📊 Résultats des Votes",
            value=(
                f"```\n"
                f"┌─────────────────────────┐\n"
                f"│  POUR     │   0  │  0.0% │\n"
                f"│  CONTRE   │   0  │  0.0% │\n"
                f"└─────────────────────────┘\n"
                f"```\n"
                f"⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜\n\n"
                f"**0** vote au total"
            ),
            inline=False
        )
        
        # Footer avec avatar
        embed.set_footer(
            text=f"Proposée par {interaction.user.name} • {datetime.datetime.now():%d/%m/%Y à %H:%M}",
            icon_url=interaction.user.display_avatar.url
        )
        
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        
        if image:
            embed.set_image(url=image)

        view = VoteView(author=interaction.user)

        channel = interaction.client.get_channel(CHANNEL_SUGGESTIONS_ID)
        if channel is None:
            await interaction.response.send_message(
                "❌ **Erreur** • Le salon de suggestions est introuvable.",
                ephemeral=True
            )
            return

        msg = await channel.send(embed=embed, view=view)
        view.message = msg

        # Confirmation stylée
        confirm_embed = discord.Embed(
            description="✅ **Suggestion envoyée avec succès !**\n\nVotre suggestion a été publiée dans le salon dédié.",
            color=COLORS["approved"]
        )
        await interaction.response.send_message(embed=confirm_embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Suggestions(bot))
