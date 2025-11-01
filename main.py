import discord
from discord.ext import commands
import asyncio
import os
from aiohttp import web, ClientSession

# ----------------------------------------------------------------------
# 1. CONFIG BOT DISCORD
# ----------------------------------------------------------------------
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents)

# ----------------------------------------------------------------------
# 2. CONFIG PING-PONG
# ----------------------------------------------------------------------
SERVER_B_URL = "https://pong-jfd2.onrender.com/ping"  # URL du serveur B
session: ClientSession = None  # Session aiohttp globale

# ----------------------------------------------------------------------
# 3. SERVEUR KEEP-ALIVE + PING-PONG
# ----------------------------------------------------------------------
async def keep_alive_server():
    """Serveur web pour Keep-Alive et recevoir les pings de B"""
    try:
        async def handle_health_check(request):
            return web.Response(text="Bot is running and port is bound.")

        async def handle_ping(request):
            data = await request.json()
            print(f"[A] Reçu de B : {data}")
            return web.json_response({"message": "pong from A"})

        PORT = int(os.environ.get("PORT", 8080))
        app = web.Application()
        app.router.add_get("/", handle_health_check)
        app.router.add_post("/ping", handle_ping)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", PORT)
        await site.start()
        print(f"🌐 Serveur Keep-Alive démarré sur 0.0.0.0:{PORT}")

    except Exception as e:
        print(f"❌ Keep-Alive échoué : {e}")

# ----------------------------------------------------------------------
# 4. BOUCLE ASYNCHRONE PING PONG VERS B
# ----------------------------------------------------------------------
async def ping_b_loop():
    global session
    await bot.wait_until_ready()  # attend que le bot soit prêt
    while True:
        try:
            payload = {"from": "A"}
            print("[A] Envoi à B :", payload)
            async with session.post(SERVER_B_URL, json=payload, timeout=10) as resp:
                resp_json = await resp.json()
                print("[A] Réponse de B :", resp_json)
        except Exception as e:
            print("[A] Erreur ping B :", e)
        await asyncio.sleep(20)

# ----------------------------------------------------------------------
# 5. ÉVÉNEMENTS DU BOT
# ----------------------------------------------------------------------
@bot.event
async def on_ready():
    print("---------------------------------------")
    print(f"🤖 Bot connecté en tant que {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔁 {len(synced)} commandes slash synchronisées.")
    except Exception as e:
        print(f"❌ Erreur de synchronisation : {e}")
    print("---------------------------------------")

@bot.event
async def on_disconnect():
    """Ferme la session aiohttp proprement."""
    global session
    print("🔌 Déconnexion du bot. Fermeture de la session aiohttp.")
    if session and not session.closed:
        await session.close()

# ----------------------------------------------------------------------
# 6. CHARGEMENT DES COGS
# ----------------------------------------------------------------------
async def setup_cogs(bot: commands.Bot):
    """Charge les cogs de manière asynchrone."""
    cogs = ["cogs.status", "cogs.support", "cogs.update", "cogs.suggestion", "cogs.MegaDownload"]
    for cog in cogs:
        try:
            await bot.load_extension(cog)
            print(f"✅ Cog {cog} chargé.")
        except Exception as e:
            print(f"❌ Erreur de chargement du cog {cog}: {e}")

# ----------------------------------------------------------------------
# 7. TÂCHES DE FOND
# ----------------------------------------------------------------------
async def start_background_tasks(bot: commands.Bot):
    """Démarre le serveur Keep-Alive et la boucle Ping-Pong."""
    global session
    session = ClientSession()  # création de la session ici
    # Démarrer le serveur Keep-Alive
    bot.loop.create_task(keep_alive_server())
    print("🚀 Tâche Keep-Alive démarrée.")
    # Démarrer la boucle ping vers B
    bot.loop.create_task(ping_b_loop())
    print("🚀 Tâche Ping-Pong démarrée.")

# ----------------------------------------------------------------------
# 8. SETUP HOOK POUR LANCER LES COGS ET LES TÂCHES DE FOND
# ----------------------------------------------------------------------
async def setup_hook():
    await asyncio.gather(
        setup_cogs(bot),
        start_background_tasks(bot)
    )

bot.setup_hook = setup_hook

# ----------------------------------------------------------------------
# 9. DÉMARRAGE PRINCIPAL
# ----------------------------------------------------------------------
if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    if not TOKEN:
        print("❌ ERREUR : La variable DISCORD_TOKEN est manquante.")
    else:
        bot.run(TOKEN)