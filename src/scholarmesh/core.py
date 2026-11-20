# ScholarMesh — shared helpers: standardized result schema (Reference.md §6), envelope
# contract, httpx with timeouts, year filter. Every connector returns the same shape.
# Standardized result schema (Reference.md §6): metadata, abstract, DOI, source,
# full-text access, provenance — every connector returns the same envelope.

from __future__ import annotations

import html
import json
import re
from typing import Any

import httpx

UA = "scholarmesh/0.2 (federated academic research agent; educational use)"
DEFAULT_TIMEOUT = 15.0

_TAG_RE = re.compile(r"<[^>]*>")
_ENTITY_RE = re.compile(r"&[a-z]+;|&#\d+;", re.I)
_WS_RE = re.compile(r"\s+")


def strip_html(s: Any) -> str:
    s = _TAG_RE.sub(" ", str(s or ""))
    s = _ENTITY_RE.sub(" ", s)
    return _WS_RE.sub(" ", s).strip()


def clamp(s: Any, n: int = 1400) -> str:
    s = str(s or "").strip()
    if len(s) > n:
        s = re.sub(r"\s+\S*$", "", s[:n]) + "…"
    return s


async def http_get(url: str, headers: dict | None = None, timeout: float = DEFAULT_TIMEOUT) -> dict:
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(timeout), follow_redirects=True) as client:
            res = await client.get(url, headers={"User-Agent": UA, **(headers or {})})
            return {"ok": res.status_code < 400, "status": res.status_code, "body": res.text, "error": None}
    except Exception as e:  # DNS / timeout / connect — detail jujur ke envelope
        return {"ok": False, "status": 0, "body": "", "error": _exc_detail(e)}


async def http_post(url: str, body: dict, headers: dict | None = None,
                    timeout: float = DEFAULT_TIMEOUT, form: bool = True) -> dict:
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(timeout), follow_redirects=True) as client:
            if form:
                res = await client.post(url, data=body, headers={"User-Agent": UA, **(headers or {})})
            else:
                res = await client.post(url, json=body, headers={"User-Agent": UA, **(headers or {})})
            return {"ok": res.status_code < 400, "status": res.status_code, "body": res.text, "error": None}
    except Exception as e:
        return {"ok": False, "status": 0, "body": "", "error": _exc_detail(e)}


def _exc_detail(e: Exception) -> str:
    cause = getattr(e, "__cause__", None) or getattr(e, "__context__", None)
    if cause is not None:
        code = getattr(cause, "code", None) or type(cause).__name__
        return str(code)
    return str(e)


def std(*, title, authors=None, year=None, doi=None, venue=None, abstract=None,
        url=None, pdf=None, source, extra=None) -> dict | None:
    """Standardized item — the ONLY shape connectors may emit."""
    title = strip_html(title)
    if not title:
        return None
    authors = [strip_html(a) for a in (authors or [])[:12] if strip_html(a)]
    return {
        "title": clamp(title, 300),
        "authors": authors,
        "year": year,
        "doi": str(doi).strip() if doi else None,
        "venue": strip_html(venue) if venue else None,
        "abstract": clamp(strip_html(abstract)) if abstract else None,
        "url": url,
        "pdf": pdf,
        "source": source,
        "extra": extra or {},
    }


# Envelopes — the ONLY shapes tools may return.
def ok(source: str, items: list, meta: dict | None = None) -> dict:
    items = [i for i in items if i]
    return {"status": "ok", "source": source, "count": len(items), "items": items, "meta": meta or {}}


def empty(source: str, note: str = "") -> dict:
    return {"status": "empty", "source": source, "count": 0, "items": [], "meta": {"note": note}}


def blocked(source: str, detail: str) -> dict:
    # Bot-wall / WAF / maintenance / DNS — reachable-in-principle, refused in practice.
    return {"status": "blocked", "source": source, "count": 0, "items": [], "meta": {"detail": detail}}


def auth_required(source: str, env_name: str, detail: str = "") -> dict:
    return {"status": "auth-required", "source": source, "count": 0, "items": [], "meta": {"env": env_name, "detail": detail}}


def failed(source: str, detail: str) -> dict:
    return {"status": "error", "source": source, "count": 0, "items": [], "meta": {"detail": detail}}


def json_loose(body: str) -> Any:
    try:
        return json.loads(body)
    except Exception:
        return None


def year_filter(items: list, yf: int | None, yt: int | None) -> tuple[list, int]:
    """Universal year filter — dipakai registry untuk SEMUA tool sebagai jaminan (connector yang
    API-nya tidak dukung filter tanggal tetap terfilter di sini; yang mendukung memakai filter
    native di handler masing-masing). Item tanpa tahun DIBUANG saat filter aktif — dihitung di meta."""
    if not yf and not yt:
        return items, 0
    keep, dropped = [], 0
    for it in items:
        y = it.get("year")
        if y is None:
            dropped += 1
            continue
        if (not yf or y >= yf) and (not yt or y <= yt):
            keep.append(it)
        else:
            dropped += 1
    return keep, dropped


# Aliases dipakai beberapa connector (1:1 dengan port JS)
html_unescape = html.unescape
