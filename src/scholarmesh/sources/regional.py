# regional.py — sumber regional per negara (Indonesia, China). Negara = metadata
# (countries per source), bukan identitas folder. Handler verbatim dari indonesia.py
# + china.py lama. Scraper bot-wall tetap best-effort dengan envelope jujur.

from __future__ import annotations

import json
import os
import re

from ..core import (auth_required, blocked, empty, failed, http_get, http_post,
                    json_loose, ok, std, strip_html)

SEARCH_SCHEMA = {
    "type": "object",
    "properties": {
        "query": {"type": "string", "description": "Kata kunci (Bahasa Indonesia/Inggris/China tergantung sumber)"},
        "limit": {"type": "integer", "minimum": 1, "maximum": 20, "default": 5},
    },
    "required": ["query"],
    "additionalProperties": False,
}


def _link_pairs(html: str) -> list[dict]:
    out = []
    for m in re.finditer(r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>([\s\S]*?)</a>', html, re.I):
        text = strip_html(m.group(2))
        if text and len(text) > 12:
            out.append({"href": m.group(1), "text": text})
    return out


def _dedupe(items: list[dict]) -> list[dict]:
    seen = set()
    out = []
    for i in items:
        k = i["title"].lower()
        if k not in seen:
            seen.add(k)
            out.append(i)
    return out


def _abs_url(href: str, base: str) -> str:
    return href if href.startswith("http") else base + href


async def _garuda_search(a: dict) -> dict:
    n = min(a.get("limit", 5), 20)
    from urllib.parse import quote
    q = quote(a["query"], safe="")
    r = await http_get(f"https://garuda.kemdikbud.go.id/documents?q={q}", timeout=12)
    if not r["ok"] and r["error"]:
        return blocked("garuda", f"Tidak bisa menjangkau garuda.kemdikbud.go.id ({r['error']}). Coba buka manual: https://garuda.kemdikbud.go.id/documents?q={q}")
    if r["status"] in (403, 429):
        return blocked("garuda", f"HTTP {r['status']} dari GARUDA (bot protection).")
    rows = [x for x in _link_pairs(r["body"]) if re.search(r"/documents/[a-f0-9]{8,}", x["href"], re.I)][:n]
    if not rows:
        return empty("garuda", "Tidak ada hasil terparse — GARUDA SPA; coba query Bahasa Indonesia.")
    items = _dedupe([std(
        title=x["text"], authors=[], year=None, doi=None, venue=None, abstract=None,
        url=_abs_url(x["href"], "https://garuda.kemdikbud.go.id"),
        source="garuda", extra={"note": "metadata lengkap buka URL di browser (SPA)"},
    ) for x in rows])
    return ok("garuda", items, {"raw_page_bytes": len(r["body"])}) if items else empty("garuda")


async def _sinta_search(a: dict) -> dict:
    n = min(a.get("limit", 5), 20)
    from urllib.parse import quote
    q = quote(a["query"], safe="")
    r = await http_get(f"https://sinta.kemdikbud.go.id/journals?q={q}", timeout=12)
    if not r["ok"] and r["error"]:
        return blocked("sinta", f"Tidak bisa menjangkau sinta.kemdikbud.go.id ({r['error']}). Manual: https://sinta.kemdikbud.go.id/journals?q={q}")
    if r["status"] in (403, 429):
        return blocked("sinta", f"HTTP {r['status']} (bot protection).")
    rows = [x for x in _link_pairs(r["body"]) if re.search(r"/journals/\d+|/authors/\d+", x["href"])][:n]
    if not rows:
        return empty("sinta")
    items = _dedupe([std(
        title=x["text"], authors=[], year=None, doi=None, venue="SINTA", abstract=None,
        url=_abs_url(x["href"], "https://sinta.kemdikbud.go.id"),
        source="sinta", extra={"kind": "author" if "authors" in x["href"] else "journal"},
    ) for x in rows])
    return ok("sinta", items) if items else empty("sinta")


async def _onesearch_search(a: dict) -> dict:
    n = min(a.get("limit", 5), 20)
    from urllib.parse import quote
    q = quote(a["query"], safe="")
    r = await http_get(f"https://onesearch.id/Search/Results?lookfor={q}&type=AllFields&limit={n}", timeout=12)
    if not r["ok"] and r["error"]:
        return blocked("onesearch", f"Tidak bisa menjangkau onesearch.id ({r['error']}).")
    if r["status"] != 200:
        return blocked("onesearch", f"HTTP {r['status']} dari OneSearch.")
    rows = [{"href": m.group(1), "text": strip_html(m.group(2))}
            for m in re.finditer(r'<a\b[^>]*href="(/Record/[^"?]+)"[^>]*class="title"[^>]*>([\s\S]*?)</a>', r["body"], re.I)]
    if not rows:
        rows = [x for x in _link_pairs(r["body"]) if re.search(r"/Record/[^?/]+$", x["href"])][:n]
    seen, uniq = set(), []
    for x in rows:
        if x["href"] not in seen:
            seen.add(x["href"])
            uniq.append(x)
    items = [std(
        title=x["text"], authors=[], year=None, doi=None, venue=None, abstract=None,
        url=_abs_url(x["href"], "https://onesearch.id"),
        source="onesearch", extra={"note": "record berisi metadata bibliografis + lokasi perpustakaan"},
    ) for x in uniq[:n]]
    return ok("onesearch", items, {"raw_page_bytes": len(r["body"])}) if items else empty("onesearch")


async def _rama_search(a: dict) -> dict:
    n = min(a.get("limit", 5), 20)
    from urllib.parse import quote
    q = quote(a["query"], safe="")
    r = await http_get(f"https://rama.kemdikbud.go.id/search?q={q}", timeout=12)
    if not r["ok"] and r["error"]:
        return blocked("rama", f"Tidak bisa menjangkau rama.kemdikbud.go.id ({r['error']}). Manual: https://rama.kemdikbud.go.id/search?q={q}")
    if r["status"] in (403, 429):
        return blocked("rama", f"HTTP {r['status']} (bot protection).")
    rows = [x for x in _link_pairs(r["body"]) if re.search(r"paper|article|document", x["href"], re.I)][:n]
    if not rows:
        return empty("rama")
    items = _dedupe([std(
        title=x["text"], authors=[], year=None, doi=None, venue="RAMA", abstract=None,
        url=_abs_url(x["href"], "https://rama.kemdikbud.go.id"), source="rama",
    ) for x in rows])
    return ok("rama", items) if items else empty("rama")


async def _moraref_search(a: dict) -> dict:
    n = min(a.get("limit", 5), 20)
    from urllib.parse import quote
    q = quote(a["query"], safe="")
    r = await http_get(f"https://moraref.kemenag.go.id/search?q={q}", timeout=12)
    if not r["ok"] and r["error"]:
        return blocked("moraref", f"Tidak bisa menjangkau moraref.kemenag.go.id ({r['error']}).")
    if re.search(r'meta name="description" content="maintenance"|sedang dalam', r["body"], re.I):
        return blocked("moraref", f"Situs Moraref sedang maintenance (terdeteksi dari halaman). Coba lagi nanti atau via Google: site:moraref.kemenag.go.id {a['query']}")
    rows = [x for x in _link_pairs(r["body"]) if re.search(r"article|paper|document", x["href"], re.I)][:n]
    if not rows:
        return empty("moraref")
    items = _dedupe([std(
        title=x["text"], authors=[], year=None, doi=None, venue="Moraref", abstract=None,
        url=_abs_url(x["href"], "https://moraref.kemenag.go.id"), source="moraref",
    ) for x in rows])
    return ok("moraref", items) if items else empty("moraref")


async def _neliti_search(a: dict) -> dict:
    from urllib.parse import quote
    q = quote(a["query"], safe="")
    r = await http_get(f"https://www.neliti.com/search/?q={q}", timeout=12, headers={"Accept-Language": "en"})
    if r["status"] in (403, 429):
        return blocked("neliti", f"HTTP {r['status']} — Neliti memakai bot protection. Manual: https://www.neliti.com/search/?q={q} (atau pakai garuda_search/onesearch_search).")
    if not r["ok"] and r["error"]:
        return blocked("neliti", f"Tidak bisa menjangkau neliti.com ({r['error']}).")
    n = min(a.get("limit", 5), 20)
    rows = [x for x in _link_pairs(r["body"]) if re.search(r"/publications/|/journals/|/reports/", x["href"])][:n]
    if not rows:
        return empty("neliti")
    items = _dedupe([std(
        title=x["text"], authors=[], year=None, doi=None, venue=None, abstract=None,
        url=_abs_url(x["href"], "https://www.neliti.com"), source="neliti",
    ) for x in rows])
    return ok("neliti", items) if items else empty("neliti")


async def _brin_search(a: dict) -> dict:
    n = min(a.get("limit", 5), 20)
    from urllib.parse import quote
    q = quote(a["query"], safe="")
    r = await http_get(f"https://repository.brin.go.id/server/api/discover/search/objects?query={q}&size={n}",
                       timeout=12, headers={"Accept": "application/json"})
    if not r["ok"] and r["error"]:
        return blocked("brin", f"Tidak bisa menjangkau repository.brin.go.id ({r['error']}). Manual: https://repository.brin.go.id/simple-search?query={q}")
    try:
        j = json.loads(r["body"])
    except Exception:
        return blocked("brin", "Respons bukan JSON — DSpace REST mungkin berubah.")
    objects = (((j.get("_embedded") or {}).get("searchResult") or {}).get("_embedded") or {}).get("objects") or []
    items = []
    for o in objects:
        m = (o.get("_embedded") or {}).get("indexableObject") or {}
        md = lambda k: ((m.get("metadata") or {}).get(k) or [{}])[0].get("value")  # noqa: E731
        issued = md("dc.date.issued")
        items.append(std(
            title=md("dc.title"),
            authors=[x.get("value") for x in (m.get("metadata") or {}).get("dc.contributor.author") or []],
            year=int(str(issued)[:4]) if issued else None,
            doi=md("dc.identifier.doi"), venue=None, abstract=md("dc.description.abstract"),
            url=f"https://repository.brin.go.id/items/{m.get('uuid')}" if m.get("uuid") else None,
            source="brin", extra={"type": md("dc.type")},
        ))
    items = [i for i in items if i]
    return ok("brin", items) if items else empty("brin")


async def _google_scholar_search(a: dict) -> dict:
    n = min(a.get("limit", 5), 10)
    from urllib.parse import quote
    q = quote(a["query"], safe="")
    r = await http_get(f"https://scholar.google.com/scholar?hl=en&q={q}&num={n}", timeout=12)
    if r["status"] == 429 or re.search(r"unusual traffic|captcha|recaptcha", r["body"], re.I):
        return blocked("googlescholar", "Google Scholar bot-detection (429/captcha). Fallback: openalex_search, semantic_scholar_search, atau crossref_search.")
    if not r["ok"] and r["error"]:
        return blocked("googlescholar", f"Tidak bisa menjangkau scholar.google.com ({r['error']}).")
    items = []
    for m in re.finditer(r'<h3 class="gs_rt[^"]*">[\s\S]*?<a[^>]*href="([^"]+)"[^>]*>([\s\S]*?)</a>', r["body"], re.I):
        items.append(std(
            title=m.group(2), authors=[], year=None, doi=None, venue=None, abstract=None,
            url=m.group(1) if m.group(1).startswith("http") else "https://scholar.google.com" + m.group(1),
            source="googlescholar", extra={"note": "snippet & sitasi buka URL di browser"},
        ))
    uniq = _dedupe(items)[:n]
    if uniq:
        return ok("googlescholar", uniq)
    # 200 tanpa hasil terparse = JS shell / consent page / markup berubah (probes 14 Nov 2026: shell).
    return blocked("googlescholar", f"HTTP {r['status']} tapi markup hasil tidak terdeteksi (JS shell / consent / markup berubah). Fallback: openalex_search, semantic_scholar_search, crossref_search.")


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
        url=p.get("url") or (f"https://www.aminer.cn/pub/{p.get('id')}" if p.get('id') else None),
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
            url=f"https://doi.org/{x['doi']}" if x.get("doi") else (f"https://www.scidb.cn/detail?dataSetId={x.get('id')}" if x.get('id') else None),
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


def _regional(id_, label, country, disciplines, note, tools, category="bot-wall", auth_env=None, auth_required=False, homepage=None):
    return {
        "id": id_, "label": label, "category": category,
        "auth_env": auth_env, "auth_required": auth_required,
        "disciplines": disciplines, "countries": [country],
        "homepage": homepage, "note": note, "tools": tools,
    }


SOURCES = [
    _regional("garuda", "GARUDA (Garba Rujukan Digital, Kemdikbud)", "ID", ["multidisciplinary"],
              "Tanpa API resmi — scraper best-effort (SPA; bisa DNS/bot-wall).",
              [{"name": "garuda_search", "description": "Cari artikel/prosiding Indonesia di GARUDA (Garba Rujukan Digital, Kemdikbud). Scraper best-effort — bisa gagal DNS/bot-wall; error disertai saran.", "input_schema": SEARCH_SCHEMA, "handler": _garuda_search}],
              homepage="https://garuda.kemdikbud.go.id"),
    _regional("sinta", "SINTA (Science and Technology Index)", "ID", ["multidisciplinary"],
              "Profil jurnal/akreditasi; scraper best-effort.",
              [{"name": "sinta_search", "description": "Cari jurnal & profil akreditasi di SINTA (Science and Technology Index). Scraper best-effort.", "input_schema": SEARCH_SCHEMA, "handler": _sinta_search}],
              homepage="https://sinta.kemdikbud.go.id"),
    _regional("onesearch", "OneSearch (PNRI union catalog)", "ID", ["multidisciplinary"],
              "Katalog gabungan perpustakaan/repository; scraper best-effort (probes 14 Nov 2026: terparse).",
              [{"name": "onesearch_search", "description": "Cari katalog perpustakaan, repository universitas, dan koleksi digital Indonesia via OneSearch (PNRI). Scraper best-effort; hasil: judul + link record.", "input_schema": SEARCH_SCHEMA, "handler": _onesearch_search}],
              homepage="https://onesearch.id"),
    _regional("rama", "RAMA (thesis/dissertation portal)", "ID", ["multidisciplinary"],
              "Skripsi/tesis/disertasi PT Indonesia; scraper best-effort.",
              [{"name": "rama_search", "description": "Cari skripsi/tesis/disertasi perguruan tinggi Indonesia di RAMA. Scraper best-effort.", "input_schema": SEARCH_SCHEMA, "handler": _rama_search}],
              homepage="https://rama.kemdikbud.go.id"),
    _regional("moraref", "Moraref (Kemenag; Islamic & social studies)", "ID", ["islamic-studies", "social-sciences"],
              "Sering maintenance — deteksi halaman maintenance jujur di envelope.",
              [{"name": "moraref_search", "description": "Cari literatur studi Islam/pendidikan/sosial di Moraref (Kemenag). Scraper best-effort; saat ini situs sering maintenance.", "input_schema": SEARCH_SCHEMA, "handler": _moraref_search}],
              homepage="https://moraref.kemenag.go.id"),
    _regional("neliti", "Neliti (Indonesian research repository)", "ID", ["multidisciplinary"],
              "Bot protection 403; fallback site search manual.",
              [{"name": "neliti_search", "description": "Cari publikasi & laporan penelitian Indonesia di Neliti. Scraper best-effort — Neliti memakai bot protection (403); bila kena, pakai site search manual.", "input_schema": SEARCH_SCHEMA, "handler": _neliti_search}],
              homepage="https://www.neliti.com"),
    _regional("brin", "BRIN Repository (DSpace 7 REST)", "ID", ["multidisciplinary"],
              "REST resmi DSpace 7; best-effort bila path berubah.",
              [{"name": "brin_search", "description": "Cari hasil riset BRIN di repository BRIN (DSpace 7 REST). Scraper best-effort.", "input_schema": SEARCH_SCHEMA, "handler": _brin_search}],
              homepage="https://repository.brin.go.id"),
    _regional("googlescholar", "Google Scholar (broad discovery, aggressive bot-detection)", "ID", ["multidisciplinary"],
              "⚠️ Sering 429/captcha; jangan dipakai bulk. (diberi countries=ID karena mirror akses jaringan; global scope)",
              [{"name": "google_scholar_search", "description": "Cari di Google Scholar (broad discovery). ⚠️ Bot detection agresif — sering 429/captcha; error disertai fallback openalex/semantic_scholar. Jangan dipakai bulk.", "input_schema": SEARCH_SCHEMA, "handler": _google_scholar_search}],
              homepage="https://scholar.google.com"),
    _regional("nssd", "NSSD/NCPSSD (SSH China, no login)", "CN", ["social-sciences", "humanities"],
              "Free; query Bahasa China memberi hasil terbaik; 403 flaky dengan retry.",
              [{"name": "nssd_search", "description": "Cari jurnal SSH China di NSSD/NCPSSD (tanpa login). Free. Hasil terbaik dengan query Bahasa China.", "input_schema": SEARCH_SCHEMA, "handler": _nssd_search}],
              category="free", homepage="https://www.ncpssd.cn"),
    _regional("baidu_scholar", "Baidu Scholar (Qianfan API)", "CN", ["multidisciplinary"],
              "Kuota gratis habis → butuh BAIDU_API_KEY; handler self-gate on 401/403.",
              [{"name": "baidu_scholar_search", "description": "Cari paper China/internasional via Baidu Scholar (Qianfan API). Freemium: ±50 call/hari tanpa key; BAIDU_API_KEY opsional.", "input_schema": SEARCH_SCHEMA, "handler": _baidu_scholar_search}],
              category="key", auth_env="BAIDU_API_KEY", homepage="https://xueshu.baidu.com"),
    _regional("aminer", "AMiner Open Platform (scholar graph)", "CN", ["computer-science"],
              "Wajib key; gate di handler.",
              [{"name": "aminer_search", "description": "Cari paper China/internasional + scholar graph via AMiner Open Platform. WAJIB AMINER_API_KEY.", "input_schema": SEARCH_SCHEMA, "handler": _aminer_search}],
              category="key", auth_env="AMINER_API_KEY", auth_required=True, homepage="https://www.aminer.cn"),
    _regional("sciencedb", "ScienceDB (CAS research data)", "CN", ["multidisciplinary"],
              "Open API tapi path best-effort (probe 415).",
              [{"name": "sciencedb_search", "description": "Cari dataset & research artifact China di ScienceDB (CAS CNIC). Free; best-effort (API path bisa berubah — error jujur disertai saran web).", "input_schema": SEARCH_SCHEMA, "handler": _sciencedb_search}],
              homepage="https://www.scidb.cn"),
    _regional("cstr", "CSTR (China Science & Technology Resources identifier)", "CN", ["multidisciplinary"],
              "Resolusi identifier wajib clientId+secret; gate di handler (dua env).",
              [{"name": "cstr_resolve", "description": "Resolusi metadata satu CSTR ID (padanan DOI untuk resources China). WAJIB CSTR_CLIENT_ID + CSTR_SECRET.", "input_schema": {"type": "object", "properties": {"id": {"type": "string", "description": "CSTR ID, mis. CSTR:31258.001.SCDB.1000.1"}}, "required": ["id"], "additionalProperties": False}, "handler": _cstr_resolve}],
              category="key", homepage="https://www.cstr.cn"),
]
