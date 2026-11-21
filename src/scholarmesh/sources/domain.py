# domain.py — sumber domain-specific: INSPIRE-HEP (physics), ERIC (education),
# zbMATH Open (math), ProofWiki (math proofs), Papers with Code (CS+code),
# Europe PMC + PubMed (biomed, full-text), NASA ADS (astro).
# Handler inspire/eric/pwc/ads verbatim dari free.py/premium.py lama; zbmath/
# europepmc/pubmed baru — probes 21 Nov 2026 (semua 200 tanpa key; CORE 429 → gated).

from __future__ import annotations

import os
import re
from urllib.parse import quote

from ..core import (auth_required, blocked, empty, failed, http_get, json_loose,
                    ok, std, strip_html)

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


async def _zbmath_search(a: dict) -> dict:
    n = min(a.get("limit", 5), 25)
    from urllib.parse import quote
    r = await http_get(f"https://api.zbmath.org/v1/document/_search?search_string={quote(a['query'], safe='')}&results_per_page={n}", timeout=20)
    j = json_loose(r["body"])
    rows = (j or {}).get("result") or []
    if not isinstance(rows, list):
        return failed("zbmath", f"HTTP {r['status']} {r['body'][:150]}")
    items = []
    for x in rows:
        # identifier bisa list of dict {type,id} ATAU list of string DOI (variasi respons API).
        doi = None
        for i in (x.get("identifier") or []):
            if isinstance(i, dict) and i.get("type") == "doi":
                doi = i.get("id")
                break
            if isinstance(i, str) and "/" in i and doi is None:
                doi = i
        items.append(std(
            title=(x.get("titles") or [{}])[0].get("title"),
            authors=[a.get("name") for a in ((x.get("contributors") or {}).get("authors") or [])],
            year=int(str(x.get("year"))[:4]) if x.get("year") else (int(str(x.get("datestamp"))[:4]) if x.get("datestamp") else None),
            doi=doi,
            venue=str(x.get("source"))[:200] or None,
            abstract=(x.get("abstracts") or [{}])[0].get("text") or None,
            url=f"https://doi.org/{doi}" if doi else (f"https://zbmath.org/?q=an%3A{x.get('id')}" if x.get("id") else None),
            pdf=None,
            source="zbmath",
            extra={"zbmath_id": x.get("id"), "document_type": (x.get("document_type") or {}).get("description"),
                   "msc": [m.get("code") for m in (x.get("msc") or [])[:3]]},
        ))
    items = [i for i in items if i]
    return ok("zbmath", items, {"total": (j or {}).get("numFound")}) if items else empty("zbmath")


async def _europepmc_search(a: dict) -> dict:
    n = min(a.get("limit", 5), 25)
    from urllib.parse import quote
    r = await http_get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={quote(a['query'], safe='')}&format=json&pageSize={n}", timeout=20)
    j = json_loose(r["body"])
    if not j or "resultList" not in j:
        return failed("europepmc", f"HTTP {r['status']} {r['body'][:150]}")
    rows = ((j.get("resultList") or {}).get("result")) or []
    items = []
    for x in rows:
        pmid = x.get("pmid") or x.get("id")
        items.append(std(
            title=x.get("title"),
            authors=[s.strip() for s in (x.get("authorString") or "").split(",") if s.strip()],
            year=int(x["pubYear"]) if str(x.get("pubYear") or "").isdigit() else None,
            doi=x.get("doi"),
            venue=x.get("journalTitle"),
            abstract=x.get("abstractText"),
            url=f"https://europepmc.org/article/{x.get('source') or 'MED'}/{pmid}" if pmid else None,
            pdf=None,
            source="europepmc",
            extra={"pmcid": x.get("pmcid"), "pmid": x.get("pmid"), "is_open_access": x.get("isOpenAccess"),
                   "in_europepmc": x.get("inEPMC"), "cited_by_count": x.get("citedByCount")},
        ))
    items = [i for i in items if i]
    return ok("europepmc", items, {"total": (j or {}).get("hitCount")}) if items else empty("europepmc")


async def _europepmc_fulltext(a: dict) -> dict:
    # Validasi ketat: pmcid hanya PMC\d+ — host tetap europepmc.org, tidak ada URL dari user.
    if not re.fullmatch(r"PMC\d+", str(a["pmcid"]).strip(), re.I):
        return failed("europepmc", "pmcid harus berbentuk PMC1234567 (cari dulu via europepmc_search, ambil extra.pmcid)")
    pmcid = str(a["pmcid"]).strip().upper()
    r = await http_get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML", timeout=25)
    if r["status"] == 404:
        return empty("europepmc", f"{pmcid} tidak punya full-text OA di Europe PMC (cek extra.in_europepmc di hasil search)")
    body = r["body"]
    if not body or body.lstrip().startswith("<error"):
        return blocked("europepmc", f"Full-text XML tidak tersedia (HTTP {r['status']}). Manual: https://europepmc.org/article/{pmcid}")
    text = strip_html(body)
    title_m = re.search(r"<article-title[^>]*>([\s\S]*?)</article-title>", body)
    extra = {"pmcid": pmcid, "fulltext": text[:40000], "source_xml": r["status"], "bytes": len(body)}
    if len(text) > 40000:
        extra["note"] = "fulltext truncated at 40000 chars"
    item = std(
        title=strip_html(title_m.group(1)) if title_m else pmcid,
        authors=[], year=None, doi=None, venue="Europe PMC (OA full text)", abstract=None,
        url=f"https://europepmc.org/article/{pmcid}",
        source="europepmc",
        extra=extra,
    )
    return ok("europepmc", [item], {"license_note": "JATS XML dari Europe PMC OA subset — hormati lisensi penerbit saat mengutip"})


async def _pubmed_search(a: dict) -> dict:
    n = min(a.get("limit", 5), 25)
    import os as _os
    from urllib.parse import quote
    key = f"&api_key={_os.environ['NCBI_API_KEY']}" if _os.getenv("NCBI_API_KEY") else ""
    r1 = await http_get(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={quote(a['query'], safe='')}&retmode=json&retmax={n}{key}", timeout=20)
    j1 = json_loose(r1["body"])
    ids = ((j1 or {}).get("esearchresult") or {}).get("idlist") or []
    if not ids:
        if (j1 or {}).get("esearchresult", {}).get("count") == "0":
            return empty("pubmed")
        return failed("pubmed", f"esearch HTTP {r1['status']} {r1['body'][:150]}")
    r2 = await http_get(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={','.join(ids)}&retmode=json{key}", timeout=20)
    j2 = json_loose(r2["body"])
    res = (j2 or {}).get("result") or {}
    items = []
    for uid in res.get("uids") or ids:
        d = res.get(uid) or {}
        doi = next((x.get("value") for x in (d.get("articleids") or []) if x.get("idtype") == "doi"), None)
        year = str(d.get("pubdate") or d.get("epubdate") or "")[:4]
        items.append(std(
            title=d.get("title"),
            authors=[x.get("name") for x in (d.get("authors") or [])],
            year=int(year) if year.isdigit() else None,
            doi=doi,
            venue=d.get("fulljournalname") or d.get("source"),
            abstract=None,  # esummary tidak membawa abstract — jujur; ambil via europepmc_fulltext bila OA
            url=f"https://pubmed.ncbi.nlm.nih.gov/{uid}/",
            source="pubmed",
            extra={"pmid": uid, "pub_types": d.get("pubtype")},
        ))
    items = [i for i in items if i]
    return ok("pubmed", items, {"total": (j1["esearchresult"]).get("count"), "ncbi_key_used": bool(_os.getenv("NCBI_API_KEY"))}) if items else empty("pubmed")


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


async def _whoiris_search(a: dict) -> dict:
    # WHO IRIS (Institutional Repository for Information Sharing) — DSpace 7 REST,
    # gratis tanpa key (probes 21 Nov 2026: 200). Pola parsing identik brin_search.
    n = min(a.get("limit", 5), 20)
    q = quote(a["query"], safe="")
    r = await http_get(f"https://iris.who.int/server/api/discover/search/objects?query={q}&size={n}",
                       timeout=20, headers={"Accept": "application/json"})
    try:
        j = json_loose(r["body"]) or {}
    except Exception:
        j = {}
    objects = (((j.get("_embedded") or {}).get("searchResult") or {}).get("_embedded") or {}).get("objects") or []
    if not objects and r["status"] != 200:
        return failed("whoiris", f"HTTP {r['status']} {r['body'][:150]}")
    items = []
    for o in objects:
        m = (o.get("_embedded") or {}).get("indexableObject") or {}
        md = lambda k: ((m.get("metadata") or {}).get(k) or [{}])[0].get("value")  # noqa: E731
        issued = md("dc.date.issued")
        items.append(std(
            title=md("dc.title"),
            authors=[x.get("value") for x in (m.get("metadata") or {}).get("dc.contributor.author") or []],
            year=int(str(issued)[:4]) if issued else None,
            doi=md("dc.identifier.doi"),
            venue="WHO IRIS",
            abstract=md("dc.description.abstract"),
            url=md("dc.identifier.uri") or (f"https://iris.who.int/items/{m.get('uuid')}" if m.get("uuid") else None),
            source="whoiris",
            extra={"type": md("dc.type")},
        ))
    items = [i for i in items if i]
    return ok("whoiris", items) if items else empty("whoiris")


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


async def _proofwiki_search(a: dict) -> dict:
    n = min(a.get("limit", 5), 25)
    q = quote(a["query"], safe="")
    r = await http_get(f"https://proofwiki.org/api.php?action=query&list=search&srsearch={q}&srlimit={n}&format=json&formatversion=2")
    if r["status"] in (403, 429, 503) or _cf(r["body"]):
        return blocked("proofwiki", f"Cloudflare/bot-wall di proofwiki.org (HTTP {r['status']}). "
                                    f"Fallback manual: buka https://proofwiki.org/wiki/Special:Search?search={q} di browser, "
                                    "lalu pakai proofwiki_get dengan judul halaman yang ketemu.")
    j = json_loose(r["body"])
    if not j or "query" not in j:
        return failed("proofwiki", f"HTTP {r['status']} — respons bukan JSON API MediaWiki {r['error'] or ''}")
    hits = (j.get("query") or {}).get("search") or []
    items = [
        std(
            title=h.get("title"),
            authors=[], year=None, doi=None, venue="ProofWiki",
            abstract=strip_html(h.get("snippet")),
            url=SITE + quote(str(h.get("title") or "").replace(" ", "_"), safe=":/"),
            source="proofwiki",
            extra={"page_id": h.get("pageid"), "ns": h.get("ns"),
                   "wordcount": h.get("wordcount"), "last_edit": h.get("timestamp")},
        )
        for h in hits
    ]
    return ok("proofwiki", items, {
        "totalhits": ((j.get("query") or {}).get("searchinfo") or {}).get("totalhits"),
        "license": LICENSE,
    }) if items else empty("proofwiki")


async def _proofwiki_get(a: dict) -> dict:
    title = str(a["page"]).strip().replace(" ", "_")
    r = await http_get(
        f"https://proofwiki.org/api.php?action=query&prop=revisions&rvslots=main&rvprop=content&redirects=1"
        f"&titles={quote(title, safe=':' + '/')}&format=json&formatversion=2",
        timeout=20,
    )
    if r["status"] in (403, 429, 503) or _cf(r["body"]):
        return blocked("proofwiki", f"Cloudflare/bot-wall di proofwiki.org (HTTP {r['status']}). "
                                    f"Fallback manual: buka {SITE}{title} di browser.")
    j = json_loose(r["body"])
    pages = ((j or {}).get("query") or {}).get("pages") or []
    if not pages:
        return empty("proofwiki", f"Halaman tidak terbaca (HTTP {r['status']}). Cari judul persis dulu via proofwiki_search.")
    p = pages[0]
    if "missing" in p:
        return empty("proofwiki", f"Halaman '{p.get('title') or a['page']}' tidak ada di ProofWiki. "
                                  "Cari judul persis dulu via proofwiki_search (judul sering memakai 'Definition:' / 'Category:').")
    rev = (p.get("revisions") or [{}])[0]
    content = ((rev.get("slots") or {}).get("main") or {}).get("content") or rev.get("*")
    if not content:
        return failed("proofwiki", "Wikitext tidak tersedia pada respons API.")
    extra: dict = {"page_id": p.get("pageid"), "last_edit": rev.get("timestamp"),
                   "wikitext": content, "license": LICENSE,
                   "attribution": f"Sumber: ProofWiki — {SITE}{quote(str(p.get('title') or title), safe=':/')} ({LICENSE})"}
    if len(content) > 40000:
        extra["wikitext"] = content[:40000] + "\n\n… [terpotong di 40000 karakter; sisanya via URL halaman]"
        extra["note"] = "wikitext truncated at 40000 chars"
    item = std(
        title=p.get("title") or a["page"],
        authors=[], year=None, doi=None, venue="ProofWiki", abstract=None,
        url=SITE + quote(str(p.get("title") or title).replace(" ", "_"), safe=":/"),
        source="proofwiki",
        extra=extra,
    )
    return ok("proofwiki", [item], {"license": LICENSE})


API = "https://proofwiki.org/api.php"
SITE = "https://proofwiki.org/wiki/"
LICENSE = "CC BY-SA 3.0 / GFDL dual-license — attribution required"

_CF_RE = re.compile(
    r"just a moment|challenge-platform|cf-browser-verification"
    r"|enable javascript and cookies|checking your browser",
    re.I,
)


def _cf(body: str) -> bool:
    return bool(_CF_RE.search(body or ""))


SOURCES = [
    {
        "id": "inspirehep", "label": "INSPIRE-HEP (high-energy physics literature)",
        "category": "free", "auth_env": None, "auth_required": False,
        "disciplines": ["physics"], "countries": [],
        "homepage": "https://inspirehep.net",
        "note": "Kurasi komunitas HEP; sintaks query sendiri (find a higgs).",
        "tools": [{"name": "inspire_search", "description": "Cari literatur HEP/particle physics di INSPIRE-HEP. Free, tanpa API key. Query pakai sintaks INSPIRE: find a higgs, find t 'title'.", "input_schema": SEARCH_SCHEMA, "handler": _inspire_search}],
    },
    {
        "id": "eric", "label": "ERIC (education literature, US Dept of Education)",
        "category": "free", "auth_env": None, "auth_required": False,
        "disciplines": ["education"], "countries": [],
        "homepage": "https://eric.ed.gov",
        "note": "Publik API Department of Education US.",
        "tools": [{"name": "eric_search", "description": "Cari literatur pendidikan/pedagogi di ERIC (public API Dept of Education US). Free, tanpa API key.", "input_schema": SEARCH_SCHEMA, "handler": _eric_search}],
    },
    {
        "id": "zbmath", "label": "zbMATH Open (math reviews, ~5M records, MSC codes)",
        "category": "free", "auth_env": None, "auth_required": False,
        "disciplines": ["mathematics"], "countries": [],
        "homepage": "https://zbmath.org",
        "note": "Review matematis + klasifikasi MSC; Free API.",
        "tools": [{"name": "zbmath_search", "description": "Cari literatur matematika di zbMATH Open (reviews + kode klasifikasi MSC). Free, tanpa key. Contoh query: 'ricci flow', 'MR' juga bisa.", "input_schema": SEARCH_SCHEMA, "handler": _zbmath_search}],
    },
    {
        "id": "proofwiki", "label": "ProofWiki (definitions, theorems, complete proofs)",
        "category": "bot-wall", "auth_env": None, "auth_required": False,
        "disciplines": ["mathematics"], "countries": [],
        "homepage": "https://proofwiki.org",
        "note": "MediaWiki API gratis; Cloudflare-fronted — dari jaringan tertentu kena challenge (blocked). Konten CC BY-SA 3.0/GFDL — atribusi wajib.",
        "tools": [
            {"name": "proofwiki_search", "description": "Cari teorema/definisi/bukti matematika di ProofWiki (proofwiki.org). Gratis via MediaWiki API, tapi bisa kena Cloudflare bot-wall (envelope blocked + saran manual).", "input_schema": SEARCH_SCHEMA, "handler": _proofwiki_search},
            {"name": "proofwiki_get", "description": "Ambil wikitext lengkap satu halaman ProofWiki (teorema/definisi/bukti) by judul. Wikitext berisi wikilink ke definisi & lema prasyarat. Bisa kena Cloudflare (blocked).", "input_schema": {"type": "object", "properties": {"page": {"type": "string", "description": "Judul halaman persis, mis. 'Pythagorean Theorem' atau 'Definition:Metric Space'"}}, "required": ["page"], "additionalProperties": False}, "handler": _proofwiki_get},
        ],
    },
    {
        "id": "paperswithcode", "label": "Papers with Code (papers + code links, rehost beta)",
        "category": "bot-wall", "auth_env": None, "auth_required": False,
        "disciplines": ["computer-science"], "countries": [],
        "homepage": "https://paperswithcode.co",
        "note": "API rehost komunitas (endpoint asli mati) — best-effort.",
        "tools": [{"name": "pwc_search", "description": "Cari paper + source code + dataset + leaderboard (Papers with Code, rehost komunitas, API beta). Bisa gagal bila endpoint berubah — error disertai saran.", "input_schema": SEARCH_SCHEMA, "handler": _pwc_search}],
    },
    {
        "id": "europepmc", "label": "Europe PMC (biomed/life sciences, 49M+ records, OA full-text XML)",
        "category": "free", "auth_env": None, "auth_required": False,
        "disciplines": ["medicine", "life-sciences"], "countries": [],
        "homepage": "https://europepmc.org",
        "note": "Termasuk OA full-text JATS XML (ganti PMC oa.fcgi yang pensiun 2025).",
        "tools": [
            {"name": "europepmc_search", "description": "Cari biomed/life-sciences di Europe PMC (49M+ records: PubMed, PMC, Agricola, preprints). Free, tanpa key. extra.pmcid → pakai europepmc_fulltext bila in_europepmc=Y.", "input_schema": SEARCH_SCHEMA, "handler": _europepmc_search},
            {"name": "europepmc_fulltext", "description": "Ambil full-text JATS XML (strip jadi teks) satu artikel OA dari Europe PMC by PMCID. Gratis. 404 = artikel bukan subset OA.", "input_schema": {"type": "object", "properties": {"pmcid": {"type": "string", "description": "PMCID, mis. PMC7159299 (dari extra.pmcid hasil europepmc_search)"}}, "required": ["pmcid"], "additionalProperties": False}, "handler": _europepmc_fulltext},
        ],
    },
    {
        "id": "pubmed", "label": "PubMed E-utilities (39M+ biomed citations, NCBI)",
        "category": "free", "auth_env": "NCBI_API_KEY", "auth_required": False,
        "disciplines": ["medicine", "life-sciences"], "countries": [],
        "homepage": "https://pubmed.ncbi.nlm.nih.gov",
        "note": "3 req/s anonim → 10 req/s dengan NCBI_API_KEY gratis (opsional).",
        "tools": [{"name": "pubmed_search", "description": "Cari sitasi biomed/medis di PubMed (NCBI E-utilities: esearch + esummary). Free; NCBI_API_KEY opsional menaikkan 3→10 req/s. Abstract tidak termasuk di esummary — pakai europepmc_fulltext untuk teks OA.", "input_schema": SEARCH_SCHEMA, "handler": _pubmed_search}],
    },
    {
        "id": "whoiris", "label": "WHO IRIS (global health publications, DSpace 7 REST)",
        "category": "free", "auth_env": None, "auth_required": False,
        "disciplines": ["medicine", "global-health", "public-health"], "countries": [],
        "homepage": "https://iris.who.int",
        "note": "Repository resmi WHO: laporan, guideline, jurnal global health.",
        "tools": [{"name": "whoiris_search", "description": "Cari publikasi global health di WHO IRIS (laporan, guideline, artikel; repository resmi WHO). Free, tanpa key.", "input_schema": SEARCH_SCHEMA, "handler": _whoiris_search}],
    },
    {
        "id": "ads", "label": "NASA ADS (astronomy & astrophysics)",
        "category": "key", "auth_env": "ADS_TOKEN", "auth_required": True,
        "disciplines": ["astronomy", "physics"], "countries": [],
        "homepage": "https://ui.adsabs.harvard.edu",
        "note": "Token gratis untuk peneliti.",
        "tools": [{"name": "ads_search", "description": "Cari paper astronomi/astrofisika di NASA ADS (metadata, citations, abstracts). WAJIB ADS_TOKEN (gratis untuk peneliti).", "input_schema": SEARCH_SCHEMA, "handler": _ads_search}],
    },
]
