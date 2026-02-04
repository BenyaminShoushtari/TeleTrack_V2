import re
import json
import asyncio
import logging
import os
from datetime import datetime
from typing import Optional, Set

import aiosqlite
import jdatetime
from telethon import TelegramClient, events
import websockets
from dotenv import load_dotenv

# ========= CONFIG =========
load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID", 0))
API_HASH = os.getenv("TELEGRAM_API_HASH", "")

CHANNEL = os.getenv("TELEGRAM_CHANNEL", "abshodeh_hanzaei")
SESSION_NAME = os.getenv("SESSION_NAME", "mazaneh_session")

WS_HOST = os.getenv("WS_HOST", "0.0.0.0")
WS_PORT = int(os.getenv("WS_PORT", 8765))

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

DB_PATH = "TeleTrack_V2.db"
MAX_DB_MB = 500
# ==========================

# ---------- Logging ----------
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('TeleTrack_V2_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ---------- Time ----------
def get_shamsi_now():
    return jdatetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

def get_gregorian_now():
    return datetime.now().isoformat()

# ---------- DB Size ----------
def get_db_size_mb():
    if not os.path.exists(DB_PATH):
        return 0
    return os.path.getsize(DB_PATH) / (1024 * 1024)

# ---------- SQLite ----------
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS mazaneh_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            price INTEGER NOT NULL,
            created_at_gregorian TEXT NOT NULL,
            created_at_shamsi TEXT NOT NULL
        )
        """)
        await db.commit()

async def cleanup_database():
    size = get_db_size_mb()

    if size < MAX_DB_MB:
        return

    async with aiosqlite.connect(DB_PATH) as db:

        async with db.execute("SELECT COUNT(*) FROM mazaneh_prices") as cur:
            total = (await cur.fetchone())[0]

        delete_count = int(total * 0.2)

        await db.execute(f"""
            DELETE FROM mazaneh_prices
            WHERE id IN (
                SELECT id FROM mazaneh_prices
                ORDER BY id ASC
                LIMIT {delete_count}
            )
        """)

        await db.commit()

    logger.warning(f"DB cleanup → deleted {delete_count} old records")

async def insert_price(price: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO mazaneh_prices 
            (price, created_at_gregorian, created_at_shamsi)
            VALUES (?, ?, ?)
            """,
            (price, get_gregorian_now(), get_shamsi_now())
        )
        await db.commit()

    await cleanup_database()

async def get_last_price():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT price FROM mazaneh_prices ORDER BY id DESC LIMIT 1"
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def get_last_timestamp():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """
            SELECT created_at_shamsi 
            FROM mazaneh_prices 
            ORDER BY id DESC LIMIT 1
            """
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

# ---------- Telegram ----------
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# ---------- WebSocket ----------
connected_clients: Set[websockets.WebSocketServerProtocol] = set()

# ---------- Utils ----------
def fa_to_en(text: str) -> str:
    persian_numbers = "۰۱۲۳۴۵۶۷۸۹"
    english_numbers = "0123456789"
    mapping = str.maketrans(persian_numbers, english_numbers)
    return text.translate(mapping)

def extract_mesghal_sell(text: str) -> Optional[int]:
    text = fa_to_en(text)
    text = re.sub(r'\s+', ' ', text)

    required_keywords = ["نقد فردا", "فروش"]
    if not all(keyword in text for keyword in required_keywords):
        return None

    patterns = [
        r"نقد\s*فردا\s*:\s*فروش\s*([\d,]+)\s*تومان",
        r"فروش\s*نقد\s*فردا\s*:\s*([\d,]+)",
        r"نقد\s*فردا.*?فروش.*?([\d,]+)",
        r"با\s*قیمت\s*([\d,]+).*?نقد\s*فردا",
        r"هر\s*مثقال.*?([\d,]+).*?نقد\s*فردا",
        r"فروش\s*:\s*([\d,]+).*?نقد\s*فردا",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            try:
                return int(match.group(1).replace(',', '').strip())
            except:
                continue

    return None

# ---------- Telegram Handler ----------
@client.on(events.NewMessage(chats=CHANNEL))
async def handler(event):
    if not event.message.text:
        return

    price = extract_mesghal_sell(event.message.text)

    if not price:
        return

    logger.info(f"Extracted price: {price}")

    try:
        last_price = await get_last_price()

        if last_price and last_price == price:
            return

        await insert_price(price)

        payload = json.dumps({
            "type": "mazaneh_update",
            "price": price,
            "timestamp": get_shamsi_now(),
            "previous_price": last_price
        })

        dead = set()
        for ws in connected_clients:
            try:
                await ws.send(payload)
            except:
                dead.add(ws)

        connected_clients.difference_update(dead)

    except Exception as e:
        logger.error(f"Handler error: {e}")

# ---------- WebSocket ----------
async def ws_handler(websocket):
    connected_clients.add(websocket)

    try:
        last_price = await get_last_price()
        timestamp = await get_last_timestamp()

        await websocket.send(json.dumps({
            "type": "init",
            "price": last_price,
            "timestamp": timestamp
        }))

        async for msg in websocket:
            if msg == "ping":
                await websocket.send("pong")

    finally:
        connected_clients.discard(websocket)

# ---------- Main ----------
async def main():
    logger.info("Starting TeleTrack_V2 Monitor")

    await init_db()

    await client.start()
    logger.info("Telegram Connected")

    ws_server = await websockets.serve(
        ws_handler,
        WS_HOST,
        WS_PORT,
        ping_interval=20,
        ping_timeout=10
    )

    logger.info(f"WebSocket server running → ws://{WS_HOST}:{WS_PORT}")

    await asyncio.gather(
        client.run_until_disconnected(),
        ws_server.wait_closed()
    )

if __name__ == "__main__":
    asyncio.run(main())
