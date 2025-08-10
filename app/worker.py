import asyncio
import os
import aiohttp
import motor.motor_asyncio
from dotenv import load_dotenv
from app.websocket_handler import broadcast

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client.crypto_dashboard
COIN_IDS = ["bitcoin", "ethereum", "solana"]


async def fetch_prices(session, coin_ids):
    ids_string = ",".join(coin_ids)
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids_string}&vs_currencies=usd&include_24hr_change=true"
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            data = await response.json()
            print(f"Получены данные: {data}")
            return data
    except Exception as e:
        print(f"Ошибка при запросе к API: {e}")
        return None


async def worker_loop(clients):
    print("Воркер запущен...")
    async with aiohttp.ClientSession() as session:
        while True:
            print("--- Новая итерация воркера ---")
            price_data = await fetch_prices(session, COIN_IDS)

            if price_data:
                document = {"prices": price_data, "timestamp": asyncio.get_event_loop().time()}
                await db.prices.insert_one(document)
                print("Данные сохранены в MongoDB.")

                await broadcast(price_data)
                print(f"Данные отправлены {len(clients)} клиентам.")

            await asyncio.sleep(10)
