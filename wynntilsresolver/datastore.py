"""Singleton data store with throttled hot reload.

Hot-path getters do a single monotonic-clock compare and return the cached
reference; file stat + JSON reload only fire when the throttle window expires.
`bootstrap()` fetches api-sourced resources that are missing or >24h old.
Env-sourced resources (paths provided via *_PATH env vars) are never fetched
remotely; they rely solely on mtime-based reload.
"""

import asyncio
import json
import os
import pathlib
import time
from typing import Dict, List, Literal, Optional, Tuple

import httpx

from .utils import run_async

if os.name == "nt":
    _DEFAULT_DATA_LOCATION = pathlib.Path.home() / "AppData" / "Local" / "wynntilsresolver"
else:
    _DEFAULT_DATA_LOCATION = pathlib.Path.home() / ".local" / "share" / "wynntilsresolver"

ITEMDB_FULL_URL = "https://api.wynncraft.com/v3/item/database?fullResult"
SHINY_TABLE_URL = "https://raw.githubusercontent.com/Wynntils/Static-Storage/main/Data-Storage/shiny_stats.json"
ID_TABLE_URL = "https://raw.githubusercontent.com/Wynntils/Static-Storage/main/Reference/id_keys.json"

Source = Literal["env", "api"]

_RESOURCE_NAMES: Tuple[str, str, str] = ("itemdb", "shiny", "id")


class DataStore:
    _instance: Optional["DataStore"] = None

    def __new__(cls, *args, **kwargs) -> "DataStore":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, check_interval: float = 60.0) -> None:
        if getattr(self, "_initialized", False):
            return
        self._initialized = True

        env_location = os.environ.get("DATA_LOCATION")
        self.data_location = pathlib.Path(env_location) if env_location else _DEFAULT_DATA_LOCATION
        self.data_location.mkdir(parents=True, exist_ok=True)

        env_itemdb = os.environ.get("ITEMDB_PATH")
        env_shiny = os.environ.get("SHINY_TABLE_PATH")
        env_id = os.environ.get("ID_TABLE_PATH")

        self.itemdb_path = pathlib.Path(env_itemdb) if env_itemdb else self.data_location / "itemdb.json"
        self.shiny_table_path = pathlib.Path(env_shiny) if env_shiny else self.data_location / "shiny_stats.json"
        self.id_table_path = pathlib.Path(env_id) if env_id else self.data_location / "id_keys.json"

        self._paths: Dict[str, pathlib.Path] = {
            "itemdb": self.itemdb_path,
            "shiny": self.shiny_table_path,
            "id": self.id_table_path,
        }
        self._sources: Dict[str, Source] = {
            "itemdb": "env" if env_itemdb else "api",
            "shiny": "env" if env_shiny else "api",
            "id": "env" if env_id else "api",
        }

        self.check_interval = check_interval

        self._cache: Dict[str, object] = dict.fromkeys(_RESOURCE_NAMES, object())
        self._mtime: Dict[str, float] = dict.fromkeys(_RESOURCE_NAMES, 0.0)
        self._last_check: Dict[str, float] = dict.fromkeys(_RESOURCE_NAMES, 0.0)
        self._id_table_reverse: Dict[int, str] = {}

        self._proxy = (
            os.environ.get("http_proxy")
            or os.environ.get("HTTP_PROXY")
            or os.environ.get("https_proxy")
            or os.environ.get("HTTPS_PROXY")
            or os.environ.get("all_proxy")
            or os.environ.get("ALL_PROXY")
        )

    def _get(self, name: str):
        cache = self._cache[name]
        now = time.monotonic()
        if cache is not None and now - self._last_check[name] < self.check_interval:
            return cache

        self._last_check[name] = now
        path = self._paths[name]
        mtime = os.path.getmtime(path)
        if cache is not None and mtime == self._mtime[name]:
            return cache

        with open(path, encoding="utf-8") as f:
            loaded = json.load(f)
        if name == "itemdb":
            loaded = {item["internalName"]: item for item in loaded}
        self._cache[name] = loaded
        self._mtime[name] = mtime
        if name == "id":
            self._id_table_reverse = {v: k for k, v in loaded.items()}
        return loaded

    @property
    def itemdb(self) -> Dict:
        return self._get("itemdb")  # type: ignore[return-value]

    @property
    def shiny_table(self) -> List[Dict]:
        return self._get("shiny")  # type: ignore[return-value]

    @property
    def id_table(self) -> Dict[str, int]:
        return self._get("id")  # type: ignore[return-value]

    def id_from_str(self, key: str) -> int:
        return self.id_table[key]

    def id_from_int(self, value: int) -> str:
        # Touch id_table to ensure reverse map is populated/current.
        _ = self.id_table
        return self._id_table_reverse[value]

    async def _fetch(self, client: httpx.AsyncClient, url: str, path: pathlib.Path) -> None:
        resp = await client.get(url)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(resp.json(), f, ensure_ascii=False)

    def _is_stale(self, path: pathlib.Path) -> bool:
        return not path.exists() or time.time() - os.path.getmtime(path) > 86400

    @run_async
    async def bootstrap(self) -> None:
        """Refresh api-sourced resources if missing or older than 24h."""
        urls = {"itemdb": ITEMDB_FULL_URL, "shiny": SHINY_TABLE_URL, "id": ID_TABLE_URL}
        async with httpx.AsyncClient(proxy=self._proxy) as client:
            tasks = [
                self._fetch(client, urls[name], self._paths[name])
                for name in _RESOURCE_NAMES
                if self._sources[name] == "api" and self._is_stale(self._paths[name])
            ]
            if tasks:
                await asyncio.gather(*tasks)


data_store = DataStore()

# Backward-compat aliases.
DATA_LOCATION = data_store.data_location
ITEMDB_PATH = data_store.itemdb_path
SHINY_TABLE_PATH = data_store.shiny_table_path
ID_TABLE_PATH = data_store.id_table_path
