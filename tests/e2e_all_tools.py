# tests/e2e_all_tools.py — live end-to-end test: 34 tools satu per satu + federasi + protokol.
# Jalankan: uv run python tests/e2e_all_tools.py
# Aturan penilaian:
#   PASS  = envelope sah (status/source/count/items/meta lengkap) DAN status sesuai ekspektasi kategori
#   FAIL  = exception keluar, envelope rusak, atau status di luar yang diizinkan
# Scraper bot-wall dianggap WAJAR bila status blocked/error (DNS/bot-wall dari jaringan ini),
# tapi tetap dicatat apa adanya di matriks.

from __future__ import annotations

import asyncio
import json
import sys

from paper_research_mcp.federation import search_papers
from paper_research_mcp.registry import CONNECTORS, call_tool

REQUIRED_ENV_KEYS = {"status", "source", "count", "items", "meta"}
REQUIRED_ITEM_KEYS = {"title", "authors", "year", "doi", "venue", "abstract", "url", "pdf", "source", "extra"}

MATRIX: list[dict] = []


def validate(name: str, result: dict, allowed: set[str], note: str = "") -> bool:
    problems = []
    if not REQUIRED_ENV_KEYS.issubset(result.keys()):
        problems.append(f"envelope keys kurang: {REQUIRED_ENV_KEYS - set(result.keys())}")
    if result.get("status") not in allowed:
        problems.append(f"status '{result.get('status')}' di luar yang diizinkan {sorted(allowed)}")
    if result.get("count") != len(result.get("items") or []):
        problems.append("count != len(items)")
    for i, item in enumerate((result.get("items") or [])[:5]):
        missing = REQUIRED_ITEM_KEYS - set(item.keys())
        if missing:
            problems.append(f"items[{i}] keys kurang: {missing}")
    status = result.get("status")
    ok_flag = not problems
    MATRIX.append({"tool": name, "status": status, "count": result.get("count", 0),
                   "verdict": "PASS" if ok_flag else "FAIL", "note": note or "; ".join(problems)})
    print(f"  {'PASS' if ok_flag else 'FAIL'}  {name:<28} status={status:<14} count={result.get('count', 0)}  {note}")
    return ok_flag


async def tool(name: str, args: dict, allowed: set[str], note: str = "") -> dict | None:
    try:
        result = await call_tool(name, args)
    except Exception as e:  # noqa: BLE001
        MATRIX.append({"tool": name, "status": "exception", "count": 0, "verdict": "FAIL",
                       "note": f"exception keluar: {e}"})
        print(f"  FAIL  {name:<28} exception: {e}")
        return None
    validate(name, result, allowed, note)
    return result


async def main() -> None:
    print("── 1. FREE connectors (12 tools) ──")
    r = await tool("openalex_search", {"query": "contrastive learning", "limit": 2, "year_from": 2024},
                   {"ok", "empty"}, "native year filter")
    if r and r["items"]:
        years = [i["year"] for i in r["items"] if i["year"]]
        if any(y < 2024 for y in years):
            MATRIX[-1].update(verdict="FAIL", note="year leak: " + str(years))
            print(f"  FAIL  openalex_search year leak: {years}")
    await tool("crossref_search", {"query": "protein structure prediction", "limit": 2}, {"ok", "empty"})
    await tool("crossref_doi", {"doi": "10.1038/nature12373"}, {"ok", "error"})
    await tool("arxiv_search", {"query": "cat:cs.CL AND all:reward model", "limit": 2,
                                "year_from": 2023, "year_to": 2025}, {"ok", "empty"}, "native submittedDate filter")
    await tool("doaj_search", {"query": "open science", "limit": 2}, {"ok", "empty"})
    await tool("semantic_scholar_search", {"query": "transformer", "limit": 2},
               {"ok", "empty", "blocked"}, "429 tanpa key = wajar")
    or_res = await tool("openreview_search", {"query": "reward hacking", "limit": 2}, {"ok", "empty"})
    if or_res and or_res["items"]:
        forum = or_res["items"][0]["extra"].get("forum_id")
        if forum:
            await tool("openreview_notes", {"forum": forum}, {"ok", "empty", "blocked", "failed"},
                       "403 challenge anti-scraping OpenReview = blocked wajar")
    await tool("inspire_search", {"query": "find t neutrino oscillation", "limit": 2}, {"ok", "empty"})
    await tool("eric_search", {"query": "literacy", "limit": 2}, {"ok", "empty"})
    await tool("unpaywall_resolve", {"doi": "10.1038/nature12373"}, {"ok", "empty", "error"})
    await tool("orcid_works", {"orcid": "0000-0002-1825-0097", "limit": 3}, {"ok", "empty", "failed"})
    await tool("pwc_search", {"query": "image classification", "limit": 2},
               {"ok", "empty", "blocked"}, "endpoint rehost beta — blocked wajar")

    print("── 2. CHINA (5 tools) ──")
    await tool("nssd_search", {"query": "知识 图谱", "limit": 2}, {"ok", "empty", "error"},
               "403 flaky wajar (sudah ada retry)")
    await tool("baidu_scholar_search", {"query": "large language model", "limit": 2},
               {"ok", "empty", "auth-required", "failed"})
    await tool("aminer_search", {"query": "transformer", "limit": 2},
               {"auth-required"}, "tanpa key = wajib auth-required")
    await tool("sciencedb_search", {"query": "carbon", "limit": 2},
               {"ok", "empty", "blocked"}, "API path best-effort")
    await tool("cstr_resolve", {"id": "CSTR:31258.001.SCDB.1000.1"}, {"auth-required"},
               "tanpa key = wajib auth-required")

    print("── 3. INDONESIA (8 tools, scraper best-effort) ──")
    indo_allowed = {"ok", "empty", "blocked", "error"}  # DNS/bot-wall dari jaringan ini = wajar
    await tool("garuda_search", {"query": "pembelajaran mesin", "limit": 2}, indo_allowed)
    await tool("sinta_search", {"query": "jurnal sains", "limit": 2}, indo_allowed)
    await tool("onesearch_search", {"query": "coral reef", "limit": 2}, indo_allowed)
    await tool("rama_search", {"query": "ekonomi digital", "limit": 2}, indo_allowed)
    await tool("moraref_search", {"query": "fiqih", "limit": 2}, indo_allowed)
    await tool("neliti_search", {"query": "rice yield", "limit": 2}, indo_allowed)
    await tool("brin_search", {"query": "genomics", "limit": 2}, indo_allowed)
    await tool("google_scholar_search", {"query": "vision transformer", "limit": 3}, indo_allowed)

    print("── 4. PREMIUM (6 tools, tanpa key = auth-required wajib) ──")
    await tool("ads_search", {"query": "exoplanet", "limit": 2}, {"auth-required"})
    await tool("alphaxiv_search", {"query": "rlhf", "limit": 2}, {"auth-required"})
    await tool("scopus_search", {"query": "machine learning", "limit": 2}, {"auth-required"})
    await tool("lens_search", {"query": "crispr", "limit": 2}, {"auth-required"})
    await tool("dimensions_search", {"query": "protein", "limit": 2}, {"auth-required"})
    await tool("wos_search", {"query": "quantum", "limit": 2}, {"auth-required"})

    print("── 5. FEDERASI (3 mode) ──")
    single = await search_papers({"query": "protein folding", "year_to": 2020,
                                  "limit_per_source": 2, "include_bot_wall": False})
    problems = []
    if single["status"] not in ("ok", "empty"):
        problems.append(f"status {single['status']}")
    leaks = [i for i in single["items"] if i.get("year") and i["year"] > 2020]
    if leaks:
        problems.append(f"year_to=2020 leak: {len(leaks)} item")
    MATRIX.append({"tool": "search_papers[single+year_to]", "status": single["status"],
                   "count": single["count"], "verdict": "PASS" if not problems else "FAIL",
                   "note": "; ".join(problems) or f"dedup={single['count']}, 0 leak"})
    print(f"  {'PASS' if not problems else 'FAIL'}  search_papers[single+year_to]      dedup={single['count']}  {problems}")

    multi = await search_papers({"queries": ["LLM watermarking", "detecting AI-generated text"],
                                 "year_from": 2024, "limit_per_source": 3, "max_results": 12,
                                 "include_bot_wall": False})
    problems = []
    if len(multi.get("coverage", [])) != 2:
        problems.append("coverage != 2 keyword")
    leaks = [i for i in multi["items"] if i.get("year") and i["year"] < 2024]
    if leaks:
        problems.append(f"year_from=2024 leak: {len(leaks)}")
    for i in multi["items"]:
        if not i.get("matchedQueries"):
            problems.append("ada item tanpa matchedQueries")
            break
    MATRIX.append({"tool": "search_papers[multi+year_from]", "status": multi["status"],
                   "count": multi["count"], "verdict": "PASS" if not problems else "FAIL",
                   "note": "; ".join(problems) or f"dedup={multi['count']}, coverage=2, 0 leak"})
    print(f"  {'PASS' if not problems else 'FAIL'}  search_papers[multi+year_from]     dedup={multi['count']}  {problems}")

    botw = await search_papers({"query": "climate", "include_bot_wall": True, "limit_per_source": 2})
    statuses = [u["status"] for u in botw.get("coverage", [{}])[0].get("sources", [])]
    MATRIX.append({"tool": "search_papers[bot-wall on]", "status": botw["status"], "count": botw["count"],
                   "verdict": "PASS" if botw["status"] in ("ok", "empty", "all-failed") else "FAIL",
                   "note": "status sumber: " + json.dumps(statuses)})
    print(f"  PASS  search_papers[bot-wall on]        status={botw['status']}  sources={statuses}")

    print("── 6. PROTOKOL MCP (stdio subprocess) ──")
    proc = await asyncio.create_subprocess_exec(
        "uv", "run", "paper-research-mcp", stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL,
    )
    reqs = "\n".join([
        json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
            "protocolVersion": "2024-11-05", "capabilities": {},
            "clientInfo": {"name": "probe", "version": "0"}}}),
        json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}),
        json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}),
    ]) + "\n"
    try:
        out, _ = await asyncio.wait_for(proc.communicate(reqs.encode()), timeout=30)
        lines = [json.loads(x) for x in out.decode().strip().split("\n") if x.strip()]
        init = next((l for l in lines if l.get("id") == 1), None)
        tl = next((l for l in lines if l.get("id") == 2), None)
        n_tools = len(tl["result"]["tools"]) if tl else 0
        ok_proto = bool(init and init["result"]["serverInfo"]["name"] == "paper-research-mcp" and n_tools == 34)
        MATRIX.append({"tool": "stdio[initialize+tools/list]", "status": "ok" if ok_proto else "error",
                       "count": n_tools, "verdict": "PASS" if ok_proto else "FAIL",
                       "note": f"serverInfo={init['result']['serverInfo'] if init else None}, tools={n_tools}"})
        print(f"  {'PASS' if ok_proto else 'FAIL'}  stdio[initialize+tools/list]  tools={n_tools}")
    except asyncio.TimeoutError:
        MATRIX.append({"tool": "stdio[initialize+tools/list]", "status": "timeout", "count": 0,
                       "verdict": "FAIL", "note": "subprocess timeout 30s"})
        print("  FAIL  stdio[initialize+tools/list] timeout")
    finally:
        try:
            proc.kill()
        except ProcessLookupError:
            pass

    # ── rekap ──
    print("\n════ REKAP ════")
    pass_n = sum(1 for m in MATRIX if m["verdict"] == "PASS")
    fail_n = len(MATRIX) - pass_n
    print(f"total={len(MATRIX)}  PASS={pass_n}  FAIL={fail_n}")
    if fail_n:
        for m in MATRIX:
            if m["verdict"] == "FAIL":
                print(f"  FAIL {m['tool']} — {m['note']}")
    print("--- REPORT_JSON ---")
    print(json.dumps(MATRIX, ensure_ascii=False, indent=2))
    sys.exit(1 if fail_n else 0)


if __name__ == "__main__":
    asyncio.run(main())
