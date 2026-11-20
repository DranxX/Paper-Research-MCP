# Contributing

Maintainer/contributor notes — the public install/usage docs live in
[README.md](README.md) / [README_ID.md](README_ID.md).

## Run the tests

```bash
uv run python tests/e2e_all_tools.py
```

Live suite: every connector tool one by one (envelope-shape validation + per-category
status expectations), the three federation modes, year-filter leak checks, and the MCP
stdio handshake in a subprocess. Scraper sources returning `blocked` count as PASS —
the envelope is the contract, not the network mood.

## Add a source

1. **Probe the endpoint live first** (curl/httpx) — confirm response shape, rate
   limits, and bot-walls before writing any code. Record the probe (command + output
   + date) in the PR.
2. Add the source to the right module under `src/scholarmesh/sources/`, grouped by
   function — NOT by country:

   | Module | Kind |
   |---|---|
   | `indexes.py` | big multidisciplinary citation/metadata indexes |
   | `preprints.py` | preprint servers & venue-specific paper indexes |
   | `archives.py` | OA repositories/aggregators & resolvers |
   | `domain.py` | domain-specific sources (physics, math, biomed, edu, astro…) |
   | `regional.py` | country-tagged sources (geography is metadata) |
   | `people.py` | researcher profiles |

   Each source is one dict in the module's `SOURCES` list:

   ```python
   {
       "id": "...", "label": "...", "category": "free|bot-wall|key",
       "auth_env": None, "auth_required": False,
       "disciplines": ["..."], "countries": [],   # [] = global
       "homepage": "...", "note": "...",
       "tools": [{"name": "...", "description": "...",
                  "input_schema": {...}, "handler": _handler}],
   }
   ```

   Handler returns the standard envelopes only (`ok`/`empty`/`blocked`/
   `auth_required`/`failed` from `core.py`) with items built by `std()`.
3. Registry, federation, and `list_sources` pick it up automatically (flat SOURCES).
4. Add tool checks to `tests/e2e_all_tools.py` with the right allowed statuses
   (bot-wall sources may legitimately return `blocked`).
5. Update `README.md` + `README_ID.md` (badge counts, sources table, architecture
   tree, tool count) and `skills/research/references/tool-map.md` if user-facing.

Rules of the house: honest envelopes (never fake a result), fixed `https://` hosts
only, attribution kept in `meta` where licenses demand it (e.g. ProofWiki CC BY-SA),
and no new heavy dependencies without a good reason.

## Release (maintainer)

1. Bump the version in `pyproject.toml`, `server.py`, and `__init__.py`.
2. Dry-run to TestPyPI (optional):

   ```bash
   uv publish --publish-url https://test.pypi.org/legacy/ --token pypi-XXXXXXXX
   ```

3. Release:

   ```bash
   uv build
   uv publish --token pypi-XXXXXXXX
   ```

   Alternatively, push a GitHub release —
   [`.github/workflows/publish.yml`](.github/workflows/publish.yml) publishes via
   PyPI Trusted Publishing (OIDC, no token needed).
4. Users upgrade with `uv tool upgrade scholarmesh`.
