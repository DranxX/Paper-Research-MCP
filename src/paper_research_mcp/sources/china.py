# china.py — platform akademik China (per Reference.md §China).
# Kategori: nssd = free (no login, "verified live" di Reference.md); sciencedb = free
# (open API, best-effort); baidu_scholar = freemium (50 call/hari); aminer & cstr = key.

from __future__ import annotations

import json
import os

from ..core import (auth_required, blocked, empty, failed, http_get, http_post,
                    json_loose, ok, std)

SEARCH_SCHEMA = {
    "type": "object",
    "properties": {
        "query": {"type": "string", "description": "Kata kunci — Bahasa China memberi hasil terbaik di NSSD; English didukung di Baidu Scholar/AMiner"},
        "limit": {"type": "integer", "minimum": 1, "maximum": 20, "default": 5},
    },
    "required": ["query"],
    "additionalProperties": False,
}


async def _nssd_search(a: dict) -> dict:
    n = min(a.get("limit", 5), 20)
    body = {"search": a["query"], "pageNum": "1", "pageSize": str(n), "sort": ""}
    r = await http_post("https://www.ncpssd.cn/searchHandler/search", body)
    # NCPSSD kadang 403 flaky pada burst — satu retry setelah jeda 1.5s (probes: 200 flaky).
    if r["status"] == 403:
        import asyncio
        await asyncio.sleep(1.5)
        r = await http_post("https://www.ncpssd.cn/searchHandler/search", body)
    j = json_loose(r["body"])
    if not j or "data" not in j:
        return failed("nssd", f"HTTP {r['status']} {r['error'] or r['body'][:120]}")
    rows = (j.get("data") or {}).get("rows") or []
    items = [std(
        title=x.get("title") or x.get("Name"),
        authors=[x.get("creator")] if x.get("creator") else ([x.get("author")] if x.get("author") else []),
        year=int(str(x.get("years"))[:4]) if x.get("years") else None,
        doi=None, venue=x.get("cbw_name"), abstract=x.get("remark"), url=None,
        source="nssd", extra={"issn": x.get("issn"), "keywords": x.get("subject")},
    ) for x in rows]
    items = [i for i in items if i]
    return ok("nssd", items, {"total": (j.get("data") or {}).get("total"),
                              "note": "SSH China — query Bahasa China direkomendasikan"}) if items else empty(
        "nssd", f"0 hasil untuk '{a['query']}' — coba kata kunci Bahasa China (endpoint NSSD terverifikasi hidup)")


async def _baidu_scholar_search(a: dict) -> dict:
    n = min(a.get("limit", 5), 20)
    from urllib.parse import quote
    q = quote(a["query"], safe="")
    headers = {}
    if os.getenv("BAIDU_API_KEY"):
        headers["Authorization"] = f"Bearer {os.environ['BAIDU_API_KEY']}"
    r = await http_get(f"https://qianfan.baidubce.com/v2/tools/baidu_scholar/search?wd={q}&pageNum=1&pageSize={n}", headers=headers)
    j = json_loose(r["body"])
    rows = None
    if isinstance(j, dict):
        data = j.get("data") or {}
        rows = data.get("items") or data.get("results") or j.get("results")
    if not rows:
        if r["status"] in (401, 403):
            return auth_required("baidu_scholar", "BAIDU_API_KEY", f"HTTP {r['status']} — kuota gratis habis / butuh authorization Qianfan")
        return failed("baidu_scholar", f"HTTP {r['status']} {r['body'][:150]}")
    items = [std(
        title=x.get("title"), authors=x.get("authors") or [], year=int(x["year"]) if x.get("year") else None,
        doi=x.get("doi"), venue=x.get("journalName"),
        abstract=x.get("abstract") or (f"AI abstract: {x['ai_abstract']}" if x.get("ai_abstract") else None),
        url=x.get("url"), source="baidu_scholar", extra={"paperId": x.get("paperId")},
    ) for x in rows[:n]]
    items = [i for i in items if i]
    return ok("baidu_scholar", items) if items else empty("baidu_scholar")


async def _aminer_search(a: dict) -> dict:
    if not os.getenv("AMINER_API_KEY"):
        return auth_required("aminer", "AMINER_API_KEY", "Open platform AMiner menolak request tanpa authorization (terverifikasi live).")
    n = min(a.get("limit", 5), 20)
    from urllib.parse import quote
    q = quote(a["query"], safe="")
    r = await http_get(f"https://datacenter.aminer.cn/gateway/open_platform/api/paper/search/pro?query={q}&size={n}",
                       headers={"Authorization": f"Bearer {os.environ['AMINER_API_KEY']}"})
    j = json_loose(r["body"])
    rows = (j or {}).get("data") or ((j or {}).get("result") or {}).get("papers")
    if not rows:
        return failed("aminer", f"HTTP {r['status']} {json.dumps(j)[:150]}")
    papers = rows if isinstance(rows, list) else rows.get("papers") or []
    items = [std(
        title=p.get("title") or p.get("paperTitle"),
        authors=[(x.get("name") if isinstance(x, dict) else x) for x in (p.get("authors") or [])],
        year=int(p["year"]) if p.get("year") else None, doi=p.get("doi"),
        venue=p.get("venue") or p.get("venueName"), abstract=p.get("abstract"),
        url=p.get("url") or (f"https://www.aminer.cn/pub/{p.get('id')}" if p.get("id") else None),
        source="aminer",
    ) for p in papers[:n]]
    items = [i for i in items if i]
    return ok("aminer", items) if items else empty("aminer")


async def _sciencedb_search(a: dict) -> dict:
    n = min(a.get("limit", 5), 20)
    from urllib.parse import quote
    q = quote(a["query"], safe="")
    attempts = [
        ("GET", f"https://www.scidb.cn/api/sdb-query-service/query?keywords={q}&page=1&size={n}", None),
        ("POST", "https://www.scidb.cn/api/sdb-query-service/query", {"keywords": a["query"], "page": 1, "size": n}),
    ]
    for method, url, body in attempts:
        r = await http_get(url) if method == "GET" else await http_post(url, body, form=False)
        j = json_loose(r["body"])
        data = (j or {}).get("data")
        rows = (data.get("records") if isinstance(data, dict) else None) \
            or (data.get("list") if isinstance(data, dict) else None) \
            or (data.get("rows") if isinstance(data, dict) else None) \
            or (data if isinstance(data, list) else None)
        if not rows:
            continue
        items = [std(
            title=x.get("title") or x.get("name"),
            authors=[(y.get("name") if isinstance(y, dict) else y) for y in (x.get("authors") or x.get("creators") or [])],
            year=int(str(x.get("publishTime"))[:4]) if x.get("publishTime") else x.get("year"),
            doi=x.get("doi") or x.get("DOI"), venue="ScienceDB",
            abstract=x.get("description") or x.get("abstract"),
            url=f"https://doi.org/{x['doi']}" if x.get("doi") else (f"https://www.scidb.cn/detail?dataSetId={x.get('id')}" if x.get("id") else None),
            source="sciencedb",
        ) for x in rows[:n]]
        items = [i for i in items if i]
        if items:
            return ok("sciencedb", items)
    return blocked("sciencedb", "API path query berubah/tak dikenali (probe 415). Manual: https://www.scidb.cn/en/search?q=" + a["query"])


async def _cstr_resolve(a: dict) -> dict:
    if not os.getenv("CSTR_CLIENT_ID") or not os.getenv("CSTR_SECRET"):
        return auth_required("cstr", "CSTR_CLIENT_ID + CSTR_SECRET", "OpenAPI v3 CSTR wajib clientId & secret (32 char) — daftar di cstr.cn.")
    from urllib.parse import quote
    cid = quote(a["id"].strip(), safe="")
    r = await http_get(f"https://www.cstr.cn/openapi/v3/api/resources/{cid}",
                       headers={"clientId": os.environ["CSTR_CLIENT_ID"], "secret": os.environ["CSTR_SECRET"]})
    j = json_loose(r["body"])
    d = (j or {}).get("data") or j
    if not d:
        return failed("cstr", f"HTTP {r['status']} {r['body'][:150]}")
    return ok("cstr", [std(
        title=d.get("res_name") or d.get("title"),
        authors=d.get("creators") or [],
        year=int(str(d.get("reg_date"))[:4]) if d.get("reg_date") else None,
        doi=None, venue=None, abstract=d.get("description"),
        url=f"https://www.cstr.cn/{a['id'].strip()}",
        source="cstr", extra={"cstr_id": d.get("cstr_id") or a["id"], "type": d.get("res_type")},
    )])


CONNECTOR = {
    "id": "china-pack",
    "label": "China platforms (NSSD, Baidu Scholar, AMiner, ScienceDB, CSTR)",
    "category": "free",  # pak: mayoritas free/freemium; aminer & cstr = key (di-gate per tool env)
    "auth_env": None,
    "auth_required": False,
    "homepage": "https://www.ncpssd.cn",
    "note": "Domain space China per Reference.md: NSSD no-login (SSH China), Baidu Scholar 50 call/hari, AMiner wajib key, ScienceDB open API, CSTR identifier wajib clientId+secret.",
    "tools": [
        {"name": "nssd_search", "description": "Cari jurnal SSH China di NSSD/NCPSSD (tanpa login). Free. Hasil terbaik dengan query Bahasa China; output: title, creator, venue, abstract, keywords.", "input_schema": SEARCH_SCHEMA, "handler": _nssd_search},
        {"name": "baidu_scholar_search", "description": "Cari paper China/internasional via Baidu Scholar (Qianfan API). Freemium: ±50 call/hari tanpa key; BAIDU_API_KEY opsional. Response: title, abstract, doi, year, journalName.", "input_schema": SEARCH_SCHEMA, "handler": _baidu_scholar_search},
        {"name": "aminer_search", "description": "Cari paper China/internasional + scholar graph via AMiner Open Platform. WAJIB AMINER_API_KEY (open platform AMiner).", "input_schema": SEARCH_SCHEMA, "handler": _aminer_search},
        {"name": "sciencedb_search", "description": "Cari dataset & research artifact China di ScienceDB (CAS CNIC). Free; best-effort (API path bisa berubah — error jujur disertai saran web).", "input_schema": SEARCH_SCHEMA, "handler": _sciencedb_search},
        {"name": "cstr_resolve", "description": "Resolusi metadata satu CSTR ID (padanan DOI untuk resources China). WAJIB CSTR_CLIENT_ID + CSTR_SECRET.", "input_schema": {"type": "object", "properties": {"id": {"type": "string", "description": "CSTR ID, mis. CSTR:31258.001.SCDB.1000.1"}}, "required": ["id"], "additionalProperties": False}, "handler": _cstr_resolve},
    ],
}
