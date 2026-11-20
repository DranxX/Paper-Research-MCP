# people.py — sumber people/orcid (profil peneliti + daftar publikasinya).

from __future__ import annotations

from ..core import empty, failed, http_get, json_loose, ok, std


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


SOURCE = {
    "id": "orcid", "label": "ORCID (researcher profile → works)",
    "category": "free", "auth_env": None, "auth_required": False,
    "disciplines": ["multidisciplinary"], "countries": [],
    "homepage": "https://orcid.org",
    "note": "Publik API v3; satu ORCID iD → daftar works + DOI.",
    "tools": [{"name": "orcid_works", "description": "Ambil daftar publikasi satu peneliti via ORCID public API (by ORCID iD).", "input_schema": {"type": "object", "properties": {"orcid": {"type": "string", "description": "ORCID iD, mis. 0000-0002-1825-0097"}, "limit": {"type": "integer", "minimum": 1, "maximum": 50, "default": 15}}, "required": ["orcid"], "additionalProperties": False}, "handler": _orcid_works}],
}

SOURCES = [SOURCE]
