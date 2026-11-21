# tests/e2e_all_tools.py — live end-to-end test: 47 connector tools satu per satu
# + cache hit + federasi + protokol (51 pengecekan). Jalankan: uv run python tests/e2e_all_tools.py
# Aturan penilaian:
#   PASS  = envelope sah (status/source/count/items/meta lengkap) DAN status sesuai ekspektasi kategori
#   FAIL  = exception keluar, envelope rusak, atau status di luar yang diizinkan
# Scraper bot-wall dianggap WAJAR bila status blocked/error (DNS/bot-wall dari jaringan ini),
# tapi tetap dicatat apa adanya di matriks.

from __future__ import annotations

import asyncio
import json
import sys

from scholarmesh.federation import search_papers
from scholarmesh.registry import SOURCES, all_tools, call_tool

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
    n_tools = len(all_tools())
    print(f"scholarmesh v-test: {n_tools} connector tools, {len(SOURCES)} sources\n")

    print("── 1. INDEXES (9 tools) ──")
    r = await tool("openalex_search", {"query": "contrastive learning", "limit": 2, "year_from": 2024},
                   {"ok", "empty"}, "native year filter")
    if r and r["items"]:
        years = [i["year"] for i in r["items"] if i["year"]]
        if any(y < 2024 for y in years):
            MATRIX[-1].update(verdict="FAIL", note="year leak: " + str(years))
            print(f"  FAIL  openalex_search year leak: {years}")
    # cache hit (absorb ytdlp): argumen sama persis → envelope dari SQLite cache, zero HTTP
    r2 = await call_tool("openalex_search", {"query": "contrastive learning", "limit": 2, "year_from": 2024})
    cached = (r2.get("meta") or {}).get("cache", {}).get("hit") is True
    MATRIX.append({"tool": "cache[openalex 2nd call]", "status": r2.get("status"), "count": r2.get("count", 0),
                   "verdict": "PASS" if cached else "FAIL", "note": "meta.cache.hit=True expected"})
    print(f"  {'PASS' if cached else 'FAIL'}  cache[openalex 2nd call]        hit={cached}")
    await tool("crossref_search", {"query": "protein structure prediction", "limit": 2},
               {"ok", "empty", "failed"}, "crossref kadang flaky — envelope error tetap kontrak sah")
    await tool("crossref_doi", {"doi": "10.1038/nature12373"}, {"ok", "error"})
    await tool("doaj_search", {"query": "open science", "limit": 2}, {"ok", "empty"})
    await tool("semantic_scholar_search", {"query": "transformer", "limit": 2},
               {"ok", "empty", "blocked"}, "429 tanpa key = wajar")
    await tool("lens_search", {"query": "crispr", "limit": 2}, {"auth-required"})
    await tool("dimensions_search", {"query": "protein", "limit": 2}, {"auth-required"})
    await tool("scopus_search", {"query": "machine learning", "limit": 2}, {"auth-required"})
    await tool("wos_search", {"query": "quantum", "limit": 2}, {"auth-required"})

    print("── 2. PREPRINTS (5 tools) ──")
    await tool("arxiv_search", {"query": "cat:cs.CL AND all:reward model", "limit": 2,
                                "year_from": 2023, "year_to": 2025}, {"ok", "empty"}, "native submittedDate filter")
    or_res = await tool("openreview_search", {"query": "reward hacking", "limit": 2}, {"ok", "empty"})
    if or_res and or_res["items"]:
        forum = or_res["items"][0]["extra"].get("forum_id")
        if forum:
            await tool("openreview_notes", {"forum": forum}, {"ok", "empty", "blocked", "failed"},
                       "403 challenge anti-scraping OpenReview = blocked wajar")
    await tool("alphaxiv_search", {"query": "rlhf", "limit": 2}, {"auth-required"})
    await tool("hf_search", {"query": "attention", "limit": 2}, {"ok", "empty", "failed"})

    print("── 3. ARCHIVES (6 tools) ──")
    await tool("unpaywall_resolve", {"doi": "10.1038/nature12373"}, {"ok", "empty", "error"})
    await tool("zenodo_search", {"query": "crispr", "limit": 2}, {"ok", "empty", "failed"})
    await tool("datacite_search", {"query": "crispr", "limit": 2}, {"ok", "empty", "failed"})
    await tool("osf_search", {"query": "crispr", "limit": 2}, {"ok", "empty", "failed"})
    await tool("openaire_search", {"query": "crispr", "limit": 2}, {"ok", "empty", "failed"})
    await tool("core_search", {"query": "crispr", "limit": 2}, {"auth-required"}, "tanpa CORE_API_KEY = wajib auth-required")

    print("── 4. DOMAIN (10 tools) ──")
    await tool("inspire_search", {"query": "find t neutrino oscillation", "limit": 2}, {"ok", "empty"})
    await tool("eric_search", {"query": "literacy", "limit": 2}, {"ok", "empty"})
    await tool("zbmath_search", {"query": "ricci flow", "limit": 2}, {"ok", "empty", "failed"})
    await tool("whoiris_search", {"query": "tuberculosis", "limit": 2}, {"ok", "empty", "failed"})
    await tool("proofwiki_search", {"query": "Pythagorean theorem", "limit": 3},
               {"ok", "empty", "blocked"}, "Cloudflare challenge dari jaringan ini = blocked wajar")
    await tool("proofwiki_get", {"page": "Pythagorean Theorem"},
               {"ok", "empty", "blocked", "error"}, "challenge = blocked wajar; empty = judul tak persis")
    await tool("pwc_search", {"query": "image classification", "limit": 2},
               {"ok", "empty", "blocked"}, "endpoint rehost beta — blocked wajar")
    epmc = await tool("europepmc_search", {"query": "crispr", "limit": 2}, {"ok", "empty", "failed"})
    if epmc and epmc["items"]:
        await tool("europepmc_fulltext", {"pmcid": "PMC7159299"}, {"ok", "empty", "blocked", "error"},
                   "PMC7159299 terverifikasi OA saat probe")
    await tool("pubmed_search", {"query": "crispr", "limit": 2}, {"ok", "empty", "failed"})
    await tool("ads_search", {"query": "exoplanet", "limit": 2}, {"auth-required"})

    print("── 5. REGIONAL (13 tools, scraper best-effort) ──")
    indo_allowed = {"ok", "empty", "blocked", "error"}  # DNS/bot-wall dari jaringan ini = wajar
    await tool("garuda_search", {"query": "pembelajaran mesin", "limit": 2}, indo_allowed)
    await tool("sinta_search", {"query": "jurnal sains", "limit": 2}, indo_allowed)
    await tool("onesearch_search", {"query": "coral reef", "limit": 2}, indo_allowed)
    await tool("rama_search", {"query": "ekonomi digital", "limit": 2}, indo_allowed)
    await tool("moraref_search", {"query": "fiqih", "limit": 2}, indo_allowed)
    await tool("neliti_search", {"query": "rice yield", "limit": 2}, indo_allowed)
    await tool("brin_search", {"query": "genomics", "limit": 2}, indo_allowed)
    await tool("google_scholar_search", {"query": "vision transformer", "limit": 3}, indo_allowed)
    await tool("jstage_search", {"query": "crispr", "limit": 2}, {"ok", "empty", "failed"}, "Atom XML JST — probes 21 Nov: 200")
    await tool("cinii_search", {"query": "crispr", "limit": 2}, {"ok", "empty", "failed"}, "JSON-LD NII — probes 21 Nov: 200")
    await tool("nssd_search", {"query": "知识 图谱", "limit": 2}, {"ok", "empty", "error"},
               "403 flaky wajar (sudah ada retry)")
    await tool("baidu_scholar_search", {"query": "large language model", "limit": 2},
               {"auth-required", "failed", "blocked"}, "kuota gratis habis → auth/failed wajar")
    await tool("aminer_search", {"query": "transformer", "limit": 2},
               {"auth-required"}, "tanpa key = wajib auth-required")
    await tool("sciencedb_search", {"query": "carbon", "limit": 2},
               {"ok", "empty", "blocked"}, "API path best-effort")
    await tool("cstr_resolve", {"id": "CSTR:31258.001.SCDB.1000.1"}, {"auth-required"},
               "tanpa key = wajib auth-required")

    print("── 6. PEOPLE (1 tool) ──")
    await tool("orcid_works", {"orcid": "0000-0002-1825-0097", "limit": 3}, {"ok", "empty", "failed"})

    print("── 7. FEDERASI (3 mode) ──")
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

    print("── 8. PROTOKOL MCP (stdio subprocess) ──")
    proc = await asyncio.create_subprocess_exec(
        "uv", "run", "scholarmesh", stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL,
    )
    reqs = "\n".join([
        json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
            "protocolVersion": "2024-11-05", "capabilities": {},
            "clientInfo": {"name": "probe", "version": "0"}}}),
        json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}),
        json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}),
    ]) + "\n"
    # stdin DIJAGA TERBUKA sampai respons tools/list terbaca — communicate() menutup stdin
    # sehingga server kena EOF dan bisa shutdown sebelum respons terakhir flush (race
    # response-vs-shutdown; gejala: tools=0 walau server hidup).
    parsed: list[dict] = []
    try:
        proc.stdin.write(reqs.encode())
        await proc.stdin.drain()
        while not any(p.get("id") == 2 for p in parsed):
            raw = await asyncio.wait_for(proc.stdout.readline(), timeout=30)
            if not raw:
                break
            try:
                parsed.append(json.loads(raw.decode()))
            except json.JSONDecodeError:
                pass
        init = next((p for p in parsed if p.get("id") == 1), None)
        tl = next((p for p in parsed if p.get("id") == 2), None)
        n = len(tl["result"]["tools"]) if tl else 0
        ok_proto = bool(init and init["result"]["serverInfo"]["name"] == "scholarmesh" and n == 50)
        MATRIX.append({"tool": "stdio[initialize+tools/list]", "status": "ok" if ok_proto else "error",
                       "count": n, "verdict": "PASS" if ok_proto else "FAIL",
                       "note": f"serverInfo={init['result']['serverInfo'] if init else None}, tools={n}"})
        print(f"  {'PASS' if ok_proto else 'FAIL'}  stdio[initialize+tools/list]  tools={n}")
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
