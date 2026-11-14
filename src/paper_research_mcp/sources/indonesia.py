# indonesia.py — kategori bot-wall: sumber akademik Indonesia tanpa API resmi.
# Sesuai Reference.md §"Catatan teknis": jangan anggap API publik stabil — connector
# scraper best-effort dengan parser multi-strategi, graceful envelope, dan status jujur.
# Probes 14 Nov 2026: onesearch 200 (diparse), moraref = halaman maintenance, neliti 403,
# garuda/sinta/rama/brin DNS gagal dari jaringan sandbox (dari jaringan lain bisa jalan).

from __future__ import annotations

import re

from ..core import (empty, blocked, http_get, ok, std, strip_html)

SEARCH_SCHEMA = {
    "type": "object",
    "properties": {
        "query": {"type": "string", "description": "Kata kunci (Bahasa Indonesia/Inggris tergantung sumber)"},
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
    import json
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


CONNECTOR = {
    "id": "indonesia-pack",
    "label": "Indonesia sources (GARUDA, SINTA, OneSearch, RAMA, Moraref, Neliti, BRIN, Google Scholar)",
    "category": "bot-wall",
    "auth_env": None,
    "auth_required": False,
    "homepage": "https://garuda.kemdikbud.go.id",
    "note": "Bloket indonesia_research per Reference.md — tanpa API resmi, scraper best-effort. Probes 14 Nov 2026: onesearch 200 (terparse), moraref maintenance, neliti 403, garuda/sinta/rama/brin DNS gagal dari jaringan sandbox (jaringan lain bisa jalan).",
    "tools": [
        {"name": "garuda_search", "description": "Cari artikel/prosiding Indonesia di GARUDA (Garba Rujukan Digital, Kemdikbud). Scraper best-effort — bisa gagal DNS/bot-wall; error disertai saran.", "input_schema": SEARCH_SCHEMA, "handler": _garuda_search},
        {"name": "sinta_search", "description": "Cari jurnal & profil akreditasi di SINTA (Science and Technology Index). Scraper best-effort.", "input_schema": SEARCH_SCHEMA, "handler": _sinta_search},
        {"name": "onesearch_search", "description": "Cari katalog perpustakaan, repository universitas, dan koleksi digital Indonesia via OneSearch (PNRI). Scraper best-effort; hasil: judul + link record.", "input_schema": SEARCH_SCHEMA, "handler": _onesearch_search},
        {"name": "rama_search", "description": "Cari skripsi/tesis/disertasi perguruan tinggi Indonesia di RAMA. Scraper best-effort.", "input_schema": SEARCH_SCHEMA, "handler": _rama_search},
        {"name": "moraref_search", "description": "Cari literatur studi Islam/pendidikan/sosial di Moraref (Kemenag). Scraper best-effort; saat ini situs dalam maintenance.", "input_schema": SEARCH_SCHEMA, "handler": _moraref_search},
        {"name": "neliti_search", "description": "Cari publikasi & laporan penelitian Indonesia di Neliti. Scraper best-effort — Neliti memakai bot protection (403); bila kena, pakai site search manual.", "input_schema": SEARCH_SCHEMA, "handler": _neliti_search},
        {"name": "brin_search", "description": "Cari hasil riset BRIN di repository BRIN (DSpace 7 REST). Scraper best-effort.", "input_schema": SEARCH_SCHEMA, "handler": _brin_search},
        {"name": "google_scholar_search", "description": "Cari di Google Scholar (broad discovery). ⚠️ Bot detection agresif — sering 429/captcha; error disertai fallback openalex/semantic_scholar. Jangan dipakai bulk.", "input_schema": SEARCH_SCHEMA, "handler": _google_scholar_search},
    ],
}
