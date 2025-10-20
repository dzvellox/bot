import discord
from discord.ext import commands
import asyncio
import os
from aiohttp import web # Importation spécifique pour le serveur web

# Configuration de base
intents = discord.Intents.all()
# Note: L'intents.all() n'est pas recommandé pour les grands bots en production
# Utilisez uniquement les intents nécessaires pour optimiser les performances.
bot = commands.Bot(command_prefix="/", intents=intents)

# ----------------------------------------------------------------------
# 1. SERVER DE 'KEEP-ALIVE' (SOLUTION AU TIMEOUT)
# ----------------------------------------------------------------------

async def keep_alive_server():
    """Démarre un petit serveur web sur le port requis par la plateforme
    (ex: Render) pour éviter le 'Port scan timeout'.
    """
    # 1. Définir le gestionnaire de requête
    async def handle_health_check(request):
        # Réponse simple pour le "Health Check"
        return web.Response(text="Bot is running and port is bound.")

    # 2. Récupérer la variable d'environnement PORT, ou utiliser 8080 par défaut
    PORT = int(os.environ.get("PORT", 8080))
    
    # 3. Configuration et démarrage du serveur aiohttp
    app = web.Application()
    app.router.add_get('/', handle_health_check) # Attachement à l'URL racine
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Lier à '0.0.0.0' pour être accessible par l'environnement
    site = web.TCPSite(runner, '0.0.0.0', PORT) 
    await site.start()
    
    print(f"🌐 Serveur Keep-Alive démarré sur 0.0.0.0:{PORT}")

# ----------------------------------------------------------------------
# 2. ÉVÉNEMENTS DU BOT DISCORD
# ----------------------------------------------------------------------

@bot.event
async def on_ready():
    """Est appelé lorsque le bot est connecté à Discord."""
    print("---------------------------------------")
    print(f"🤖 Bot connecté en tant que {bot.user}")
    
    try:
        # Synchronisation des commandes slash
        synced = await bot.tree.sync()
        print(f"🔁 {len(synced)} commandes slash synchronisées.")
    except Exception as e:
        print(f"❌ Erreur de synchronisation : {e}")
        
    print("---------------------------------------")

# ----------------------------------------------------------------------
# 3. CHARGEMENT DES COGS ET DÉMARRAGE
# ----------------------------------------------------------------------

async def main():
    """Fonction principale pour charger les extensions et démarrer le bot."""
    
    # 3.1. Chargement des extensions (Cogs)
    print("Chargement des cogs...")
    try:
        await bot.load_extension("cogs.status")
        await bot.load_extension("cogs.support")
        await bot.load_extension("cogs.update")
        await bot.load_extension("cogs.suggestion")
        await bot.load_extension("cogs.MegaDownload")
        print("✅ Cogs chargés avec succès.")
    except Exception as e:
        print(f"❌ ERREUR lors du chargement des cogs : {e}")
        
    # 3.2. Lancement du serveur Keep-Alive en tâche de fond
    # Il doit être lancé AVANT le bot.start()
    asyncio.create_task(keep_alive_server())

    # 3.3. Récupération du Token et lancement du Bot
    TOKEN = os.getenv("DISCORD_TOKEN")
    if not TOKEN:
        print("❌ ERREUR : La variable DISCORD_TOKEN est manquante.")
        return

    # Cette ligne est bloquante et maintiendra le bot en ligne
    await bot.start(TOKEN)

if __name__ == "__main__":
    # Point d'entrée de l'application
    asyncio.run(main())