# federation.py — federated research retrieval layer (Reference.md §6):
# pencarian lintas connector, hasil terstandardisasi, dedup DOI → title, provenance per item.
# v2: multi-keyword (queries[]) dijalankan PARALLEL dengan worker pool, year filter
# di-pass ke tiap connector (native bila didukung + post-filter universal di registry).

from __future__ import annotations

import asyncio

from .registry import SOURCES, call_tool

DEFAULT_SOURCES = [c["id"] for c in SOURCES if c["category"] != "key"]


def _norm_doi(doi):
    if not doi:
        return None
    return str(doi).strip().lower().removeprefix("https://doi.org/").removeprefix("http://doi.org/")


def _norm_title(t) -> str:
    import re
    return re.sub(r"[^a-z0-9]+", "", str(t or "").lower())[:160]


async def _run_job(query: str, source_id: str, limit_per: int, year_args: dict, timeout_ms: int) -> dict:
    c = next((x for x in SOURCES if x["id"] == source_id), None)
    if not c:
        return {"query": query, "source": source_id, "status": "error", "count": 0, "items": [], "meta": {"detail": "connector tidak dikenal"}}
    # Hanya tool yang skemanya memang berbasis query (skip unpaywall/orcid/cstr/openreview_notes).
    primary = next((t for t in c["tools"] if "query" in (t["input_schema"].get("required") or [])), None)
    if not primary:
        return {"query": query, "source": source_id, "status": "skipped", "count": 0, "items": [],
                "meta": {"detail": f"bukan pencarian keyword (pakai {c['tools'][0]['name']} langsung)"}}
    try:
        result = await asyncio.wait_for(
            call_tool(primary["name"], {"query": query, "limit": limit_per, **year_args}),
            timeout=timeout_ms / 1000,
        )
        # Envelope dari call_tool (auth-required/blocked/error) tidak selalu punya "query" —
        # tambahkan agar coverage/provenance tidak KeyError.
        if isinstance(result, dict):
            result["query"] = query
        return result
    except asyncio.TimeoutError:
        return {"query": query, "source": source_id, "status": "blocked", "count": 0, "items": [],
                "meta": {"detail": f"federation timeout {timeout_ms}ms"}}
    except Exception as e:  # noqa: BLE001
        return {"query": query, "source": source_id, "status": "error", "count": 0, "items": [], "meta": {"detail": str(e)}}


async def search_papers(args: dict) -> dict:
    """Backward compat: `query` tunggal; baru: `queries[]` — tiap keyword dijalankan parallel
    di semua sumber terpilih, worker pool 8, dedup DOI → title, provenance lengkap."""
    queries = (args.get("queries") if isinstance(args.get("queries"), list) and args["queries"] else [args.get("query")])
    queries = [str(q).strip() for q in queries if str(q).strip()]
    if not queries:
        return {"status": "error", "count": 0, "items": [], "meta": {"detail": "wajib `query` (string) atau `queries` (array of string)"}}

    limit_per = min(args.get("limit_per_source", 4), 10)
    include_bot_wall = args.get("include_bot_wall", True)
    if isinstance(args.get("sources"), list) and args["sources"]:
        requested = args["sources"]
    elif include_bot_wall:
        requested = DEFAULT_SOURCES
    else:
        requested = [c["id"] for c in SOURCES if c["id"] in DEFAULT_SOURCES and c["category"] == "free"]

    year_args = {}
    if args.get("year_from"):
        year_args["year_from"] = args["year_from"]
    if args.get("year_to"):
        year_args["year_to"] = args["year_to"]
    year_note = ({"year_from": args.get("year_from"), "year_to": args.get("year_to")}
                 if (args.get("year_from") or args.get("year_to")) else None)

    timeout_ms = args.get("timeout_ms", 30000)

    # Job matrix: queries × sources, worker pool 8.
    sem = asyncio.Semaphore(8)
    jobs = [(q, sid) for q in queries for sid in requested]

    async def worker(job):
        async with sem:
            return await _run_job(job[0], job[1], limit_per, year_args, timeout_ms)

    results = await asyncio.gather(*(worker(job) for job in jobs))

    used = [{"query": r["query"], "source": r["source"], "status": r["status"], "count": r["count"],
             "detail": (r.get("meta") or {}).get("detail")} for r in results]
    skipped = [{"query": u["query"], "source": u["source"], "detail": u["detail"]} for u in used if u["status"] == "skipped"]

    coverage = [{
        "query": q,
        "total": sum(u["count"] for u in used if u["query"] == q),
        "sources": [{"source": u["source"], "status": u["status"], "count": u["count"]}
                    for u in used if u["query"] == q],
    } for q in queries]

    by_key: dict[str, dict] = {}
    for r in results:
        for item in r.get("items") or []:
            k = _norm_doi(item.get("doi")) or "t:" + _norm_title(item.get("title"))
            if not k or k == "t:":
                continue
            existing = by_key.get(k)
            if not existing:
                by_key[k] = {**item, "alsoIn": [item["source"]], "matchedQueries": [r["query"]]}
            else:
                if item["source"] not in existing["alsoIn"]:
                    existing["alsoIn"].append(item["source"])
                if r["query"] not in existing["matchedQueries"]:
                    existing["matchedQueries"].append(r["query"])
                if not existing.get("abstract") and item.get("abstract"):
                    existing["abstract"] = item["abstract"]
                if not existing.get("pdf") and item.get("pdf"):
                    existing["pdf"] = item["pdf"]
                if not existing.get("year") and item.get("year"):
                    existing["year"] = item["year"]
    merged = list(by_key.values())

    # Brief aggregate (absorb youtube-research-mcp): ringkasan kesehatan run dalam satu objek.
    hist: dict[str, int] = {}
    for u in used:
        hist[u["status"]] = hist.get(u["status"], 0) + 1
    years = [i["year"] for i in merged if isinstance(i.get("year"), int)]
    brief = {
        "sources_used": len(used),
        "status_histogram": hist,
        "unique_results": len(merged),
        "year_range": [min(years), max(years)] if years else None,
        "abstract_chars": sum(len(i.get("abstract") or "") for i in merged),
    }

    return {
        "status": "ok" if merged else ("empty" if any(u["status"] == "ok" for u in used) else "all-failed"),
        "queries": queries,
        "year": year_note,
        "count": len(merged),
        "items": merged[: args.get("max_results", 30)],
        "coverage": coverage,
        "skipped": skipped,
        "brief": brief,
        "meta": {
            "dedup": "doi lalu title-normalized; satu paper bisa match >1 keyword (matchedQueries)",
            "default_note": "Default: semua sumber tanpa API key (free + bot-wall), 8 request paralel. "
                            "Key-gated (scopus/lens/ads/alphaxiv/dimensions/wos/aminer/baidu/cstr/core) via sources[] + env.",
        },
    }
