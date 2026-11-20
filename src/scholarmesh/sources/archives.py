# archives.py — repositori & agregator open-access (Zenodo, DataCite, OSF, OpenAIRE,
# CORE) + resolusi OA Unpaywall. Probe 21 Nov 2026: zenodo/datacite/osf/openaire OK
# tanpa key; CORE 429 tanpa key (free registration) → auth-gated via CORE_API_KEY.

from __future__ import annotations

import os

from ..core import (auth_required, empty, failed, http_get, json_loose, ok, std)

EMAIL = "scholarmesh@users.noreply.github.com"

DOI_SCHEMA = {
    "type": "object",
    "properties": {
        "doi": {"type": "string", "description": "DOI, mis. 10.1038/nature12373"},
        "email": {"type": "string", "description": "Email opsional (default identitas politeness server)"},
    },
    "required": ["doi"],
    "additionalProperties": False,
}

SEARCH_SCHEMA = {
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


async def _unpaywall_resolve(a: dict) -> dict:
    import re as _re
    from urllib.parse import quote
    doi = _re.sub(r"^https?://(dx\.)?doi\.org/", "", str(a["doi"]).strip(), flags=_re.I)
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


async def _zenodo_search(a: dict) -> dict:
    n = min(a.get("limit", 5), 25)
    from urllib.parse import quote
    r = await http_get(f"https://zenodo.org/api/records?q={quote(a['query'], safe='')}&size={n}", timeout=20)
    j = json_loose(r["body"])
    rows = ((j or {}).get("hits") or {}).get("hits") or []
    if not isinstance(rows, list):
        return failed("zenodo", f"HTTP {r['status']} {r['body'][:150]}")
    items = []
    for x in rows:
        md = x.get("metadata") or {}
        files = x.get("files") or []
        items.append(std(
            title=x.get("title") or md.get("title"),
            authors=[c.get("name") for c in (md.get("creators") or [])],
            year=int(str(md.get("publication_date"))[:4]) if md.get("publication_date") else None,
            doi=x.get("doi") or md.get("doi"),
            venue="Zenodo",
            abstract=x.get("description") or md.get("description"),
            url=x.get("doi_url") or (x.get("links") or {}).get("self_html"),
            pdf=(files[0].get("links") or {}).get("self") if files else None,
            source="zenodo",
            extra={"recid": x.get("recid") or x.get("id"), "resource_type": (md.get("resource_type") or {}).get("title")},
        ))
    items = [i for i in items if i]
    return ok("zenodo", items, {"total": ((j.get("hits") or {}).get("total"))}) if items else empty("zenodo")


async def _datacite_search(a: dict) -> dict:
    n = min(a.get("limit", 5), 25)
    from urllib.parse import quote
    r = await http_get(f"https://api.datacite.org/dois?query={quote(a['query'], safe='')}&page%5Bsize%5D={n}", timeout=20)
    j = json_loose(r["body"])
    rows = (j or {}).get("data") or []
    if not isinstance(rows, list):
        return failed("datacite", f"HTTP {r['status']} {r['body'][:150]}")
    items = []
    for d in rows:
        at = d.get("attributes") or {}
        desc = next((x.get("description") for x in (at.get("descriptions") or [])
                     if x.get("description")), None)
        items.append(std(
            title=(at.get("titles") or [{}])[0].get("title"),
            authors=[c.get("name") for c in (at.get("creators") or [])],
            year=at.get("publicationYear"),
            doi=at.get("doi"),
            venue=at.get("publisher"),
            abstract=desc,
            url=at.get("url") or (f"https://doi.org/{at['doi']}" if at.get("doi") else None),
            source="datacite",
            extra={"publisher": at.get("publisher"), "types": (at.get("types") or {}).get("resourceTypeGeneral")},
        ))
    items = [i for i in items if i]
    return ok("datacite", items, {"total": (j or {}).get("meta", {}).get("total")}) if items else empty("datacite")


async def _osf_search(a: dict) -> dict:
    n = min(a.get("limit", 5), 25)
    from urllib.parse import quote
    kind = a.get("kind", "preprints")
    if kind == "nodes":
        url = f"https://api.osf.io/v2/nodes/?filter%5Btitle%5D={quote(a['query'], safe='')}&page%5Bsize%5D={n}"
    else:
        url = f"https://api.osf.io/v2/preprints/?filter%5Btitle%5D={quote(a['query'], safe='')}&page%5Bsize%5D={n}"
    r = await http_get(url, timeout=20)
    j = json_loose(r["body"])
    rows = (j or {}).get("data") or []
    if not isinstance(rows, list):
        return failed("osf", f"HTTP {r['status']} {r['body'][:150]}")
    items = []
    for d in rows:
        at = d.get("attributes") or {}
        items.append(std(
            title=at.get("title"),
            authors=[],  # contributors butuh request per-item — biarkan kosong, jujur
            year=int(str(at.get("date_published"))[:4]) if at.get("date_published") else None,
            doi=at.get("doi"),
            venue="OSF" if kind == "nodes" else "OSF Preprints",
            abstract=at.get("description"),
            url=(d.get("links") or {}).get("html"),
            pdf=None,
            source="osf",
            extra={"kind": kind, "osf_id": d.get("id")},
        ))
    items = [i for i in items if i]
    return ok("osf", items, {"kind": kind}) if items else empty("osf", f"0 hasil '{a['query']}' (filter[title] = substring judul)")


async def _openaire_search(a: dict) -> dict:
    n = min(a.get("limit", 5), 25)
    from urllib.parse import quote
    r = await http_get(f"https://api.openaire.eu/graph/v1/researchProducts?search={quote(a['query'], safe='')}&pageSize={n}", timeout=20)
    j = json_loose(r["body"])
    rows = (j or {}).get("results") or []
    if not isinstance(rows, list):
        return failed("openaire", f"HTTP {r['status']} {r['body'][:150]}")
    items = []
    for x in rows:
        doi = x.get("doi")
        year = int(str(x.get("publicationDate"))[:4]) if x.get("publicationDate") else x.get("publicationYear")
        items.append(std(
            title=x.get("mainTitle"),
            authors=x.get("authors") or [],
            year=year,
            doi=doi,
            venue=x.get("publisher"),
            abstract=x.get("description"),
            url=f"https://doi.org/{doi}" if doi else x.get("websiteURL"),
            source="openaire",
            extra={"type": x.get("type"), "open_access": x.get("openAccessColor")},
        ))
    items = [i for i in items if i]
    return ok("openaire", items, {"total": ((j.get("header") or {}).get("numFound"))}) if items else empty("openaire")


async def _core_search(a: dict) -> dict:
    if not os.getenv("CORE_API_KEY"):
        return auth_required("core", "CORE_API_KEY",
                             "CORE API v3 butuh key — registrasi gratis di core.ac.uk (integrasi 400M+ works, full-text terdalam setelah OpenAlex).")
    n = min(a.get("limit", 5), 25)
    from urllib.parse import quote
    r = await http_get(f"https://api.core.ac.uk/v3/search/works?q={quote(a['query'], safe='')}&limit={n}",
                       headers={"Authorization": f"Bearer {os.environ['CORE_API_KEY']}"}, timeout=20)
    j = json_loose(r["body"])
    rows = (j or {}).get("results") or []
    if not isinstance(rows, list):
        return failed("core", f"HTTP {r['status']} {r['body'][:150]}")
    items = []
    for x in rows:
        doi = x.get("doi")
        items.append(std(
            title=x.get("title"),
            authors=[c.get("name") for c in (x.get("authors") or []) if isinstance(c, dict)] or x.get("authors") or [],
            year=x.get("yearPublished"),
            doi=doi,
            venue=(x.get("publisher") or "") or None,
            abstract=x.get("abstract"),
            url=x.get("downloadUrl") or x.get("sourceFulltextUrl") or (f"https://doi.org/{doi}" if doi else None),
            pdf=x.get("downloadUrl"),
            source="core",
            extra={"core_id": x.get("id"), "full_text": bool(x.get("fullText"))},
        ))
    items = [i for i in items if i]
    return ok("core", items, {"total": (j or {}).get("totalHits")}) if items else empty("core")


SOURCES = [
    {
        "id": "unpaywall", "label": "Unpaywall (OA location resolver per DOI)",
        "category": "free", "auth_env": "UNPAYWALL_EMAIL", "auth_required": False,
        "disciplines": ["multidisciplinary"], "countries": [],
        "homepage": "https://unpaywall.org",
        "note": "Resolver: satu DOI → lokasi OA + lisensi. UNPAYWALL_EMAIL opsional (politeness).",
        "tools": [{"name": "unpaywall_resolve", "description": "Cari lokasi full-text open-access untuk satu DOI via Unpaywall (OA location, license, repository).", "input_schema": DOI_SCHEMA, "handler": _unpaywall_resolve}],
    },
    {
        "id": "zenodo", "label": "Zenodo (datasets, software, preprints — CERN)",
        "category": "free", "auth_env": None, "auth_required": False,
        "disciplines": ["multidisciplinary"], "countries": [],
        "homepage": "https://zenodo.org",
        "note": "Records campuran (dataset/software/preprint) — cek resource_type di extra.",
        "tools": [{"name": "zenodo_search", "description": "Cari records di Zenodo (datasets, software, preprints dari CERN). Free, tanpa key.", "input_schema": SEARCH_SCHEMA, "handler": _zenodo_search}],
    },
    {
        "id": "datacite", "label": "DataCite (DOI registry untuk datasets/software)",
        "category": "free", "auth_env": None, "auth_required": False,
        "disciplines": ["multidisciplinary"], "countries": [],
        "homepage": "https://datacite.org",
        "note": "DOI non-artikel (dataset/software/MPG). 142M+ records via API.",
        "tools": [{"name": "datacite_search", "description": "Cari DOI records di DataCite (datasets, software, GIFs; registry DOI alternatif Crossref). Free, tanpa key.", "input_schema": SEARCH_SCHEMA, "handler": _datacite_search}],
    },
    {
        "id": "osf", "label": "OSF (preprints + project nodes)",
        "category": "free", "auth_env": None, "auth_required": False,
        "disciplines": ["multidisciplinary"], "countries": [],
        "homepage": "https://osf.io",
        "note": "Preprints endpoint mencakup SocArXiv, PsyArXiv, engrXiv, dsb.",
        "tools": [{"name": "osf_search", "description": "Cari preprints (default) atau project nodes di Open Science Framework. Free, tanpa key. filter[title] = substring judul.", "input_schema": {**SEARCH_SCHEMA, "properties": {**SEARCH_SCHEMA["properties"], "kind": {"type": "string", "enum": ["preprints", "nodes"], "description": "Cari preprints (default) atau project nodes"}}}, "handler": _osf_search}],
    },
    {
        "id": "openaire", "label": "OpenAIRE Graph (EU aggregator, 150M+ products)",
        "category": "free", "auth_env": None, "auth_required": False,
        "disciplines": ["multidisciplinary"], "countries": [],
        "homepage": "https://graph.openaire.eu",
        "note": "Agregasi repository Eropa + Global South; kuat buat proyek EU-funded.",
        "tools": [{"name": "openaire_search", "description": "Cari research products (publikasi, dataset, software) di OpenAIRE Graph. Free, tanpa key.", "input_schema": SEARCH_SCHEMA, "handler": _openaire_search}],
    },
    {
        "id": "core", "label": "CORE (OA aggregator, 400M+ works claim)",
        "category": "key", "auth_env": "CORE_API_KEY", "auth_required": True,
        "disciplines": ["multidisciplinary"], "countries": [],
        "homepage": "https://core.ac.uk",
        "note": "Registrasi key GRATIS di core.ac.uk; free tier rate-limit longgar (batch 1 req/10s).",
        "tools": [{"name": "core_search", "description": "Cari works open-access di CORE (agregator repository global; full-text terdalam setelah OpenAlex). WAJIB CORE_API_KEY — registrasi gratis.", "input_schema": SEARCH_SCHEMA, "handler": _core_search}],
    },
]
