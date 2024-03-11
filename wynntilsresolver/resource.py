"""
Author       : FYWinds i@windis.cn
Date         : 2024-02-29 15:48:21
LastEditors  : FYWinds i@windis.cn
LastEditTime : 2024-03-10 22:39:35
FilePath     : /wynntilsresolver/resource.py
"""

import asyncio
import json
import os
import pathlib
import time

import httpx

from .utils import run_async

if os.name == "nt":
    DATA_LOCATION = pathlib.Path.home() / "AppData" / "Local" / "wynntilsresolver"
else:
    DATA_LOCATION = pathlib.Path.home() / ".local" / "share" / "wynntilsresolver"

DATA_LOCATION.mkdir(parents=True, exist_ok=True)

ITEMDB_FULL_URL = "https://api.wynncraft.com/v3/item/database?fullResult"
SHINY_TABLE_URL = "https://raw.githubusercontent.com/Wynntils/Static-Storage/main/Data-Storage/shiny_stats.json"
ID_TABLE_URL = "https://raw.githubusercontent.com/Wynntils/Static-Storage/main/Reference/id_keys.json"

ITEMDB_PATH = DATA_LOCATION / "itemdb.json"
SHINY_TABLE_PATH = DATA_LOCATION / "shiny_stats.json"
ID_TABLE_PATH = DATA_LOCATION / "id_keys.json"


@run_async
async def startup():
    """Fetch all data from Wynncraft API and Artemis Repository."""
    client = httpx.AsyncClient()

    # Fetch the file only if was not updated within 24 hours.
    tasks = []
    if not ITEMDB_PATH.exists() or time.time() - os.path.getmtime(ITEMDB_PATH) > 86400:
        tasks += [fetch_item_db(client)]
    if not SHINY_TABLE_PATH.exists() or time.time() - os.path.getmtime(SHINY_TABLE_PATH) > 86400:
        tasks += [fetch_shiny_table(client)]
    if not ID_TABLE_PATH.exists() or time.time() - os.path.getmtime(ID_TABLE_PATH) > 86400:
        tasks += [fetch_id_table(client)]
    await asyncio.gather(*tasks)

    await client.aclose()


last_update = 0


def should_update():
    global last_update
    """Check if the data should be updated."""
    if (time.time() - last_update) <= 86400:
        return False
    if not ITEMDB_PATH.exists() or time.time() - os.path.getmtime(ITEMDB_PATH) > 86400:
        return True
    if not SHINY_TABLE_PATH.exists() or time.time() - os.path.getmtime(SHINY_TABLE_PATH) > 86400:
        return True
    if not ID_TABLE_PATH.exists() or time.time() - os.path.getmtime(ID_TABLE_PATH) > 86400:
        return True
    last_update = time.time()
    return False


if not should_update():
    with open(ITEMDB_PATH, encoding="utf-8") as f:
        ITEMDB = json.load(f)

    with open(ID_TABLE_PATH, encoding="utf-8") as f:
        ID_TABLE = json.load(f)

    with open(SHINY_TABLE_PATH, encoding="utf-8") as f:
        SHINY_TABLE = json.load(f)
else:
    ITEMDB = {}
    ID_TABLE = {}
    SHINY_TABLE = []


RESOURCES = {
    "ITEMDB": ITEMDB,
    "ID_TABLE": ID_TABLE,
    "SHINY_TABLE": SHINY_TABLE,
}


async def fetch_item_db(client: httpx.AsyncClient):
    data = await client.get(ITEMDB_FULL_URL)
    with open(DATA_LOCATION / "itemdb.json", "w", encoding="utf-8") as f:
        json.dump(data.json(), f, ensure_ascii=False)
    RESOURCES["ITEM_DB"] = data.json()


async def fetch_shiny_table(client: httpx.AsyncClient):
    global SHINY_TABLE
    data = await client.get(SHINY_TABLE_URL)
    with open(DATA_LOCATION / "shiny_stats.json", "w", encoding="utf-8") as f:
        json.dump(data.json(), f, ensure_ascii=False)
    RESOURCES["SHINY_TABLE"] = data.json()


async def fetch_id_table(client: httpx.AsyncClient):
    global ID_TABLE
    data = await client.get(ID_TABLE_URL)
    with open(DATA_LOCATION / "id_keys.json", "w", encoding="utf-8") as f:
        json.dump(data.json(), f, ensure_ascii=False)
    RESOURCES["ID_TABLE"] = data.json()
