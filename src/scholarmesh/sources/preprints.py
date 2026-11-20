# preprints.py — preprint servers & venue-specific paper indexes (arXiv, OpenReview,
# AlphaXiv, Hugging Face papers). Handler arxiv/openreview verbatim dari free.py lama;
# hfpapers connector baru (probe 21 Nov 2026: HF api papers/search OK, tanpa key).

from __future__ import annotations

import json
import os
import re

from ..core import (auth_required, empty, failed, http_get, json_loose, ok,
                    std, strip_html)

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


async def _openreview_search(a: dict) -> dict:
    n = min(a.get("limit", 5), 20)
    from urllib.parse import quote
    r = await http_get(f"https://api2.openreview.net/notes/search?term={quote(a['query'], safe='')}&limit={n * 2}")
    j = json_loose(r["body"])
    if not j or "notes" not in j:
        return failed("openreview", f"HTTP {r['status']}")
    items = []
    for nt in j["notes"]:
        c = nt.get("content") or {}

        def v(k):
            val = c.get(k)
            return val.get("value") if isinstance(val, dict) else val

        title = v("title")
        if not title:
            continue  # review-only notes (tanpa judul) masuk lewat openreview_notes, bukan search
        items.append(std(
            title=title, authors=v("authors") or [],
            year=(int(__import__("datetime").datetime.utcfromtimestamp(nt["pdate"]).year)
                  if nt.get("pdate") else (int(v("year")) if v("year") else None)),
            doi=None,
            venue=(nt.get("invitations") or [None])[0].split("/")[-2] if nt.get("invitations") else v("venue"),
            abstract=v("abstract"),
            url=f"https://openreview.net/forum?id={nt.get('forum') or nt.get('id')}",
            pdf=f"https://openreview.net/pdf?id={nt.get('forum') or nt.get('id')}" if v("pdf") else None,
            source="openreview",
            extra={"forum_id": nt.get("forum") or nt.get("id"), "rating": v("rating"), "keywords": v("keywords")},
        ))
    items = items[:n]
    return ok("openreview", items, {"note": "submission OpenReview (review/rebuttal via openreview_notes)"}) if items else empty("openreview")


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
        for k, val in (nt.get("content") or {}).items():
            value = val.get("value") if isinstance(val, dict) else val
            content[k] = clamp(value if isinstance(value, str) else json.dumps(value), 800)
        notes.append({
            "id": nt.get("id"), "invitations": nt.get("invitations"),
            "readers": "public" if "everyone" in (nt.get("readers") or []) else "restricted",
            **content,
        })
    items = [{**n, "title": n.get("title") or (n.get("invitations") or [None])[0], "source": "openreview"} for n in notes]
    return ok("openreview", items, {"forum": a["forum"], "count_raw": len(notes)})


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
        url=p.get("url") or (f"https://www.alphaxiv.org/abs/{p.get('arxiv_id')}" if p.get('arxiv_id') else None),
        pdf=p.get("pdf_url"), source="alphaxiv", extra={"arxiv_id": p.get("arxiv_id")},
    ) for p in rows[:n]]
    items = [i for i in items if i]
    return ok("alphaxiv", items) if items else empty("alphaxiv")


async def _hfpapers_search(a: dict) -> dict:
    # HF tidak punya param limit — respons bisa besar (probe 21 Nov 2026: 653 KB); slice di sisi kita.
    from urllib.parse import quote
    r = await http_get(f"https://huggingface.co/api/papers/search?q={quote(a['query'], safe='')}", timeout=25)
    j = json_loose(r["body"])
    if not isinstance(j, list):
        return failed("hfpapers", f"HTTP {r['status']} {r['body'][:150]}")
    n = min(a.get("limit", 5), 20)
    items = []
    for entry in j[:n]:
        p = entry.get("paper") or {}
        pid = p.get("id")
        items.append(std(
            title=p.get("title"),
            authors=[x.get("name") for x in (p.get("authors") or []) if isinstance(x, dict)],
            year=int(str(p.get("publishedAt"))[:4]) if p.get("publishedAt") else None,
            doi=None, venue="Hugging Face Papers",
            abstract=p.get("summary"),
            url=f"https://huggingface.co/papers/{pid}" if pid else None,
            pdf=f"https://arxiv.org/pdf/{pid}" if pid else None,
            source="hfpapers",
            extra={"paper_id": pid, "upvotes": p.get("upvotes")},
        ))
    items = [i for i in items if i]
    return ok("hfpapers", items, {"note": "ML papers trending di Hugging Face (metrik komunitas, bukan sitasi)"}) if items else empty("hfpapers")


SOURCES = [
    {
        "id": "arxiv", "label": "arXiv (preprints; cat: filter kategori)",
        "category": "free", "auth_env": None, "auth_required": False,
        "disciplines": ["physics", "mathematics", "computer-science"], "countries": [],
        "homepage": "https://arxiv.org",
        "note": "Preprint utama fisika/math/CS. submittedDate filter native.",
        "tools": [{"name": "arxiv_search", "description": "Cari preprint di arXiv (Atom API). Free. Trik query: 'cat:cs.CL AND all:reward' untuk filter kategori.", "input_schema": SEARCH_SCHEMA, "handler": _arxiv_search}],
    },
    {
        "id": "openreview", "label": "OpenReview (submissions + peer-review trail)",
        "category": "free", "auth_env": None, "auth_required": False,
        "disciplines": ["computer-science"], "countries": [],
        "homepage": "https://openreview.net",
        "note": "API v2; review/rebuttal/decision bisa diambil per forum.",
        "tools": [
            {"name": "openreview_search", "description": "Cari submission di OpenReview (API v2). Free. Berguna untuk melihat versi di bawah review, bukan hanya paper final.", "input_schema": SEARCH_SCHEMA, "handler": _openreview_search},
            {"name": "openreview_notes", "description": "Ambil semua note publik satu forum OpenReview — abstrak, reviews, rebuttals, meta-review, decision. Bisa kena challenge anti-scraping (blocked).", "input_schema": {"type": "object", "properties": {"forum": {"type": "string", "description": "Forum id OpenReview"}}, "required": ["forum"], "additionalProperties": False}, "handler": _openreview_notes},
        ],
    },
    {
        "id": "alphaxiv", "label": "AlphaXiv (semantic retrieval + researcher graph)",
        "category": "key", "auth_env": "ALPHAXIV_API_KEY", "auth_required": True,
        "disciplines": ["computer-science"], "countries": [],
        "homepage": "https://www.alphaxiv.org",
        "note": "Punya MCP resmi sendiri di api.alphaxiv.org/mcp/v1 — pertimbangkan pakai langsung.",
        "tools": [{"name": "alphaxiv_search", "description": "Cari paper + semantic retrieval + researcher graph via AlphaXiv. WAJIB ALPHAXIV_API_KEY (atau pakai MCP resmi alphaxiv langsung).", "input_schema": SEARCH_SCHEMA, "handler": _alphaxiv_search}],
    },
    {
        "id": "hfpapers", "label": "Hugging Face Papers (ML papers + community metrics)",
        "category": "free", "auth_env": None, "auth_required": False,
        "disciplines": ["computer-science"], "countries": [],
        "homepage": "https://huggingface.co/papers",
        "note": "Trending ML papers; upvotes komunitas. Respons API besar — di-slice server-side.",
        "tools": [{"name": "hf_search", "description": "Cari ML papers di Hugging Face Papers (trending + upvotes komunitas). Free, tanpa key. Tautan PDF ke arXiv bila id-nya arXiv.", "input_schema": SEARCH_SCHEMA, "handler": _hfpapers_search}],
    },
]
