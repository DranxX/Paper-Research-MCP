# indexes.py — sumber multidisciplinary indexes (metadata & sitasi skala besar).
# Handler diambil verbatim dari free.py/premium.py lama. Negara & disiplin sekarang
# metadata per sumber (countries/disciplines), bukan identitas folder.

from __future__ import annotations

import json
import os

from ..core import (auth_required, blocked, clamp, empty, failed, http_get,
                    http_post, json_loose, ok, std, strip_html)

EMAIL = "scholarmesh@users.noreply.github.com"


def _search_schema() -> dict:
    return {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Kata kunci pencarian"},
            "limit": {"type": "integer", "minimum": 1, "maximum": 25, "default": 5},
            "year_from": {"type": "integer", "description": "Filter tahun terbit (>=)"},
            "year_to": {"type": "integer", "description": "Filter tahun terbit (<=)"},
        },
        "required": ["query"],
        "additionalProperties": False,
    }


def _openalex_abstract(inv):
    if not isinstance(inv, dict):
        return None
    words: list[str] = []
    for w, positions in inv.items():
        for p in positions:
            while len(words) <= p:  # posisi inverted-index punya gap — jangan langsung index
                words.append("")
            words[p] = w
    text = " ".join(w for w in words if w)
    return text or None


async def _openalex_search(a: dict) -> dict:
    n = min(a.get("limit", 5), 25)
    url = f"https://api.openalex.org/works?search={a['query']}&per-page={n}&mailto={EMAIL}"
    date_filters = []
    if a.get("year_from"):
        date_filters.append(f"from_publication_date:{a['year_from']}-01-01")
    if a.get("year_to"):
        date_filters.append(f"to_publication_date:{a['year_to']}-12-31")
    if date_filters:
        url += "&filter=" + ",".join(date_filters)
    import os
    if os.getenv("OPENALEX_API_KEY"):
        url += f"&api_key={os.environ['OPENALEX_API_KEY']}"
    r = await http_get(url)
    j = json_loose(r["body"])
    if not j or "results" not in j:
        return failed("openalex", f"HTTP {r['status']} {r['error'] or r['body'][:200]}")
    items = [
        std(
            title=w.get("display_name"),
            authors=[x["author"]["display_name"] for x in (w.get("authorships") or []) if x.get("author")],
            year=w.get("publication_year"),
            doi=w.get("doi"),
            venue=(w.get("primary_location") or {}).get("source", {}).get("display_name"),
            abstract=_openalex_abstract(w.get("abstract_inverted_index")),
            url=w.get("doi") or (w.get("ids") or {}).get("landing_page"),
            pdf=(w.get("best_oa_location") or {}).get("pdf_url"),
            source="openalex",
            extra={"cited_by_count": w.get("cited_by_count"), "open_access": (w.get("open_access") or {}).get("oa_status"), "type": w.get("type")},
        )
        for w in j["results"]
    ]
    return ok("openalex", items, {"total": (j.get("meta") or {}).get("count")})


async def _crossref_search(a: dict) -> dict:
    n = min(a.get("limit", 5), 25)
    url = f"https://api.crossref.org/works?query={a['query']}&rows={n}&select=title,author,issued,DOI,container-title,abstract,URL,link,is-referenced-by-count,type"
    filters = []
    if a.get("filter"):
        filters.append(a["filter"])
    if a.get("year_from"):
        filters.append(f"from-pub-date:{a['year_from']}-01-01")
    if a.get("year_to"):
        filters.append(f"until-pub-date:{a['year_to']}-12-31")
    if filters:
        from urllib.parse import quote
        url += "&filter=" + quote(",".join(filters), safe="")
    r = await http_get(url)
    j = json_loose(r["body"])
    if not j or "items" not in (j.get("message") or {}):
        return failed("crossref", f"HTTP {r['status']}")
    msg = j["message"]
    items = [
        std(
            title=(w.get("title") or [None])[0],
            authors=[" ".join(p for p in (x.get("given"), x.get("family")) if p) for x in (w.get("author") or [])],
            year=((w.get("issued") or {}).get("date-parts") or [[None]])[0][0],
            doi=w.get("DOI"),
            venue=(w.get("container-title") or [None])[0],
            abstract=w.get("abstract"),
            url=w.get("URL") or (f"https://doi.org/{w['DOI']}" if w.get("DOI") else None),
            pdf=next((l["URL"] for l in (w.get("link") or []) if l.get("content-type") == "application/pdf"), None),
            source="crossref",
            extra={"cited_by_count": w.get("is-referenced-by-count"), "type": w.get("type")},
        )
        for w in msg["items"]
    ]
    return ok("crossref", items, {"total": msg.get("total-results")})


async def _crossref_doi(a: dict) -> dict:
    import re as _re
    doi = _re.sub(r"^https?://(dx\.)?doi\.org/", "", str(a["doi"]).strip(), flags=_re.I)
    r = await http_get(f"https://api.crossref.org/works/{doi}")
    j = json_loose(r["body"])
    w = (j or {}).get("message")
    if not w:
        return failed("crossref", f"DOI tidak ditemukan / HTTP {r['status']}")
    return ok("crossref", [std(
        title=(w.get("title") or [None])[0],
        authors=[" ".join(p for p in (x.get("given"), x.get("family")) if p) for x in (w.get("author") or [])],
        year=((w.get("issued") or {}).get("date-parts") or [[None]])[0][0],
        doi=w.get("DOI"),
        venue=(w.get("container-title") or [None])[0],
        abstract=w.get("abstract"),
        url=w.get("URL"),
        source="crossref",
        extra={"cited_by_count": w.get("is-referenced-by-count"), "publisher": w.get("publisher"), "type": w.get("type")},
    )])


async def _doaj_search(a: dict) -> dict:
    n = min(a.get("limit", 5), 25)
    from urllib.parse import quote
    r = await http_get(f"https://doaj.org/api/search/articles/{quote(a['query'], safe='')}&pageSize={n}")
    j = json_loose(r["body"])
    if not j or "results" not in j:
        return failed("doaj", f"HTTP {r['status']}")
    items = []
    for x in j["results"]:
        b = x.get("bibjson") or {}
        doi = next((i["id"] for i in (b.get("identifier") or []) if i.get("type") == "doi"), None)
        link = next((l["url"] for l in (b.get("link") or []) if l.get("type") == "fulltext"), None)
        items.append(std(
            title=b.get("title"), authors=[au.get("name") for au in (b.get("author") or [])],
            year=int(b["year"]) if b.get("year") else None, doi=doi, venue=(b.get("journal") or {}).get("title"),
            abstract=b.get("abstract"), url=link or (f"https://doi.org/{doi}" if doi else None),
            source="doaj", extra={"license": ((b.get("journal") or {}).get("license") or [{}])[0].get("title"), "oa": True},
        ))
    items = [i for i in items if i]
    return ok("doaj", items, {"total": j.get("total")}) if items else empty("doaj")


async def _semantic_scholar_search(a: dict) -> dict:
    import os
    n = min(a.get("limit", 5), 20)
    headers = {}
    if os.getenv("S2_API_KEY"):
        headers["x-api-key"] = os.environ["S2_API_KEY"]
    year_param = ""
    if a.get("year_from") or a.get("year_to"):
        year_param = f"&year={a.get('year_from', '')}-{a.get('year_to', '')}"
    r = await http_get(
        f"https://api.semanticscholar.org/graph/v1/paper/search?query={a['query']}&limit={n}{year_param}"
        f"&fields=title,abstract,year,externalIds,venue,authors,openAccessPdf,url,citationCount",
        headers=headers,
    )
    j = json_loose(r["body"])
    if r["status"] == 429:
        return blocked("semanticscholar", "Rate-limited (429) tanpa API key. Set env S2_API_KEY (gratis) atau pakai openalex_search.")
    if not j or "data" not in j:
        return failed("semanticscholar", f"HTTP {r['status']}")
    items = []
    for w in j["data"]:
        ext = w.get("externalIds") or {}
        items.append(std(
            title=w.get("title"), authors=[x.get("name") for x in (w.get("authors") or [])], year=w.get("year"),
            doi=ext.get("DOI"), venue=w.get("venue"), abstract=w.get("abstract"),
            url=w.get("url") or (f"https://doi.org/{ext['DOI']}" if ext.get("DOI") else None),
            pdf=(w.get("openAccessPdf") or {}).get("url"), source="semanticscholar",
            extra={"citationCount": w.get("citationCount")},
        ))
    items = [i for i in items if i]
    return ok("semanticscholar", items, {"total": j.get("total")}) if items else empty("semanticscholar")


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
        pub_info = ((rec.get("static_data") or {}).get("summary") or {}).get("pub_info") or {}
        pubyear = pub_info.get("pubyear")
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


SOURCES = [
    {
        "id": "openalex", "label": "OpenAlex (open scholarly metadata, citation graph)",
        "category": "free", "auth_env": "OPENALEX_API_KEY", "auth_required": False,
        "disciplines": ["multidisciplinary"], "countries": [],
        "homepage": "https://openalex.org",
        "note": "Open metadata index. Tanpa key pakai budget harian per-IP; OPENALEX_API_KEY (opsional) memberi budget sendiri.",
        "tools": [{"name": "openalex_search", "description": "Cari paper via OpenAlex (open scholarly metadata, citation graph, OA locations). Free, tanpa API key (budget harian bersama per IP; OPENALEX_API_KEY opsional menaikkan budget).", "input_schema": _search_schema(), "handler": _openalex_search}],
    },
    {
        "id": "crossref", "label": "Crossref (DOI registry metadata)",
        "category": "free", "auth_env": None, "auth_required": False,
        "disciplines": ["multidisciplinary"], "countries": [],
        "homepage": "https://www.crossref.org",
        "note": "DOI registry; metadata resmi penerbit.",
        "tools": [
            {"name": "crossref_search", "description": "Cari metadata publikasi via Crossref (DOI registry). Free, tanpa API key.", "input_schema": {**_search_schema(), "properties": {**_search_schema()["properties"], "filter": {"type": "string", "description": "Filter Crossref opsional, mis. 'type:journal-article'"}}}, "handler": _crossref_search},
            {"name": "crossref_doi", "description": "Ambil metadata lengkap satu publikasi berdasarkan DOI via Crossref.", "input_schema": {"type": "object", "properties": {"doi": {"type": "string", "description": "DOI, mis. 10.1038/nature12373"}}, "required": ["doi"], "additionalProperties": False}, "handler": _crossref_doi},
        ],
    },
    {
        "id": "doaj", "label": "DOAJ (curated open-access articles)",
        "category": "free", "auth_env": None, "auth_required": False,
        "disciplines": ["multidisciplinary"], "countries": [],
        "homepage": "https://doaj.org",
        "note": "Artikel OA terkurasi.",
        "tools": [{"name": "doaj_search", "description": "Cari artikel open-access terkurasi di DOAJ. Free, tanpa API key.", "input_schema": _search_schema(), "handler": _doaj_search}],
    },
    {
        "id": "semanticscholar", "label": "Semantic Scholar (rate-limited tanpa key)",
        "category": "bot-wall", "auth_env": "S2_API_KEY", "auth_required": False,
        "disciplines": ["multidisciplinary"], "countries": [],
        "homepage": "https://www.semanticscholar.org",
        "note": "429 tanpa key; S2_API_KEY gratis menghilangkan limit.",
        "tools": [{"name": "semantic_scholar_search", "description": "Cari paper via Semantic Scholar. Free tapi rate-limit ketat tanpa key — kalau 429, pakai openalex_search sebagai fallback.", "input_schema": _search_schema(), "handler": _semantic_scholar_search}],
    },
    {
        "id": "lens", "label": "The Lens (scholarly works + patent linkage)",
        "category": "key", "auth_env": "LENS_TOKEN", "auth_required": True,
        "disciplines": ["multidisciplinary"], "countries": [],
        "homepage": "https://www.lens.org",
        "note": "Approval manual.",
        "tools": [{"name": "lens_search", "description": "Cari scholarly works (+patent linkage) di The Lens. WAJIB LENS_TOKEN (approval manual di lens.org).", "input_schema": _search_schema(), "handler": _lens_search}],
    },
    {
        "id": "dimensions", "label": "Dimensions (publications, citations, grants)",
        "category": "key", "auth_env": "DIMENSIONS_TOKEN", "auth_required": True,
        "disciplines": ["multidisciplinary"], "countries": [],
        "homepage": "https://www.dimensions.ai",
        "note": "Token via Dimensions API portal.",
        "tools": [{"name": "dimensions_search", "description": "Cari publikasi di Dimensions (publications + citations + grants). WAJIB DIMENSIONS_TOKEN.", "input_schema": _search_schema(), "handler": _dimensions_search}],
    },
    {
        "id": "scopus", "label": "Scopus (curated citation index, Elsevier)",
        "category": "key", "auth_env": "SCOPUS_API_KEY", "auth_required": True,
        "disciplines": ["multidisciplinary"], "countries": [],
        "homepage": "https://dev.elsevier.com",
        "note": "Butuh entitlement institusi selain key.",
        "tools": [{"name": "scopus_search", "description": "Cari publikasi di Scopus (abstract & citation database). WAJIB SCOPUS_API_KEY + entitlement institusi; tanpa entitlement akan ditolak Elsevier.", "input_schema": _search_schema(), "handler": _scopus_search}],
    },
    {
        "id": "wos", "label": "Web of Science Lite (Clarivate)",
        "category": "key", "auth_env": "WOS_API_KEY", "auth_required": True,
        "disciplines": ["multidisciplinary"], "countries": [],
        "homepage": "https://developer.clarivate.com",
        "note": "Lite API terbatas; full API berlangganan.",
        "tools": [{"name": "wos_search", "description": "Cari publikasi di Web of Science (Lite API). WAJIB WOS_API_KEY (Clarivate developer portal).", "input_schema": _search_schema(), "handler": _wos_search}],
    },
]
