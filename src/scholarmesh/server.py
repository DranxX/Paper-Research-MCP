# server.py — entry point ScholarMesh (stdio transport via MCP SDK, lowlevel Server).
# Console scripts: `scholarmesh` (+ legacy alias `paper-research-mcp`) — lihat [project.scripts] pyproject.

from __future__ import annotations

import asyncio
import json
import logging

import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server

from .federation import search_papers
from .registry import SOURCES, all_tools, call_tool

VERSION = "0.5.5"

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("scholarmesh")


def _search_papers_schema() -> dict:
    return {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Satu kata kunci (mode spesifik) — atau pakai queries[] untuk parallel multi-keyword"},
            "queries": {"type": "array", "items": {"type": "string"}, "maxItems": 8,
                        "description": "Beberapa kata kunci sekaligus — dijalankan PARALLEL di semua sumber terpilih, hasil didedup lintas keyword"},
            "sources": {"type": "array", "items": {"type": "string"},
                        "description": "Opsional — id sumber yang dipakai (lihat list_sources). Default: semua non-key."},
            "year_from": {"type": "integer", "description": "Filter tahun terbit >= (native di openalex/crossref/arxiv/s2 + post-filter universal)"},
            "year_to": {"type": "integer", "description": "Filter tahun terbit <="},
            "limit_per_source": {"type": "integer", "minimum": 1, "maximum": 10, "default": 4},
            "max_results": {"type": "integer", "minimum": 1, "maximum": 50, "default": 30},
            "include_bot_wall": {"type": "boolean", "default": True,
                                 "description": "false = hanya sumber API resmi (skip scraper regional/scholar/proofwiki)"},
            "timeout_ms": {"type": "integer", "default": 30000},
        },
        "additionalProperties": False,
    }


async def _search_papers(args: dict) -> list[types.TextContent]:
    result = await search_papers(args or {})
    return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _list_sources(args: dict) -> list[types.TextContent]:
    category = (args or {}).get("category")
    import os
    sources = []
    for c in SOURCES:
        if category and c["category"] != category:
            continue
        env = c.get("auth_env")
        sources.append({
            "id": c["id"], "label": c["label"], "category": c["category"],
            "auth": "required" if c.get("auth_required") else ("optional" if env else "none"),
            "env": env, "env_set": bool(os.getenv(env)) if env else None,
            "disciplines": c.get("disciplines"), "countries": c.get("countries"),
            "homepage": c.get("homepage"), "note": c.get("note"),
            "tools": [t["name"] for t in c["tools"]],
        })
    result = {"sources": sources}
    return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


server = Server("scholarmesh")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    tools = [
        types.Tool(
            name="search_papers",
            description="Federated search ke banyak sumber paper sekaligus + dedup (DOI → title) + provenance. "
                        "Mode: (1) spesifik — `query` tunggal; (2) parallel multi-keyword — `queries: [\"kata1\",\"kata2\"]` "
                        "dijalankan paralel di semua sumber, satu paper yang match >1 keyword ditandai matchedQueries. "
                        "Bisa dibatasi tanggal via `year_from`/`year_to` (dipass native ke API yang mendukung + post-filter universal). "
                        "Default: semua sumber tanpa API key; key-gated via sources[].",
            inputSchema=_search_papers_schema(),
        ),
        types.Tool(
            name="list_sources",
            description="Daftar semua sumber ScholarMesh: kategori akses (free/bot-wall/key), disiplin & negara, "
                        "env var yang dibutuhkan, status env saat ini, tools per sumber.",
            inputSchema={"type": "object",
                         "properties": {"category": {"type": "string", "enum": ["free", "bot-wall", "key"],
                                                     "description": "Filter opsional per kategori"}},
                         "additionalProperties": False},
        ),
    ]
    for t in all_tools():
        tools.append(types.Tool(name=t["name"], description=t["description"], inputSchema=t["input_schema"]))
    return tools


@server.call_tool()
async def call_tool_handler(name: str, args: dict) -> list[types.TextContent]:
    if name == "search_papers":
        return await _search_papers(args)
    if name == "list_sources":
        return await _list_sources(args)
    try:
        result = await call_tool(name, args)
    except LookupError as e:
        raise ValueError(str(e)) from e
    text = json.dumps(result, ensure_ascii=False, indent=2)
    return [types.TextContent(type="text", text=text)]


async def _serve() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main() -> None:
    """MCP stdio entry point."""
    log.info("scholarmesh v%s: %d tools, %d sources ready (stdio)",
             VERSION, 2 + len(all_tools()), len(SOURCES))
    try:
        asyncio.run(_serve())
    except KeyboardInterrupt:
        log.info("shutdown requested (Ctrl+C) — bye")


if __name__ == "__main__":
    main()
