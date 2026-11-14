# proofwiki.py — ProofWiki (proofwiki.org): wiki komunitas berisi definisi, teorema,
# dan bukti lengkap untuk matematika. MediaWiki API (api.php) gratis tanpa key, tapi
# berada di depan Cloudflare — dari jaringan tertentu kena JS challenge (probes 14 Nov 2026:
# "Just a moment..." walau pakai UA browser) → blocked best-effort dengan saran manual,
# bukan error diam. Dari jaringan ber-IP bersih biasanya 200.
# Konten berlisensi CC BY-SA 3.0 / GFDL — atribusi wajib saat mengutip ulang (di meta envelope).

from __future__ import annotations

import re
from urllib.parse import quote

from ..core import blocked, empty, failed, http_get, json_loose, ok, std, strip_html

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


SEARCH_SCHEMA = {
    "type": "object",
    "properties": {
        "query": {"type": "string",
                  "description": "Nama teorema/definisi/istilah, mis. 'Pythagorean Theorem', 'metric space', 'Bayes'"},
        "limit": {"type": "integer", "minimum": 1, "maximum": 25, "default": 5},
    },
    "required": ["query"],
    "additionalProperties": False,
}

GET_SCHEMA = {
    "type": "object",
    "properties": {
        "page": {"type": "string",
                 "description": "Judul halaman persis, mis. 'Pythagorean Theorem' atau 'Definition:Metric Space' (cari dulu via proofwiki_search)"},
    },
    "required": ["page"],
    "additionalProperties": False,
}


async def _proofwiki_search(a: dict) -> dict:
    n = min(a.get("limit", 5), 25)
    q = quote(a["query"], safe="")
    r = await http_get(f"{API}?action=query&list=search&srsearch={q}&srlimit={n}&format=json&formatversion=2")
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
    })


async def _proofwiki_get(a: dict) -> dict:
    title = str(a["page"]).strip().replace(" ", "_")
    r = await http_get(
        f"{API}?action=query&prop=revisions&rvslots=main&rvprop=content&redirects=1"
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


CONNECTOR = {
    "id": "proofwiki",
    "label": "ProofWiki (math definitions, theorems, complete proofs)",
    "category": "bot-wall",
    "auth_env": None,
    "auth_required": False,
    "homepage": "https://proofwiki.org",
    "note": "API MediaWiki gratis tanpa key, tapi Cloudflare-fronted — dari jaringan tertentu kena JS challenge "
            "(probes 14 Nov 2026: blocked). Dari jaringan ber-IP bersih biasanya 200. Konten CC BY-SA 3.0/GFDL — "
            "atribusi wajib. Kompanion skill: skills/math-research.",
    "tools": [
        {"name": "proofwiki_search", "description": "Cari teorema/definisi/bukti matematika di ProofWiki (proofwiki.org). "
                     "Gratis via MediaWiki API, tapi bisa kena Cloudflare bot-wall (envelope blocked + saran manual). "
                     "Cocok untuk theorem-hunting sebelum membuktikan ulang suatu klaim.",
         "input_schema": SEARCH_SCHEMA, "handler": _proofwiki_search},
        {"name": "proofwiki_get", "description": "Ambil wikitext lengkap satu halaman ProofWiki (teorema/definisi/bukti) by judul. "
                     "Wikitext berisi wikilink ke definisi & lema prasyarat — bagus untuk melacak pohon dependensi bukti. "
                     "Bisa kena Cloudflare (blocked).",
         "input_schema": GET_SCHEMA, "handler": _proofwiki_get},
    ],
}
