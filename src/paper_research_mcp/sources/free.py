# free.py — connectors dengan API publik terbuka, tanpa API key.
# Semua endpoint di-probe live sebelum ditulis (OpenAlex, Crossref, arXiv, DOAJ,
# Semantic Scholar, OpenReview, INSPIRE-HEP, ERIC, Unpaywall, ORCID).

from __future__ import annotations

import re

from ..core import (blocked, clamp, empty, failed, http_get, json_loose, ok,
                    std, strip_html)

EMAIL = "paper-research-mcp@users.noreply.github.com"


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


async def _arxiv_search(a: dict) -> dict:
    n = min(a.get("limit", 5), 30)
    q = f"({a['query']})"
    if a.get("year_from") or a.get("year_to"):
        from_ = f"{a.get('year_from') or 1000}01010000"
        to_ = f"{a.get('year_to') or 9999}12312359"
        q += f" AND submittedDate:[{from_} TO {to_}]"
    from urllib.parse import quote
    # arXiv API: spasi = '+' di URL; jangan encode '+' di range submittedDate jadi %2B.
    encoded = quote(q, safe="").replace("%20", "+")
    r = await http_get(f"https://export.arxiv.org/api/query?search_query={encoded}&max_results={n}&sortBy=relevance")
    if not r["ok"]:
        return failed("arxiv", f"HTTP {r['status']} {r['error'] or ''}")
    body = r["body"]
    items = []
    for chunk in body.split("<entry>")[1:]:
        chunk = chunk.split("</entry>")[0]

        def pick(tag: str) -> str:
            m = re.search(rf"<{tag}[^>]*>([\s\S]*?)</{tag}>", chunk)
            return strip_html(m.group(1)) if m else ""

        pdf_m = re.search(r'href="(https?://arxiv\.org/pdf/[^"]+)"', chunk)
        items.append(std(
            title=pick("title"),
            authors=[m.group(1) for m in re.finditer(r"<name>([\s\S]*?)</name>", chunk)],
            year=int((re.match(r"^(\d{4})", pick("published")) or [None, None])[1] or 0) or None,
            doi=(re.search(r"<arxiv:doi[^>]*>([\s\S]*?)</arxiv:doi>", chunk) or [None, ""])[1].strip() or None,
            venue="arXiv",
            abstract=pick("summary"),
            url=(re.search(r"<id>([\s\S]*?)</id>", chunk) or [None, ""])[1].strip(),
            pdf=pdf_m.group(1) if pdf_m else None,
            source="arxiv",
            extra={"primary_category": (re.search(r'<arxiv:primary_category[^>]*term="([^"]+)"', chunk) or [None, None])[1]},
        ))
    items = [i for i in items if i]
    return ok("arxiv", items) if items else empty("arxiv")


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


async def _openreview_search(a: dict) -> dict:
    n = min(a.get("limit", 5), 20)
    from urllib.parse import quote
    r = await http_get(f"https://api2.openreview.net/notes/search?term={quote(a['query'], safe='')}&limit={n * 2}")
    j = json_loose(r["body"])
    if not j or "notes" not in j:
        return failed("openreview", f"HTTP {r['status']}")

    def map_note(nt: dict, kind: str) -> dict | None:
        c = nt.get("content") or {}

        def v(k):
            val = c.get(k)
            return val.get("value") if isinstance(val, dict) else val

        title = v("title") or (f"[review] {str(v('summary') or '')[:90]}" if kind == "review" else None)
        return std(
            title=title, authors=v("authors") or [],
            year=(int(__import__("datetime").datetime.utcfromtimestamp(nt["pdate"]).year)
                  if nt.get("pdate") else (int(v("year")) if v("year") else None)),
            doi=None,
            venue=(nt.get("invitations") or [None])[0].split("/")[-2] if nt.get("invitations") else v("venue"),
            abstract=v("abstract") or (v("summary") if kind == "review" else None),
            url=f"https://openreview.net/forum?id={nt.get('forum') or nt.get('id')}",
            pdf=f"https://openreview.net/pdf?id={nt.get('forum') or nt.get('id')}" if v("pdf") else None,
            source="openreview",
            extra={"kind": kind, "forum_id": nt.get("forum") or nt.get("id"), "rating": v("rating"), "keywords": v("keywords")},
        )

    submissions = [map_note(nt, "submission") for nt in j["notes"] if (nt.get("content") or {}).get("title", {}).get("value")]
    submissions = [s for s in submissions if s]
    base = submissions[:n] if submissions else [m for m in (map_note(nt, "review") for nt in j["notes"]) if m][:n]
    return ok("openreview", base, {"note": "hasil campuran submission+review dari OpenReview search"}) if base else empty("openreview")


async def _openreview_notes(a: dict) -> dict:
    from urllib.parse import quote
    r = await http_get(f"https://api2.openreview.net/notes?forum={quote(a['forum'], safe='')}&details=replyCount")
    j = json_loose(r["body"])
    if r["status"] == 403 and "ChallengeRequiredError" in r["body"]:
        return blocked("openreview", "OpenReview meminta challenge verification (anti-scraping). Coba lagi nanti atau buka forum di browser: https://openreview.net/forum?id=" + a["forum"])
    if not j or "notes" not in j:
        return failed("openreview", f"HTTP {r['status']}")
    notes = []
    for nt in j["notes"]:
        content = {}
        for k, v in (nt.get("content") or {}).items():
            val = v.get("value") if isinstance(v, dict) else v
            content[k] = clamp(val if isinstance(val, str) else json.dumps(val), 800)
        notes.append({
            "id": nt.get("id"), "invitations": nt.get("invitations"),
            "readers": "public" if "everyone" in (nt.get("readers") or []) else "restricted",
            **content,
        })
    items = [{**n, "title": n.get("title") or (n.get("invitations") or [None])[0], "source": "openreview"} for n in notes]
    return ok("openreview", items, {"forum": a["forum"], "count_raw": len(notes)})


async def _inspire_search(a: dict) -> dict:
    n = min(a.get("limit", 5), 25)
    from urllib.parse import quote
    r = await http_get(f"https://inspirehep.net/api/literature?q={quote(a['query'], safe='')}&size={n}")
    j = json_loose(r["body"])
    if not j or "hits" not in j:
        return failed("inspirehep", f"HTTP {r['status']}")
    items = []
    for h in j["hits"]["hits"]:
        m = h.get("metadata") or {}
        items.append(std(
            title=(m.get("titles") or [{}])[0].get("title"),
            authors=[x.get("full_name") for x in (m.get("authors") or [])],
            year=(m.get("publication_info") or [{}])[0].get("year") or (m.get("preprint_date") or "")[:4] or None,
            doi=(m.get("dois") or [{}])[0].get("value"),
            venue=(m.get("publication_info") or [{}])[0].get("journal_title"),
            abstract=(m.get("abstracts") or [{}])[0].get("value"),
            url=f"https://inspirehep.net/literature/{h.get('id')}",
            pdf=(m.get("documents") or [{}])[0].get("url"),
            source="inspirehep",
            extra={"arxiv_eprint": (m.get("arxiv_eprints") or [{}])[0].get("value"), "citation_count": m.get("citation_count")},
        ))
    items = [i for i in items if i]
    return ok("inspirehep", items, {"total": j["hits"].get("total")}) if items else empty("inspirehep")


async def _eric_search(a: dict) -> dict:
    n = min(a.get("limit", 5), 25)
    from urllib.parse import quote
    fields = "title,author,publicationdateyear,source,ericid,description,id"
    r = await http_get(f"https://api.ies.ed.gov/eric/?search={quote(a['query'], safe='')}&format=json&pageSize={n}&fields={fields}")
    j = json_loose(r["body"])
    if not j or "docs" not in (j.get("response") or {}):
        return failed("eric", f"HTTP {r['status']}")
    docs = j["response"]["docs"][:n]
    items = [std(
        title=d.get("title"), authors=d.get("author") or [],
        year=int(d["publicationdateyear"]) if d.get("publicationdateyear") else None,
        doi=None, venue=d.get("source"), abstract=d.get("description"),
        url=f"https://eric.ed.gov/?id={d.get('ericid') or d.get('id')}",
        source="eric", extra={"eric_id": d.get("ericid") or d.get("id")},
    ) for d in docs]
    items = [i for i in items if i]
    return ok("eric", items, {"total": j["response"].get("numFound")}) if items else empty("eric")


async def _unpaywall_resolve(a: dict) -> dict:
    import re as _re
    from urllib.parse import quote
    doi = _re.sub(r"^https?://(dx\.)?doi\.org/", "", str(a["doi"]).strip(), flags=_re.I)
    import os
    email = a.get("email") or os.getenv("UNPAYWALL_EMAIL") or EMAIL
    r = await http_get(f"https://api.unpaywall.org/v2/{quote(doi, safe='')}?email={email}")
    j = json_loose(r["body"])
    if r["status"] == 404:
        return empty("unpaywall", f"DOI {doi} tidak ada di Unpaywall")
    if not j or "doi" not in j:
        return failed("unpaywall", f"HTTP {r['status']}")
    best = j.get("best_oa_location") or {}
    return ok("unpaywall", [std(
        title=j.get("title"),
        authors=[((x.get("given") or "") + " " + (x.get("family") or "")).strip() for x in (j.get("z_authors") or [])],
        year=j.get("year"), doi=j.get("doi"), venue=j.get("journal_name"), abstract=None,
        url=best.get("url_for_landing_page") or f"https://doi.org/{j['doi']}",
        pdf=best.get("url_for_pdf") or best.get("url"),
        source="unpaywall",
        extra={"oa_status": j.get("oa_status"), "license": best.get("license"), "is_paratext": j.get("is_paratext")},
    )])


async def _orcid_works(a: dict) -> dict:
    n = min(a.get("limit", 15), 50)
    from urllib.parse import quote
    r = await http_get(f"https://pub.orcid.org/v3.0/{quote(a['orcid'].strip(), safe='')}/works",
                       headers={"Accept": "application/json"})
    j = json_loose(r["body"])
    if not j or "group" not in j:
        return failed("orcid", f"HTTP {r['status']} — cek format ORCID iD")
    items = []
    for g in j["group"][:n]:
        w = (g.get("work-summary") or [{}])[0]
        ext = next((x for x in ((w.get("external-ids") or {}).get("external-id") or [])
                    if x.get("external-id-type") == "doi"), None)
        items.append(std(
            title=((w.get("title") or {}).get("title") or {}).get("value"),
            authors=[], year=((w.get("publication-date") or {}).get("year") or {}).get("value"),
            doi=ext.get("external-id-value") if ext else None,
            venue=(w.get("journal-title") or {}).get("value"),
            url=(ext.get("external-id-url") or {}).get("value") if ext else None,
            source="orcid", extra={"put_code": w.get("put-code"), "type": w.get("type")},
        ))
    items = [i for i in items if i]
    return ok("orcid", items) if items else empty("orcid", "ORCID ini belum punya work publik")


async def _pwc_search(a: dict) -> dict:
    n = min(a.get("limit", 5), 20)
    from urllib.parse import quote
    candidates = [
        f"https://paperswithcode.co/api/v1/papers/?q={quote(a['query'], safe='')}&limit={n}",
        f"https://paperswithcode.co/api/v1/search/?q={quote(a['query'], safe='')}",
        f"https://api.paperswithcode.com/api/v1/papers/?q={quote(a['query'], safe='')}&limit={n}",
    ]
    for url in candidates:
        r = await http_get(url)
        j = json_loose(r["body"])
        rows = j.get("results") or j.get("papers") if isinstance(j, dict) else None
        if not r["ok"] or not isinstance(rows, list):
            continue
        items = [std(
            title=p.get("paper_title") or p.get("title"),
            authors=[], year=int(str(p.get("published"))[:4]) if p.get("published") else None,
            doi=p.get("doi"), venue=None, abstract=p.get("abstract"),
            url=p.get("url_abs") or p.get("url"), pdf=p.get("url_pdf"), source="paperswithcode",
            extra={"code_links": [c.get("url") for c in (p.get("codes") or [])],
                   "tasks": [t.get("name") or t.get("id") for t in (p.get("tasks") or [])]},
        ) for p in rows[:n]]
        items = [i for i in items if i]
        if items:
            return ok("paperswithcode", items, {"endpoint": url})
        if rows == []:
            return empty("paperswithcode")
    return blocked("paperswithcode", "Semua endpoint API rehost tidak ditemukan/berubah (404). Cek https://paperswithcode.co/docs/api atau pakai semantic_scholar_search.")


CONNECTOR = {
    "id": "free-pack",
    "label": "Free connectors (OpenAlex, Crossref, arXiv, DOAJ, Semantic Scholar, OpenReview, INSPIRE-HEP, ERIC, Unpaywall, ORCID, Papers with Code)",
    "category": "free",
    "auth_env": None,
    "auth_required": False,
    "homepage": "https://openalex.org",
    "note": "API publik terbuka tanpa key. Probe live 14 Nov 2026: OK kecuali S2 (429 tanpa key, wajar) dan PwC (endpoint rehost beta).",
    "tools": [
        {"name": "openalex_search", "description": "Cari paper via OpenAlex (open scholarly metadata, citation graph, OA locations). Free, tanpa API key (budget harian bersama per IP; OPENALEX_API_KEY opsional menaikkan budget).", "input_schema": _search_schema(), "handler": _openalex_search},
        {"name": "crossref_search", "description": "Cari metadata publikasi via Crossref (DOI registry). Free, tanpa API key.", "input_schema": {**_search_schema(), "properties": {**_search_schema()["properties"], "filter": {"type": "string", "description": "Filter Crossref opsional, mis. 'type:journal-article'"}}}, "handler": _crossref_search},
        {"name": "crossref_doi", "description": "Ambil metadata lengkap satu publikasi berdasarkan DOI via Crossref.", "input_schema": {"type": "object", "properties": {"doi": {"type": "string", "description": "DOI, mis. 10.1038/nature12373"}}, "required": ["doi"], "additionalProperties": False}, "handler": _crossref_doi},
        {"name": "arxiv_search", "description": "Cari preprint di arXiv (Atom API). Free. Trik query: 'cat:cs.CL AND all:reward' untuk filter kategori.", "input_schema": _search_schema(), "handler": _arxiv_search},
        {"name": "doaj_search", "description": "Cari artikel open-access terkurasi di DOAJ. Free, tanpa API key.", "input_schema": _search_schema(), "handler": _doaj_search},
        {"name": "semantic_scholar_search", "description": "Cari paper via Semantic Scholar. Free tapi rate-limit ketat tanpa key — kalau 429, pakai openalex_search sebagai fallback.", "input_schema": _search_schema(), "handler": _semantic_scholar_search},
        {"name": "openreview_search", "description": "Cari submission + peer review di OpenReview (API v2). Free. Berguna untuk melihat proses evaluasi, bukan hanya paper final.", "input_schema": _search_schema(), "handler": _openreview_search},
        {"name": "openreview_notes", "description": "Ambil semua note publik satu forum OpenReview — abstrak, reviews, rebuttals, meta-review, decision.", "input_schema": {"type": "object", "properties": {"forum": {"type": "string", "description": "Forum id OpenReview"}}, "required": ["forum"], "additionalProperties": False}, "handler": _openreview_notes},
        {"name": "inspire_search", "description": "Cari literatur HEP/particle physics di INSPIRE-HEP. Free, tanpa API key. Query pakai sintaks INSPIRE: find a higgs, find t 'title'.", "input_schema": _search_schema(), "handler": _inspire_search},
        {"name": "eric_search", "description": "Cari literatur pendidikan/pedagogi di ERIC (public API Dept of Education US). Free, tanpa API key.", "input_schema": _search_schema(), "handler": _eric_search},
        {"name": "unpaywall_resolve", "description": "Cari lokasi full-text open-access untuk satu DOI via Unpaywall (OA location, license, repository).", "input_schema": {"type": "object", "properties": {"doi": {"type": "string"}, "email": {"type": "string", "description": "Email opsional (default identitas politeness skill)"}}, "required": ["doi"], "additionalProperties": False}, "handler": _unpaywall_resolve},
        {"name": "orcid_works", "description": "Ambil daftar publikasi satu peneliti via ORCID public API (by ORCID iD).", "input_schema": {"type": "object", "properties": {"orcid": {"type": "string", "description": "ORCID iD, mis. 0000-0002-1825-0097"}, "limit": {"type": "integer", "minimum": 1, "maximum": 50, "default": 15}}, "required": ["orcid"], "additionalProperties": False}, "handler": _orcid_works},
        {"name": "pwc_search", "description": "Cari paper + source code + dataset + leaderboard (Papers with Code, rehost komunitas, API beta). Bisa gagal bila endpoint berubah — error disertai saran.", "input_schema": _search_schema(), "handler": _pwc_search},
    ],
}
