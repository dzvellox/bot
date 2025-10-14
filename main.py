import discord
from discord.ext import commands
import asyncio
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"🔁 {len(synced)} commandes slash synchronisées.")
    except Exception as e:
        print(f"Erreur de synchronisation : {e}")

async def main():
    await bot.load_extension("cogs.status")
    await bot.load_extension("cogs.support")
    await bot.load_extension("cogs.update")
    await bot.load_extension("cogs.suggestion")
    await bot.load_extension("cogs.MegaDownload")

    # Récupère le token depuis les variables d'environnement Render
    TOKEN = os.getenv("DISCORD_TOKEN")

    if not TOKEN:
        print("❌ ERREUR : aucune variable DISCORD_TOKEN trouvée !")
        return

    await bot.start(TOKEN)

asyncio.run(main())
