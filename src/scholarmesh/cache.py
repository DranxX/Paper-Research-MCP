# cache.py — SQLite WAL TTL cache untuk hasil search (absorb pattern dari
# youtube-research-mcp; memperbaiki bug cache-key mereka: key = FULL sorted args,
# jadi params seperti languages/limit tidak pernah diabaikan saat cache hit).
# Fail-open: error cache tidak pernah menggagalkan fetch live — cache hanyalah
# optimasi, primary path selalu jalan.

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import time
from pathlib import Path

TTL_SEARCH = 2 * 3600  # 2 jam, sejalan dengan TTL search di referensi


def enabled() -> bool:
    return os.getenv("SCHOLARMESH_CACHE", "on") != "off"


def _db_path() -> Path:
    path = Path(os.getenv("SCHOLARMESH_CACHE_DB") or (Path.home() / ".cache" / "scholarmesh" / "cache.db"))
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def key(tool: str, args: dict) -> str:
    # full sorted args → param apa pun ikut: tanpa ini, cache hit mengabaikan params
    # (bug yang ada di youtube-research-mcp: key transcript = video_id saja).
    raw = json.dumps({"tool": tool, "args": args}, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode()).hexdigest()


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(_db_path(), timeout=10)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(
        "CREATE TABLE IF NOT EXISTS cache ("
        "k TEXT PRIMARY KEY, v TEXT NOT NULL, expires REAL NOT NULL)"
    )
    return conn


def get(tool: str, args: dict) -> dict | None:
    if not enabled():
        return None
    k = key(tool, args)
    try:
        with _connect() as conn:
            row = conn.execute("SELECT v, expires FROM cache WHERE k = ?", (k,)).fetchone()
        if not row:
            return None
        if row[1] < time.time():
            with _connect() as conn:
                conn.execute("DELETE FROM cache WHERE k = ?", (k,))
            return None
        result = json.loads(row[0])
        result["meta"]["cache"] = {"hit": True, "key": k[:12], "ttl_remaining_s": int(row[1] - time.time())}
        return result
    except Exception as e:  # noqa: BLE001 — cache gagal = lanjut live, jangan gagalkan fetch
        import logging
        logging.getLogger("scholarmesh.cache").warning("cache get gagal (fail-open): %s", e)
        return None


def put(tool: str, args: dict, result: dict, ttl: int = TTL_SEARCH) -> bool:
    if not enabled() or result.get("status") != "ok":
        return False
    k = key(tool, args)
    try:
        with _connect() as conn:
            conn.execute(
                "INSERT INTO cache (k, v, expires) VALUES (?, ?, ?) "
                "ON CONFLICT(k) DO UPDATE SET v = excluded.v, expires = excluded.expires",
                (k, json.dumps(result, ensure_ascii=False), time.time() + ttl),
            )
        return True
    except Exception:  # noqa: BLE001 — sama: fail-open
        return False
