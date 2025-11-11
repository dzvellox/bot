import discord
from discord.ext import commands
from discord import app_commands, Embed
import datetime

ROLE_ID_AUTORISE = 1401313791509266521
MEGA_LINK = "https://www.dropbox.com/scl/fi/z5bbnvry9fdfqc58h7hpn/app-release.apk?rlkey=17eoaogda2343xijuukl8bcrp&st=xmjlo1pn&dl=1"

# Palette de couleurs moderne
COLORS = {
    "primary": 0x5865F2,     # Bleu Discord
    "success": 0x57F287,     # Vert vibrant
    "android": 0x3DDC84,     # Vert Android
    "danger": 0xED4245,      # Rouge vibrant
    "info": 0x00D9FF         # Cyan
}

class DownloadView(discord.ui.View):
    def __init__(self, download_link: str):
        super().__init__(timeout=None)
        self.download_link = download_link
        
        # Ajouter le bouton de téléchargement avec lien
        download_button = discord.ui.Button(
            label="Download APK",
            emoji="📥",
            style=discord.ButtonStyle.link,
            url=download_link
        )
        self.add_item(download_button)
    
    @discord.ui.button(label="Installation Guide", emoji="📖", style=discord.ButtonStyle.secondary)
    async def guide_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        guide_embed = discord.Embed(
            title="📖 APK Installation Guide",
            description=(
                "Follow these steps to install the APK on your Android device:\n\n"
                "**Step 1: Enable Unknown Sources**\n"
                "```\n"
                "Settings → Security → Unknown Sources\n"
                "Enable installation from unknown sources\n"
                "```\n"
                "**Step 2: Download the APK**\n"
                "• Click the 'Download APK' button above\n"
                "• Wait for the download to complete\n\n"
                "**Step 3: Install**\n"
                "• Open your file manager\n"
                "• Navigate to Downloads folder\n"
                "• Tap on the APK file\n"
                "• Click 'Install'\n\n"
                "**Step 4: Launch**\n"
                "• Once installed, tap 'Open'\n"
                "• Grant any necessary permissions\n"
            ),
            color=COLORS["android"]
        )
        guide_embed.set_footer(text="💡 Tip: You may need to allow installations from this source")
        await interaction.response.send_message(embed=guide_embed, ephemeral=True)
    
    @discord.ui.button(label="Report Issue", emoji="🐛", style=discord.ButtonStyle.danger)
    async def report_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        report_embed = discord.Embed(
            description=(
                "## 🐛 Found a Bug?\n\n"
                "If you're experiencing issues with the APK, please report them:\n\n"
                "**Include:**\n"
                "• Your device model\n"
                "• Android version\n"
                "• Description of the issue\n"
                "• Steps to reproduce\n\n"
                "Contact support or open a ticket for assistance."
            ),
            color=COLORS["danger"]
        )
        await interaction.response.send_message(embed=report_embed, ephemeral=True)

class MegaDownload(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="apk", description="📱 Display the APK download link with instructions")
    async def apk_mega(self, interaction: discord.Interaction):
        # Vérifier si l'utilisateur a le rôle autorisé
        if not any(role.id == ROLE_ID_AUTORISE for role in interaction.user.roles):
            deny_embed = discord.Embed(
                description="🚫 **Access Denied**\n\nYou don't have permission to access the APK download.",
                color=COLORS["danger"]
            )
            await interaction.response.send_message(embed=deny_embed, ephemeral=True)
            return

        # Embed principal avec design moderne
        main_embed = discord.Embed(
            title="",
            description=(
                "## 📱 Android APK Download\n\n"
                "Download the latest version of our app for Android devices.\n\n"
                "**⚡ Quick Download**\n"
                "Click the button below to start your download immediately.\n"
            ),
            color=COLORS["android"],
            timestamp=datetime.datetime.now()
        )
        
        # Informations sur la version
        main_embed.add_field(
            name="📦 Package Info",
            value=(
                "```\n"
                "Platform: Android\n"
                "Format: APK\n"
                "Status: Latest Release\n"
                "```"
            ),
            inline=True
        )
        
        # Requirements
        main_embed.add_field(
            name="📋 Requirements",
            value=(
                "```\n"
                "Android 5.0+\n"
                "~50 MB storage\n"
                "Internet connection\n"
                "```"
            ),
            inline=True
        )
        
        # Instructions rapides
        main_embed.add_field(
            name="🚀 Quick Start",
            value=(
                "1️⃣ Click **Download APK** button\n"
                "2️⃣ Allow installation from unknown sources\n"
                "3️⃣ Install the downloaded file\n"
                "4️⃣ Open the app and enjoy!\n\n"
                "Need help? Click **Installation Guide** 📖"
            ),
            inline=False
        )
        
        # Warning
        main_embed.add_field(
            name="⚠️ Important Notice",
            value=(
                "```diff\n"
                "- Only download from official sources\n"
                "+ Enable 'Unknown Sources' before installing\n"
                "! Keep your device security settings updated\n"
                "```"
            ),
            inline=False
        )
        
        # Thumbnail Android logo
        main_embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/Android_logo_2019_%28stacked%29.svg/2346px-Android_logo_2019_%28stacked%29.svg.png")
        
        main_embed.set_footer(
            text=f"Shared by {interaction.user.name} • APK Distribution System",
            icon_url=interaction.user.display_avatar.url
        )

        # Créer la vue avec les boutons
        view = DownloadView(MEGA_LINK)

        # Envoyer avec style
        await interaction.response.send_message(
            content="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            embed=main_embed,
            view=view
        )

    @app_commands.command(name="apkinfo", description="📊 Show detailed information about the APK")
    async def apk_info(self, interaction: discord.Interaction):
        if not any(role.id == ROLE_ID_AUTORISE for role in interaction.user.roles):
            deny_embed = discord.Embed(
                description="🚫 **Access Denied**\n\nYou don't have permission to view APK information.",
                color=COLORS["danger"]
            )
            await interaction.response.send_message(embed=deny_embed, ephemeral=True)
            return

        info_embed = discord.Embed(
            title="📊 APK Information",
            description=(
                "Detailed information about the Android application package.\n"
            ),
            color=COLORS["info"]
        )
        
        info_embed.add_field(
            name="📦 Technical Details",
            value=(
                "```yaml\n"
                "File Type: APK (Android Package)\n"
                "Distribution: Dropbox CDN\n"
                "Architecture: Universal\n"
                "Signature: Signed Release\n"
                "```"
            ),
            inline=False
        )
        
        info_embed.add_field(
            name="🔒 Security",
            value=(
                "```\n"
                "✓ Digitally signed\n"
                "✓ Official release build\n"
                "✓ Verified source\n"
                "✓ No known malware\n"
                "```"
            ),
            inline=True
        )
        
        info_embed.add_field(
            name="⚙️ Compatibility",
            value=(
                "```\n"
                "• Android 5.0 - 14.0\n"
                "• ARM & x86 support\n"
                "• Phones & tablets\n"
                "• ~50 MB install size\n"
                "```"
            ),
            inline=True
        )
        
        info_embed.add_field(
            name="📱 Installation Methods",
            value=(
                "**Method 1: Direct Download**\n"
                "Use the `/apk` command to get the download link.\n\n"
                "**Method 2: Manual Install**\n"
                "Download → Enable Unknown Sources → Install\n\n"
                "**Method 3: ADB Install**\n"
                "```bash\n"
                "adb install app-release.apk\n"
                "```"
            ),
            inline=False
        )
        
        info_embed.set_footer(text="For download link, use /apk command")
        
        await interaction.response.send_message(embed=info_embed, ephemeral=True)

    @app_commands.command(name="apkhelp", description="❓ Get help with APK installation and troubleshooting")
    async def apk_help(self, interaction: discord.Interaction):
        help_embed = discord.Embed(
            title="❓ APK Help & Troubleshooting",
            description="Common issues and solutions for APK installation",
            color=COLORS["primary"]
        )
        
        help_embed.add_field(
            name="🚫 Can't Install APK",
            value=(
                "**Solution:**\n"
                "1. Enable 'Unknown Sources' in Settings\n"
                "2. Go to: Settings → Security → Install Unknown Apps\n"
                "3. Allow your browser/file manager to install apps\n"
            ),
            inline=False
        )
        
        help_embed.add_field(
            name="⚠️ Installation Blocked",
            value=(
                "**Solution:**\n"
                "1. Check your antivirus settings\n"
                "2. Temporarily disable Play Protect\n"
                "3. Try installing via file manager instead\n"
            ),
            inline=False
        )
        
        help_embed.add_field(
            name="📱 App Crashes on Launch",
            value=(
                "**Solution:**\n"
                "1. Clear app cache and data\n"
                "2. Restart your device\n"
                "3. Reinstall the APK\n"
                "4. Check Android version compatibility\n"
            ),
            inline=False
        )
        
        help_embed.add_field(
            name="🔄 Update Issues",
            value=(
                "**Solution:**\n"
                "1. Uninstall the old version first\n"
                "2. Download the latest APK\n"
                "3. Install the new version\n"
                "Note: Your data should be preserved\n"
            ),
            inline=False
        )
        
        help_embed.add_field(
            name="💬 Still Need Help?",
            value=(
                "If you're still experiencing issues:\n"
                "• Open a support ticket\n"
                "• Contact an administrator\n"
                "• Check our documentation\n"
            ),
            inline=False
        )
        
        help_embed.set_footer(text="💡 Most issues can be solved by enabling Unknown Sources")
        
        await interaction.response.send_message(embed=help_embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(MegaDownload(bot))