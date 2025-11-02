import discord
from discord.ext import commands, tasks
import asyncio
import os
from aiohttp import web, ClientSession
import logging
import traceback
from datetime import datetime

# Configuration du logging avec plus de détails
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
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

# Variables de monitoring
last_activity = datetime.now()
ping_count = 0
error_count = 0

# ----------------------------------------------------------------------
# 3. SERVEUR KEEP-ALIVE + PING-PONG
# ----------------------------------------------------------------------
async def keep_alive_server():
    """Serveur web pour Keep-Alive et recevoir les pings de B"""
    async def handle_health_check(request):
        global last_activity
        last_activity = datetime.now()
        
        status_info = {
            "bot_ready": bot.is_ready(),
            "bot_closed": bot.is_closed(),
            "guilds": len(bot.guilds) if bot.is_ready() else 0,
            "latency": f"{round(bot.latency * 1000, 2)}ms" if bot.is_ready() else "N/A",
            "last_activity": last_activity.isoformat(),
            "ping_count": ping_count,
            "error_count": error_count,
            "ping_task_running": ping_b_task.is_running() if hasattr(ping_b_task, 'is_running') else False
        }
        
        logger.debug(f"[HEALTH CHECK] {status_info}")
        
        if bot.is_ready():
            return web.json_response(status_info)
        else:
            return web.json_response(status_info, status=503)
    
    async def handle_ping(request):
        global last_activity
        last_activity = datetime.now()
        
        try:
            data = await request.json()
            logger.info(f"[A] 📨 Reçu de B : {data}")
            return web.json_response({
                "message": "pong from A",
                "status": "active",
                "bot_ready": bot.is_ready(),
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"[A] ❌ Erreur handle_ping : {e}")
            logger.debug(traceback.format_exc())
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
    global ping_count, error_count, last_activity
    
    try:
        ping_count += 1
        last_activity = datetime.now()
        
        payload = {
            "from": "A",
            "status": "alive",
            "timestamp": datetime.now().isoformat(),
            "ping_number": ping_count,
            "bot_ready": bot.is_ready()
        }
        
        logger.debug(f"[A] 📤 Envoi ping #{ping_count} à B...")
        
        async with session.post(SERVER_B_URL, json=payload, timeout=10) as resp:
            if resp.status == 200:
                resp_json = await resp.json()
                logger.info(f"[A] ✅ Réponse de B (ping #{ping_count}) : {resp_json}")
            else:
                error_count += 1
                logger.warning(f"[A] ⚠️ Status {resp.status} de B (ping #{ping_count})")
                
    except asyncio.TimeoutError:
        error_count += 1
        logger.error(f"[A] ⏱️ Timeout lors du ping #{ping_count} vers B")
    except Exception as e:
        error_count += 1
        logger.error(f"[A] ❌ Erreur ping #{ping_count} vers B : {e}")
        logger.debug(traceback.format_exc())

@ping_b_task.before_loop
async def before_ping_b():
    """Attendre que le bot soit prêt avant de commencer les pings"""
    logger.debug("[A] ⏳ En attente que le bot soit prêt...")
    await bot.wait_until_ready()
    logger.info("[A] ✅ Bot prêt, démarrage des pings vers B")

@ping_b_task.error
async def ping_b_task_error(error):
    """Gestion des erreurs de la tâche de ping"""
    global error_count
    error_count += 1
    logger.error(f"[A] 🔥 ERREUR CRITIQUE dans ping_b_task : {error}")
    logger.debug(traceback.format_exc())

# ----------------------------------------------------------------------
# 5. ÉVÉNEMENTS DU BOT - DEBUG COMPLET
# ----------------------------------------------------------------------
@bot.event
async def on_ready():
    global last_activity
    last_activity = datetime.now()
    
    logger.info("=" * 60)
    logger.info(f"🤖 BOT CONNECTÉ")
    logger.info(f"   Nom : {bot.user}")
    logger.info(f"   ID : {bot.user.id}")
    logger.info(f"   Serveurs : {len(bot.guilds)}")
    logger.info(f"   Latence : {round(bot.latency * 1000, 2)}ms")
    logger.info(f"   Time : {datetime.now()}")
    
    try:
        synced = await bot.tree.sync()
        logger.info(f"🔁 {len(synced)} commandes slash synchronisées")
    except Exception as e:
        logger.error(f"❌ Erreur de synchronisation : {e}")
        logger.debug(traceback.format_exc())
    
    # Démarrer la tâche de ping si elle n'est pas déjà lancée
    if not ping_b_task.is_running():
        logger.info("🚀 Démarrage de la tâche de ping...")
        ping_b_task.start()
    else:
        logger.warning("⚠️ Tâche de ping déjà en cours")
    
    logger.info("=" * 60)

@bot.event
async def on_disconnect():
    """Événement déclenché quand le bot se déconnecte"""
    logger.warning("🔴 BOT DÉCONNECTÉ DE DISCORD!")
    logger.warning(f"   Time : {datetime.now()}")
    logger.warning(f"   Pings effectués : {ping_count}")
    logger.warning(f"   Erreurs : {error_count}")

@bot.event
async def on_resumed():
    """Événement déclenché quand le bot se reconnecte"""
    global last_activity
    last_activity = datetime.now()
    logger.info("🟢 BOT RECONNECTÉ À DISCORD!")
    logger.info(f"   Time : {datetime.now()}")
    logger.info(f"   Latence : {round(bot.latency * 1000, 2)}ms")

@bot.event
async def on_error(event, *args, **kwargs):
    """Capture toutes les erreurs non gérées"""
    logger.error(f"🔥 ERREUR NON GÉRÉE dans l'événement : {event}")
    logger.error(f"   Args : {args}")
    logger.error(f"   Kwargs : {kwargs}")
    logger.debug(traceback.format_exc())

@bot.event
async def on_guild_join(guild):
    logger.info(f"➕ Bot ajouté au serveur : {guild.name} (ID: {guild.id})")

@bot.event
async def on_guild_remove(guild):
    logger.warning(f"➖ Bot retiré du serveur : {guild.name} (ID: {guild.id})")

@bot.event
async def on_connect():
    logger.info("🔗 WebSocket connecté à Discord")

@bot.event
async def on_shard_connect(shard_id):
    logger.debug(f"🔗 Shard {shard_id} connecté")

@bot.event
async def on_shard_disconnect(shard_id):
    logger.warning(f"🔴 Shard {shard_id} déconnecté")

# ----------------------------------------------------------------------
# 6. TÂCHE DE SURVEILLANCE
# ----------------------------------------------------------------------
@tasks.loop(minutes=2)
async def watchdog():
    """Surveille l'état du bot toutes les 2 minutes"""
    try:
        time_since_activity = (datetime.now() - last_activity).total_seconds()
        
        logger.info("=" * 60)
        logger.info(f"🔍 WATCHDOG CHECK")
        logger.info(f"   Bot prêt : {bot.is_ready()}")
        logger.info(f"   Bot fermé : {bot.is_closed()}")
        logger.info(f"   Latence : {round(bot.latency * 1000, 2)}ms" if bot.is_ready() else "   Latence : N/A")
        logger.info(f"   Dernière activité : il y a {int(time_since_activity)}s")
        logger.info(f"   Pings envoyés : {ping_count}")
        logger.info(f"   Erreurs : {error_count}")
        logger.info(f"   Tâche ping active : {ping_b_task.is_running()}")
        logger.info(f"   Serveurs : {len(bot.guilds)}")
        logger.info("=" * 60)
        
        # Alerte si pas d'activité depuis 5 minutes
        if time_since_activity > 300:
            logger.error(f"⚠️⚠️⚠️ AUCUNE ACTIVITÉ DEPUIS {int(time_since_activity)}s !")
        
        # Alerte si la tâche de ping ne tourne pas
        if bot.is_ready() and not ping_b_task.is_running():
            logger.error("⚠️⚠️⚠️ TÂCHE DE PING ARRÊTÉE ALORS QUE LE BOT EST PRÊT!")
            logger.info("🔄 Tentative de redémarrage de la tâche...")
            try:
                ping_b_task.start()
            except Exception as e:
                logger.error(f"❌ Impossible de redémarrer la tâche : {e}")
        
    except Exception as e:
        logger.error(f"❌ Erreur dans watchdog : {e}")
        logger.debug(traceback.format_exc())

@watchdog.before_loop
async def before_watchdog():
    await bot.wait_until_ready()
    logger.info("🐕 Watchdog démarré")

# ----------------------------------------------------------------------
# 7. GESTION PROPRE DE L'ARRÊT
# ----------------------------------------------------------------------
async def cleanup():
    """Nettoyage des ressources avant fermeture"""
    logger.info("🧹 Nettoyage en cours...")
    
    # Arrêter les tâches
    if ping_b_task.is_running():
        ping_b_task.cancel()
        logger.debug("   Tâche ping arrêtée")
    
    if watchdog.is_running():
        watchdog.cancel()
        logger.debug("   Watchdog arrêté")
    
    # Fermer la session HTTP
    if session and not session.closed:
        await session.close()
        logger.debug("   Session HTTP fermée")
    
    # Fermer le bot
    if not bot.is_closed():
        await bot.close()
        logger.debug("   Bot fermé")
    
    logger.info("✅ Nettoyage terminé")

# ----------------------------------------------------------------------
# 8. DÉMARRAGE PRINCIPAL
# ----------------------------------------------------------------------
async def main():
    global session
    
    logger.info("🚀 DÉMARRAGE DU BOT")
    logger.info(f"   Python : {os.sys.version}")
    logger.info(f"   Discord.py : {discord.__version__}")
    
    # Créer la session HTTP
    session = ClientSession()
    logger.debug("   Session HTTP créée")
    
    try:
        # Charger les cogs
        cogs_to_load = [
            "cogs.status",
            "cogs.support",
            "cogs.update",
            "cogs.suggestion",
            "cogs.MegaDownload"
        ]
        
        logger.info("📦 Chargement des cogs...")
        for cog in cogs_to_load:
            try:
                await bot.load_extension(cog)
                logger.info(f"   ✅ {cog}")
            except Exception as e:
                logger.error(f"   ❌ {cog} : {e}")
                logger.debug(traceback.format_exc())
        
        # Lancer le serveur Keep-Alive
        logger.info("🌐 Démarrage du serveur Keep-Alive...")
        asyncio.create_task(keep_alive_server())
        
        # Démarrer le watchdog
        logger.info("🐕 Démarrage du watchdog...")
        watchdog.start()
        
        # Vérifier le token
        TOKEN = os.getenv("DISCORD_TOKEN")
        if not TOKEN:
            logger.error("❌ ERREUR FATALE : Variable DISCORD_TOKEN manquante")
            return
        
        logger.debug(f"   Token : {TOKEN[:20]}...")
        
        # Démarrer le bot
        logger.info("🤖 Connexion à Discord...")
        await bot.start(TOKEN)
        
    except KeyboardInterrupt:
        logger.info("⌨️ Interruption clavier détectée")
    except discord.LoginFailure:
        logger.error("❌ ÉCHEC DE CONNEXION : Token Discord invalide")
    except Exception as e:
        logger.error(f"❌ ERREUR FATALE : {e}")
        logger.debug(traceback.format_exc())
    finally:
        await cleanup()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Arrêt du bot")
    except Exception as e:
        logger.error(f"❌ Erreur au démarrage : {e}")
        logger.debug(traceback.format_exc())
