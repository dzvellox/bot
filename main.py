import discord
from discord.ext import commands, tasks
import asyncio
import os
from aiohttp import web, ClientSession
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------
# 1. CONFIG BOT DISCORD
# ----------------------------------------------------------------------
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents)

# ----------------------------------------------------------------------
# 2. CONFIG PING-PONG
# ----------------------------------------------------------------------
SERVER_B_URL = "https://pong-jfd2.onrender.com/ping"
session = None  # Sera initialisé dans main()

# ----------------------------------------------------------------------
# 3. SERVEUR KEEP-ALIVE + PING-PONG
# ----------------------------------------------------------------------
async def keep_alive_server():
    """Serveur web pour Keep-Alive et recevoir les pings de B"""
    async def handle_health_check(request):
        # Vérifier si le bot est vraiment connecté
        if bot.is_ready():
            return web.Response(text="Bot is running and connected.")
        else:
            return web.Response(text="Bot is starting...", status=503)
    
    async def handle_ping(request):
        try:
            data = await request.json()
            logger.info(f"[A] Reçu de B : {data}")
            return web.json_response({"message": "pong from A", "status": "active"})
        except Exception as e:
            logger.error(f"[A] Erreur handle_ping : {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    PORT = int(os.environ.get("PORT", 8080))
    app = web.Application()
    app.router.add_get("/", handle_health_check)
    app.router.add_post("/ping", handle_ping)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logger.info(f"🌐 Serveur Keep-Alive démarré sur 0.0.0.0:{PORT}")

# ----------------------------------------------------------------------
# 4. TÂCHE ASYNCHRONE PING PONG VERS B (avec tasks.loop)
# ----------------------------------------------------------------------
@tasks.loop(seconds=20)
async def ping_b_task():
    """Tâche de ping vers le serveur B"""
    try:
        payload = {"from": "A", "status": "alive"}
        logger.info("[A] Envoi à B...")
        
        async with session.post(SERVER_B_URL, json=payload, timeout=10) as resp:
            if resp.status == 200:
                resp_json = await resp.json()
                logger.info(f"[A] ✅ Réponse de B : {resp_json}")
            else:
                logger.warning(f"[A] ⚠️ Status {resp.status} de B")
    except asyncio.TimeoutError:
        logger.error("[A] ⏱️ Timeout lors du ping vers B")
    except Exception as e:
        logger.error(f"[A] ❌ Erreur ping B : {e}")

@ping_b_task.before_loop
async def before_ping_b():
    """Attendre que le bot soit prêt avant de commencer les pings"""
    await bot.wait_until_ready()
    logger.info("[A] Bot prêt, démarrage des pings vers B")

# ----------------------------------------------------------------------
# 5. ÉVÉNEMENTS DU BOT
# ----------------------------------------------------------------------
@bot.event
async def on_ready():
    logger.info("---------------------------------------")
    logger.info(f"🤖 Bot connecté : {bot.user} (ID: {bot.user.id})")
    logger.info(f"📊 Connecté à {len(bot.guilds)} serveur(s)")
    
    try:
        synced = await bot.tree.sync()
        logger.info(f"🔁 {len(synced)} commandes slash synchronisées")
    except Exception as e:
        logger.error(f"❌ Erreur de synchronisation : {e}")
    
    # Démarrer la tâche de ping si elle n'est pas déjà lancée
    if not ping_b_task.is_running():
        ping_b_task.start()
    
    logger.info("---------------------------------------")

@bot.event
async def on_disconnect():
    """Événement déclenché quand le bot se déconnecte"""
    logger.warning("⚠️ Bot déconnecté de Discord!")

@bot.event
async def on_resumed():
    """Événement déclenché quand le bot se reconnecte"""
    logger.info("🔄 Bot reconnecté à Discord!")

# ----------------------------------------------------------------------
# 6. GESTION PROPRE DE L'ARRÊT
# ----------------------------------------------------------------------
async def cleanup():
    """Nettoyage des ressources avant fermeture"""
    logger.info("🧹 Nettoyage en cours...")
    
    # Arrêter la tâche de ping
    if ping_b_task.is_running():
        ping_b_task.cancel()
    
    # Fermer la session HTTP
    if session and not session.closed:
        await session.close()
    
    # Fermer le bot
    if not bot.is_closed():
        await bot.close()
    
    logger.info("✅ Nettoyage terminé")

# ----------------------------------------------------------------------
# 7. DÉMARRAGE PRINCIPAL
# ----------------------------------------------------------------------
async def main():
    global session
    
    # Créer la session HTTP
    session = ClientSession()
    
    try:
        # Charger les cogs
        cogs_to_load = [
            "cogs.status",
            "cogs.support",
            "cogs.update",
            "cogs.suggestion",
            "cogs.MegaDownload"
        ]
        
        for cog in cogs_to_load:
            try:
                await bot.load_extension(cog)
                logger.info(f"✅ Cog chargé : {cog}")
            except Exception as e:
                logger.error(f"❌ Erreur chargement {cog} : {e}")
        
        # Lancer le serveur Keep-Alive
        asyncio.create_task(keep_alive_server())
        
        # Vérifier le token
        TOKEN = os.getenv("DISCORD_TOKEN")
        if not TOKEN:
            logger.error("❌ ERREUR : Variable DISCORD_TOKEN manquante")
            return
        
        # Démarrer le bot
        logger.info("🚀 Démarrage du bot...")
        await bot.start(TOKEN)
        
    except KeyboardInterrupt:
        logger.info("⌨️ Interruption clavier détectée")
    except Exception as e:
        logger.error(f"❌ Erreur fatale : {e}")
    finally:
        await cleanup()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Arrêt du bot")
