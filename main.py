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
SERVER_B_URL = "srv-d3rugsi4d50c73fmnt8g/ping"  # URL du serveur B (à modifier)

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
# 6. DÉMARRAGE PRINCIPAL
# ----------------------------------------------------------------------
async def main():
    # Charger les cogs
    try:
        await bot.load_extension("cogs.status")
        await bot.load_extension("cogs.support")
        await bot.load_extension("cogs.update")
        await bot.load_extension("cogs.suggestion")
        await bot.load_extension("cogs.MegaDownload")
        print("✅ Cogs chargés avec succès.")
    except Exception as e:
        print(f"❌ Erreur lors du chargement des cogs : {e}")

    # Lancer le serveur Keep-Alive + Ping-Pong
    asyncio.create_task(keep_alive_server())

    # Lancer la boucle ping vers B
    asyncio.create_task(ping_b_loop())

    # Lancer le bot
    TOKEN = os.getenv("DISCORD_TOKEN")
    if not TOKEN:
        print("❌ ERREUR : La variable DISCORD_TOKEN est manquante.")
        return
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())

