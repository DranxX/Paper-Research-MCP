# registry.py — agregasi FLAT semua source connector (satu dict per sumber, bukan per pak)
# + auth-gating + universal year filter. Negara/disiplin = metadata per sumber;
# federation & list_sources bisa filter per kategori akses / disiplin / negara.

from __future__ import annotations

import os

from .core import year_filter
from .sources import archives, domain, indexes, people, preprints, regional

SOURCES: list[dict] = [
    *indexes.SOURCES,
    *preprints.SOURCES,
    *archives.SOURCES,
    *domain.SOURCES,
    *regional.SOURCES,
    *people.SOURCES,
]


def source_status(c: dict) -> dict:
    env = c.get("auth_env")
    return {
        "id": c["id"],
        "label": c["label"],
        "category": c["category"],
        "auth": "required" if c.get("auth_required") else ("optional" if env else "none"),
        "auth_env": env,
        "env_present": bool(os.getenv(env)) if env else None,
        "disciplines": c.get("disciplines"),
        "countries": c.get("countries"),
        "homepage": c.get("homepage"),
        "note": c.get("note"),
        "tools": [t["name"] for t in c["tools"]],
    }


def list_sources(category: str | None = None) -> dict:
    sources = [c for c in SOURCES if not category or c["category"] == category]
    return {"sources": [source_status(c) for c in sources]}


def all_tools() -> list[dict]:
    out = []
    for c in SOURCES:
        out.extend(c["tools"])
    return out


async def call_tool(name: str, args: dict | None = None) -> dict:
    args = args or {}
    for c in SOURCES:
        tool = next((x for x in c["tools"] if x["name"] == name), None)
        if not tool:
            continue
        # Auth-gating: hanya source yang MENDEKLARASIKAN gate keras (auth_required=True
        # + satu env). Source dengan gate multi-env/behavioral (cstr, baidu) self-gate
        # di handler masing-masing.
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
