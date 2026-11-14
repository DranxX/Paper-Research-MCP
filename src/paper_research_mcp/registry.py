# registry.py — agregasi semua connector + auth-gating + universal year filter.

from __future__ import annotations

import os

from .core import year_filter
from .sources import china, free, indonesia, premium

CONNECTORS: list[dict] = [
    free.CONNECTOR,
    china.CONNECTOR,
    indonesia.CONNECTOR,
    premium.CONNECTOR,
]


def connector_status(c: dict) -> dict:
    env = c.get("auth_env")
    return {
        "id": c["id"],
        "label": c["label"],
        "category": c["category"],
        "homepage": c.get("homepage"),
        "auth": "required" if c.get("auth_required") else ("optional" if env else "none"),
        "auth_env": env,
        "env_present": bool(os.getenv(env)) if env else None,
        "note": c.get("note"),
        "tools": [t["name"] for t in c["tools"]],
    }


def list_sources(category: str | None = None) -> dict:
    connectors = [c for c in CONNECTORS if not category or c["category"] == category]
    return {"sources": [connector_status(c) for c in connectors]}


def all_tools() -> list[dict]:
    out = []
    for c in CONNECTORS:
        out.extend(c["tools"])
    return out


async def call_tool(name: str, args: dict | None = None) -> dict:
    args = args or {}
    for c in CONNECTORS:
        tool = next((x for x in c["tools"] if x["name"] == name), None)
        if not tool:
            continue
        if c.get("auth_required") and c.get("auth_env") and not os.getenv(c["auth_env"]):
            return {"status": "auth-required", "source": c["id"], "count": 0, "items": [],
                    "meta": {"env": c["auth_env"],
                             "detail": f"{c['label']} wajib {c['auth_env']} (lihat README / .env.example). {c.get('note', '')}"}
                    }
        result = await tool["handler"](args)
        # Universal year filter — jaminan untuk semua tool meski API-nya tak dukung filter tanggal.
        if args.get("year_from") or args.get("year_to"):
            items, dropped = year_filter(result.get("items") or [], args.get("year_from"), args.get("year_to"))
            result["items"] = items
            result["count"] = len(items)
            result["meta"] = {**(result.get("meta") or {}),
                              "year_filter": {"from": args.get("year_from"), "to": args.get("year_to"),
                                              "dropped_unknown_or_out_of_range": dropped}}
        return result
    raise LookupError(f"Tool tidak ditemukan: {name}")
