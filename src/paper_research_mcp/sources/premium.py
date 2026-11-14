# premium.py — connector yang WAJIB API key/institutional entitlement.
# Semua tools di sini terdaftar di MCP, tapi return status "auth-required" kalau env kosong.
# Sesuai Reference.md: Scopus/WoS = curated citation index (jangan disamakan cakupannya
# dengan OpenAlex/S2); Lens = approval manual; Scopus akses tergantung entitlement institusi.

from __future__ import annotations

import json
import os

from ..core import (auth_required, clamp, empty, failed, http_get, http_post,
                    json_loose, ok, std, strip_html)

SEARCH_SCHEMA = {
    "type": "object",
    "properties": {"query": {"type": "string"}, "limit": {"type": "integer", "minimum": 1, "maximum": 25, "default": 5}},
    "required": ["query"],
    "additionalProperties": False,
}


async def _ads_search(a: dict) -> dict:
    if not os.getenv("ADS_TOKEN"):
        return auth_required("ads", "ADS_TOKEN", "Daftar token gratis: https://ui.adsabs.harvard.edu/user/settings/token")
    n = min(a.get("limit", 5), 25)
    from urllib.parse import quote
    r = await http_get(f"https://api.adsabs.harvard.edu/v1/search/query?q={quote(a['query'], safe='')}&rows={n}&fl=title,author,year,doi,bibcode,abstract,pub",
                       headers={"Authorization": f"Bearer {os.environ['ADS_TOKEN']}"})
    j = json_loose(r["body"])
    docs = ((j or {}).get("response") or {}).get("docs") or []
    items = [std(
        title=(d.get("title") or [None])[0], authors=(d.get("author") or [])[:10], year=d.get("year"),
        doi=(d.get("doi") or [None])[0], venue=d.get("pub"), abstract=d.get("abstract"),
        url=f"https://ui.adsabs.harvard.edu/abs/{d.get('bibcode')}", source="ads",
        extra={"bibcode": d.get("bibcode"), "citation_count": d.get("citation_count")},
    ) for d in docs]
    items = [i for i in items if i]
    return ok("ads", items, {"total": ((j or {}).get("response") or {}).get("numFound")}) if items else empty("ads")


async def _alphaxiv_search(a: dict) -> dict:
    if not os.getenv("ALPHAXIV_API_KEY"):
        return auth_required("alphaxiv", "ALPHAXIV_API_KEY", "Alternatif: tambahkan MCP resmi AlphaXiv langsung (endpoint https://api.alphaxiv.org/mcp/v1, OAuth 2.1 atau API key) — kemampuan lengkapnya (21 tools: PDF Q&A, researcher graph) lebih kaya dari proxy ini.")
    n = min(a.get("limit", 5), 20)
    from urllib.parse import quote
    r = await http_get(f"https://api.alphaxiv.org/v1/alphaxiv/search?query={quote(a['query'], safe='')}&limit={n}",
                       headers={"Authorization": f"Bearer {os.environ['ALPHAXIV_API_KEY']}"})
    j = json_loose(r["body"])
    rows = (j or {}).get("results") or (j or {}).get("data")
    if not rows:
        return failed("alphaxiv", f"HTTP {r['status']} {r['body'][:150]}")
    items = [std(
        title=p.get("title"), authors=[(x.get("name") if isinstance(x, dict) else x) for x in (p.get("authors") or [])],
        year=int(p["year"]) if p.get("year") else None, doi=p.get("doi"), venue=p.get("journal"),
        abstract=p.get("abstract"),
        url=p.get("url") or (f"https://www.alphaxiv.org/abs/{p.get('arxiv_id')}" if p.get("arxiv_id") else None),
        pdf=p.get("pdf_url"), source="alphaxiv", extra={"arxiv_id": p.get("arxiv_id")},
    ) for p in rows[:n]]
    items = [i for i in items if i]
    return ok("alphaxiv", items) if items else empty("alphaxiv")


async def _scopus_search(a: dict) -> dict:
    if not os.getenv("SCOPUS_API_KEY"):
        return auth_required("scopus", "SCOPUS_API_KEY", "Daftar di dev.elsevier.com; akses data tergantung entitlement institusi, bukan sekadar API key.")
    n = min(a.get("limit", 5), 25)
    from urllib.parse import quote
    r = await http_get(f"https://api.elsevier.com/content/search/scopus?query={quote(a['query'], safe='')}&count={n}",
                       headers={"X-ELS-APIKey": os.environ["SCOPUS_API_KEY"], "Accept": "application/json"})
    j = json_loose(r["body"])
    rows = ((j or {}).get("search-results") or {}).get("entry")
    if not rows:
        msg = json.dumps(j)[:200]
        if r["status"] in (401, 403) or "entitlement" in msg.lower() or "INVALID" in msg:
            return auth_required("scopus", "SCOPUS_API_KEY", f"Key ada tapi akses ditolak ({r['status']}): {msg} — entitlement institusi diperlukan.")
        return failed("scopus", f"HTTP {r['status']} {msg}")
    items = []
    for e in rows:
        if "error" in e:
            continue
        authors = []
        for x in e.get("auth:author") or e.get("authors") or []:
            authors.append(x.get("authname") or f"{x.get('given-name', '')} {x.get('surname', '')}".strip())
        items.append(std(
            title=e.get("dc:title"), authors=authors,
            year=int(str(e.get("prism:coverDate"))[:4]) if e.get("prism:coverDate") else None,
            doi=e.get("prism:doi"), venue=e.get("prism:publicationName"), abstract=e.get("dc:description"),
            url=next((l.get("@href") for l in (e.get("link") or []) if l.get("@ref") == "scopus"), None)
                or (f"https://doi.org/{e['prism:doi']}" if e.get("prism:doi") else None),
            source="scopus", extra={"cited_by": e.get("citedby-count"), "eid": e.get("eid")},
        ))
    items = [i for i in items if i]
    return ok("scopus", items, {"total": ((j or {}).get("search-results") or {}).get("opensearch:totalResults")}) if items else empty("scopus")


async def _lens_search(a: dict) -> dict:
    if not os.getenv("LENS_TOKEN"):
        return auth_required("lens", "LENS_TOKEN", "Lens API perlu approval akses + token (bukan self-service).")
    n = min(a.get("limit", 5), 25)
    r = await http_post("https://api.lens.org/scholarly/search",
                        {"query": {"bool": {"must": {"query_string": {"query": a["query"]}}}}, "size": n},
                        headers={"Authorization": f"Bearer {os.environ['LENS_TOKEN']}"}, form=False)
    j = json_loose(r["body"])
    rows = (j or {}).get("data")
    if not rows:
        return failed("lens", f"HTTP {r['status']} {json.dumps(j)[:150]}")
    items = [std(
        title=(d.get("title") or [None])[0], authors=[x.get("display_name") for x in (d.get("authors") or [])],
        year=d.get("year_published"), doi=d.get("doi"), venue=(d.get("source") or {}).get("title"),
        abstract=clamp(strip_html(d["abstract"][0])) if d.get("abstract") else None,
        url=f"https://www.lens.org/lens/patent/{d.get('lens_id')}" if d.get("lens_id") else None,
        source="lens", extra={"lens_id": d.get("lens_id"), "patent_count": d.get("patent_count")},
    ) for d in rows[:n]]
    items = [i for i in items if i]
    return ok("lens", items, {"total": (j or {}).get("total")}) if items else empty("lens")


async def _dimensions_search(a: dict) -> dict:
    if not os.getenv("DIMENSIONS_TOKEN"):
        return auth_required("dimensions", "DIMENSIONS_TOKEN", "Token via https://www.dimensions.ai/products/api/")
    n = min(a.get("limit", 5), 25)
    q = f'search publications in publications for "{a["query"].replace(chr(34), "")}" return publications[id+title+year+doi+journal+abstract] limit {n}'
    r = await http_post("https://app.dimensions.ai/api/dimensions/2", {"query": q},
                        headers={"Authorization": f"Bearer {os.environ['DIMENSIONS_TOKEN']}"}, form=False)
    j = json_loose(r["body"])
    rows = (j or {}).get("publications")
    if not rows:
        return failed("dimensions", f"HTTP {r['status']} {json.dumps(j)[:150]}")
    items = [std(
        title=p.get("title"), authors=[], year=p.get("year"), doi=p.get("doi"),
        venue=(p.get("journal") or {}).get("title"), abstract=p.get("abstract"),
        url=f"https://doi.org/{p['doi']}" if p.get("doi") else f"https://app.dimensions.ai/details/publication/{p.get('id')}",
        source="dimensions",
    ) for p in rows]
    items = [i for i in items if i]
    return ok("dimensions", items) if items else empty("dimensions")


async def _wos_search(a: dict) -> dict:
    if not os.getenv("WOS_API_KEY"):
        return auth_required("wos", "WOS_API_KEY", "Daftar di developer.clarivate.com (Lite API terbatas; full API butuh subscription).")
    n = min(a.get("limit", 5), 25)
    r = await http_post(f"https://api.clarivate.com/api/woslite?databaseId=WOK&count={n}",
                        {"usrQuery": a["query"], "option": "OpenAccess"},
                        headers={"X-ApiKey": os.environ["WOS_API_KEY"]}, form=False)
    j = json_loose(r["body"])
    rows = (((j or {}).get("Data") or {}).get("Records") or {}).get("records") or {}
    recs = rows.get("REC") or []
    if isinstance(recs, dict):
        recs = [recs]
    items = []
    for rec in recs:
        titles = (((rec.get("static_data") or {}).get("summary") or {}).get("titles") or {}).get("title") or []
        title = next((t.get("value") for t in titles if t.get("type") == "item"), None)
        venue = next((t.get("value") for t in titles if t.get("type") == "source"), None)
        year = ((rec.get("static_data") or {}).get("summary") or {}).get("pub_info") or {}
        pubyear = year.get("pubyear")
        doi = None
        for ident in (((rec.get("dynamic_data") or {}).get("cluster_related") or {}).get("identifier") or []):
            if isinstance(ident, dict) and ident.get(".attrib") == "identifier.doi":
                doi = ident.get(".content")
        if not doi:
            for ident in (((rec.get("dynamic_data") or {}).get("identifiers") or {}).get("identifier") or []):
                if isinstance(ident, dict) and ident.get("type") == "doi":
                    doi = ident.get("value")
        items.append(std(
            title=title, authors=[], year=int(pubyear) if pubyear else None, doi=doi, venue=venue,
            abstract=None, url=f"https://doi.org/{doi}" if doi else None, source="wos", extra={"ut": rec.get("UID")},
        ))
    items = [i for i in items if i]
    return ok("wos", items, {"total": ((j or {}).get("QueryResult") or {}).get("RecordsFound")}) if items else empty("wos")


CONNECTOR = {
    "id": "premium-pack",
    "label": "Premium (NASA ADS, AlphaXiv, Scopus, The Lens, Dimensions, Web of Science)",
    "category": "key",
    "auth_env": None,  # per-tool env; gate dilakukan di handler masing-masing
    "auth_required": False,
    "homepage": "https://dev.elsevier.com",
    "note": "Curated citation indexes & platform berlangganan (Scopus/WoS = curated index, jangan disamakan cakupannya dengan OpenAlex/S2). AlphaXiv punya MCP resmi sendiri di api.alphaxiv.org/mcp/v1 — pertimbangkan tambahkan langsung.",
    "tools": [
        {"name": "ads_search", "description": "Cari paper astronomi/astrofisika di NASA ADS (metadata, citations, abstracts). WAJIB ADS_TOKEN (gratis untuk peneliti).", "input_schema": SEARCH_SCHEMA, "handler": _ads_search},
        {"name": "alphaxiv_search", "description": "Cari paper + semantic retrieval + researcher graph via AlphaXiv. WAJIB ALPHAXIV_API_KEY (atau pakai MCP resmi alphaxiv langsung — lihat note).", "input_schema": SEARCH_SCHEMA, "handler": _alphaxiv_search},
        {"name": "scopus_search", "description": "Cari publikasi di Scopus (abstract & citation database). WAJIB SCOPUS_API_KEY + entitlement institusi; tanpa entitlement akan ditolak Elsevier.", "input_schema": SEARCH_SCHEMA, "handler": _scopus_search},
        {"name": "lens_search", "description": "Cari scholarly works (+patent linkage) di The Lens. WAJIB LENS_TOKEN (approval manual di lens.org).", "input_schema": SEARCH_SCHEMA, "handler": _lens_search},
        {"name": "dimensions_search", "description": "Cari publikasi di Dimensions (publications + citations + grants). WAJIB DIMENSIONS_TOKEN.", "input_schema": SEARCH_SCHEMA, "handler": _dimensions_search},
        {"name": "wos_search", "description": "Cari publikasi di Web of Science (Lite API). WAJIB WOS_API_KEY (Clarivate developer portal).", "input_schema": SEARCH_SCHEMA, "handler": _wos_search},
    ],
}
