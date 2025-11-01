import discord
from discord.ext import commands, tasks
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
SERVER_B_URL = "https://pong-jfd2.onrender.com/ping"  # URL du serveur B (à modifier)

# Session HTTP globale
session = ClientSession()

# ----------------------------------------------------------------------
# 3. SERVEUR KEEP-ALIVE + PING-PONG
# ----------------------------------------------------------------------
async def keep_alive_server():
    """Serveur web pour Keep-Alive et recevoir les pings de B"""
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
    print(f"🌐 Serveur Keep-Alive + Ping-Pong démarré sur 0.0.0.0:{PORT}")

# ----------------------------------------------------------------------
# 4. TÂCHE ASYNCHRONE PING PONG VERS B
# ----------------------------------------------------------------------
async def ping_b_loop():
    await bot.wait_until_ready()  # attend que le bot soit prêt
    while True:
        try:
            payload = {"from": "A"}
            print("[A] Envoi à B :", payload)
            async with session.post(SERVER_B_URL, json=payload, timeout=10) as resp:
                resp_json = await resp.json()
                print("[A] Réponse de B :", resp_json)
        except Exception as e:
            print("[A] Erreur :", e)
        await asyncio.sleep(20)  # attente 20 secondes

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

# ----------------------------------------------------------------------
# 6. NOUVELLE STRUCTURE DE DÉMARRAGE
# ----------------------------------------------------------------------

# (Laisser tout le code précédent tel quel, y compris 1, 2, 3, 4, 5)

async def setup_cogs(bot: commands.Bot):
    """Charge les cogs de manière asynchrone."""
    cogs = ["cogs.status", "cogs.support", "cogs.update", "cogs.suggestion", "cogs.MegaDownload"]
    for cog in cogs:
        try:
            await bot.load_extension(cog)
            print(f"✅ Cog {cog} chargé.")
        except Exception as e:
            print(f"❌ Erreur de chargement du cog {cog}: {e}")

async def start_background_tasks(bot: commands.Bot):
    """Démarre le serveur Keep-Alive et la boucle Ping-Pong."""
    # Lancer le serveur Keep-Alive + Ping-Pong
    # Note : Le serveur web doit être démarré en tant que tâche de fond.
    bot.loop.create_task(keep_alive_server())
    print("🚀 Tâche Keep-Alive démarrée.")

    # Lancer la boucle ping vers B
    # Si vous utilisez la version @tasks.loop, utilisez :
    # ping_b_loop.start() 
    # Si vous gardez la version async def :
    bot.loop.create_task(ping_b_loop())
    print("🚀 Tâche Ping-Pong démarrée.")


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
    print("🔌 Déconnexion du bot. Fermeture de la session aiohttp.")
    if not session.closed:
        await session.close()
        

# ----------------------------------------------------------------------
# DÉMARRAGE PRINCIPAL (Le seul bloc "if __name__")
# ----------------------------------------------------------------------

# On s'assure que les tâches de fond sont démarrées dans la boucle d'événements du bot.
# La méthode 'setup_hook' est appelée juste avant que le bot ne se connecte à Discord.
bot.setup_hook = lambda: asyncio.gather(
    setup_cogs(bot),
    start_background_tasks(bot)
)

if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    if not TOKEN:
        print("❌ ERREUR : La variable DISCORD_TOKEN est manquante.")
    else:
        # bot.run() démarre tout : la boucle, les cogs (via setup_hook), et la connexion Discord.
        bot.run(TOKEN)


