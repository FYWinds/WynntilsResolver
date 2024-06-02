"""
Author       : FYWinds i@windis.cn
Date         : 2024-02-29 15:48:21
LastEditors  : FYWinds i@windis.cn
LastEditTime : 2024-06-02 11:34:26
FilePath     : /wynntilsresolver/startup.py
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

if data_location := os.environ.get("DATA_LOCATION"):
    DATA_LOCATION = pathlib.Path(data_location)

DATA_LOCATION.mkdir(parents=True, exist_ok=True)


ITEMDB_FULL_URL = "https://api.wynncraft.com/v3/item/database?fullResult"
SHINY_TABLE_URL = "https://raw.githubusercontent.com/Wynntils/Static-Storage/main/Data-Storage/shiny_stats.json"
ID_TABLE_URL = "https://raw.githubusercontent.com/Wynntils/Static-Storage/main/Reference/id_keys.json"

itemdb_path = os.environ.get("ITEMDB_PATH")
shiny_table_path = os.environ.get("SHINY_TABLE_PATH")
id_table_path = os.environ.get("ID_TABLE_PATH")

itemdb_should_update = True
shiny_table_should_update = True
id_table_should_update = True

if itemdb_path:
    itemdb_should_update = False
if shiny_table_path:
    shiny_table_should_update = False
if id_table_path:
    id_table_should_update = False

ITEMDB_PATH = pathlib.Path(itemdb_path or DATA_LOCATION / "itemdb.json")
SHINY_TABLE_PATH = pathlib.Path(shiny_table_path or DATA_LOCATION / "shiny_stats.json")
ID_TABLE_PATH = pathlib.Path(id_table_path or DATA_LOCATION / "id_keys.json")

# Read proxy from environment variable.
http_proxy = os.environ.get("http_proxy") or os.environ.get("HTTP_PROXY")
https_proxy = os.environ.get("https_proxy") or os.environ.get("HTTPS_PROXY")
all_proxy = os.environ.get("all_proxy") or os.environ.get("ALL_PROXY")


@run_async
async def startup():
    """Fetch all data from Wynncraft API and Artemis Repository."""
    client = httpx.AsyncClient(proxy=http_proxy or https_proxy or all_proxy)

    # Fetch the file only if was not updated within 24 hours.
    tasks = []
    if (not ITEMDB_PATH.exists() or time.time() - os.path.getmtime(ITEMDB_PATH) > 86400) and itemdb_should_update:
        tasks += [fetch_item_db(client)]
    if (
        not SHINY_TABLE_PATH.exists() or time.time() - os.path.getmtime(SHINY_TABLE_PATH) > 86400
    ) and shiny_table_should_update:
        tasks += [fetch_shiny_table(client)]
    if (not ID_TABLE_PATH.exists() or time.time() - os.path.getmtime(ID_TABLE_PATH) > 86400) and id_table_should_update:
        tasks += [fetch_id_table(client)]
    await asyncio.gather(*tasks)

    await client.aclose()


async def fetch_item_db(client: httpx.AsyncClient):
    data = await client.get(ITEMDB_FULL_URL)
    with open(DATA_LOCATION / "itemdb.json", "w", encoding="utf-8") as f:
        json.dump(data.json(), f, ensure_ascii=False)


async def fetch_shiny_table(client: httpx.AsyncClient):
    data = await client.get(SHINY_TABLE_URL)
    with open(DATA_LOCATION / "shiny_stats.json", "w", encoding="utf-8") as f:
        json.dump(data.json(), f, ensure_ascii=False)


async def fetch_id_table(client: httpx.AsyncClient):
    data = await client.get(ID_TABLE_URL)
    with open(DATA_LOCATION / "id_keys.json", "w", encoding="utf-8") as f:
        json.dump(data.json(), f, ensure_ascii=False)
