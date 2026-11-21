<div align="center">

# 🎓 ScholarMesh

### *One query. Forty academic sources. Zero API keys to start.*

**Federated academic research retrieval over MCP** — fan one (or many) keywords out
to 40 scholarly sources in parallel, deduplicate by DOI, keep provenance, and get
honest failures when a source says no.

[![PyPI](https://img.shields.io/pypi/v/scholarmesh)](https://pypi.org/project/scholarmesh/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org)
[![MCP](https://img.shields.io/badge/protocol-MCP_2024--11--05-orange)](https://modelcontextprotocol.io)
[![Sources](https://img.shields.io/badge/sources-40-8A2BE2)](#-40-sources-46-tools)
[![Tools](https://img.shields.io/badge/tools-46-brightgreen)](#-40-sources-46-tools)
[![Tests](https://img.shields.io/badge/e2e-47%20PASS-success)](#-testing)
[![License](https://img.shields.io/badge/license-MIT-yellow)](#-license)

**🇬🇧 English** · [🇮🇩 Bahasa Indonesia](README_ID.md) · [📦 PyPI](https://pypi.org/project/scholarmesh/)

</div>

---

## ✨ Why ScholarMesh?

| | |
|---|---|
| 🧵 **Federated by design** | `search_papers` runs 1–8 keywords × 30+ sources **in parallel** (pool of 8), dedups by DOI → normalized title, and tags every result with `alsoIn` (where else it appeared) and `matchedQueries` (which keyword hit it) |
| 🔓 **Free-first** | 18 sources run with **zero keys**; 10 more unlock with a free registration; premium indexes stay dormant until you set env vars |
| 📅 **Date-bounded everywhere** | `year_from` / `year_to` pass natively to APIs that support it and apply as a universal post-filter everywhere else — no leaks |
| 🏷 **A catalog you can query** | every source carries `category` (free / bot-wall / key), `disciplines`, and `countries` metadata — `list_sources` filters by all three |
| 🟢 **Honest failures** | bot-walls and rate limits come back as structured `blocked` envelopes **with a manual-fallback URL** — never a silent lie |
| 🧩 **Agent skill included** | `skills/research` — literature scans, claim verification, proof & argument verification, falsification hunts, numeric sanity checks |

---

## 🚀 60-second start

**Step 1 — install** (requires [uv](https://docs.astral.sh/uv/)):

```bash
uv tool install scholarmesh
```

**Step 2 — connect** your MCP client, then restart it:

```jsonc
// ZCode & modern clients (tested shape)
{
  "scholarmesh": {
    "type": "stdio",
    "command": "uvx",
    "args": ["scholarmesh"]
  }
}
```

<details>
<summary><b>Other clients</b> — Claude Desktop, Cursor, VS Code, Codex CLI</summary>

```jsonc
// Claude Desktop & Cursor (mcpServers wrapper)
{
  "mcpServers": {
    "scholarmesh": { "command": "uvx", "args": ["scholarmesh"] }
  }
}
```

| Client | Config location |
|---|---|
| **ZCode** | Settings → MCP servers |
| **Claude Desktop** | macOS: `~/Library/Application Support/Claude/claude_desktop_config.json` · Windows: `%APPDATA%\Claude\claude_desktop_config.json` |
| **Cursor** | `~/.cursor/mcp.json` (Settings → MCP) |
| **VS Code (Copilot)** | `.vscode/mcp.json` — servers sit under a `"servers"` key |
| **Codex CLI** | `~/.codex/config.toml` → `[mcp_servers.scholarmesh]` with `command = "uvx"`, `args = ["scholarmesh"]` |

GUI apps often don't inherit your shell PATH — the `uvx` form above sidesteps that
entirely. Already `uv tool install`ed? `"command": "scholarmesh"` works too.

</details>

**Step 3 — verify & use.** Restart the client and all **46 tools** appear
(`tools/list`). From a terminal you can also probe:

```bash
scholarmesh           # prints: 46 tools, 40 sources ready (stdio) — Ctrl+C exits
uv tool upgrade scholarmesh
uv tool uninstall scholarmesh
```

## 💬 What you can just *ask*

| You say | ScholarMesh runs |
|---|---|
| *"Survey 2024+ work on LLM watermarking **and** AI-text detection — all free sources"* | `search_papers` — parallel `queries:[]` + `year_from`, cross-source dedup |
| *"Full text of PMC7159299"* | `europepmc_fulltext` — OA JATS XML → clean text |
| *"Biomed papers on CRISPR base editing, 2025+"* | `europepmc_search` / `pubmed_search` + year filter |
| *"Proof of the Pythagorean theorem + its prerequisites"* | `proofwiki_search` → `proofwiki_get` |
| *"Math papers reviewing Ricci flow"* | `zbmath_search` (MSC-classified reviews) |
| *"Reviewers' take on this OpenReview submission?"* | `openreview_search` → `openreview_notes` |
| *"Code implementations for image-classification papers"* | `pwc_search` |
| *"Resolve this DOI + find an OA copy"* | `crossref_doi` → `unpaywall_resolve` |
| *"Cari jurnal Indonesia soal pertanian"* | `garuda_search` / `neliti_search` / `brin_search` |

<details>
<summary>📦 What a result actually looks like (trimmed)</summary>

```jsonc
{
  "status": "ok",
  "source": "federation",
  "count": 2,
  "items": [
    {
      "title": "…",
      "authors": ["…"],
      "year": 2024,
      "doi": "10.…",
      "venue": "…",
      "abstract": "…",
      "url": "https://doi.org/10.…",
      "pdf": "https://…/paper.pdf",
      "source": "openalex",
      "extra": { "cited_by_count": 42 },
      "alsoIn": ["crossref", "semantic_scholar"],
      "matchedQueries": ["LLM watermarking"]
    }
  ],
  "meta": { "…": "coverage per keyword, year filter, skipped sources" }
}
```

Every tool returns the **same envelope**: `status · source · count · items[] · meta`.
`alsoIn` = other sources holding the same paper (deduped); `matchedQueries` = which
of your keywords matched. Bot-walled sources return `{"status": "blocked"}` with a
manual-fallback URL.
</details>

## 🌐 40 sources · 46 tools

| Category | Sources |
|---|---|
| 🟢 **FREE** — 18, on by default | OpenAlex · Crossref · arXiv · DOAJ · OpenReview · Hugging Face Papers · Unpaywall · Zenodo · DataCite · OSF · OpenAIRE · INSPIRE-HEP · ERIC · zbMATH Open · Europe PMC · PubMed · NSSD (China SSH) · ORCID |
| 🟡 **FREE, bot-wall** — 12, on by default, honest errors | Semantic Scholar · Papers with Code · Google Scholar · GARUDA 🇮🇩 · SINTA 🇮🇩 · OneSearch 🇮🇩 · RAMA 🇮🇩 · Moraref 🇮🇩 · Neliti 🇮🇩 · BRIN 🇮🇩 · ProofWiki · ScienceDB 🇨🇳 |
| 🔑 **API KEY** — 10, dormant until env set | CORE *(free registration)* · NASA ADS · AlphaXiv · Scopus · The Lens · Dimensions · Web of Science · Baidu Scholar 🇨🇳 · AMiner 🇨🇳 · CSTR 🇨🇳 |

<details>
<summary><b>All 46 tools</b></summary>

| Group | Tools |
|---|---|
| Federation | `search_papers` · `list_sources` |
| Indexes | `openalex_search` · `crossref_search` · `crossref_doi` · `doaj_search` · `semantic_scholar_search` · `lens_search` ᵏ · `dimensions_search` ᵏ · `scopus_search` ᵏ · `wos_search` ᵏ |
| Preprints | `arxiv_search` · `openreview_search` · `openreview_notes` · `alphaxiv_search` ᵏ · `hf_search` |
| Archives | `unpaywall_resolve` · `zenodo_search` · `datacite_search` · `osf_search` · `openaire_search` · `core_search` ᵏ |
| Domain | `inspire_search` · `eric_search` · `zbmath_search` · `proofwiki_search` · `proofwiki_get` · `pwc_search` · `europepmc_search` · `europepmc_fulltext` · `pubmed_search` · `ads_search` ᵏ |
| Regional | `garuda_search` · `sinta_search` · `onesearch_search` · `rama_search` · `moraref_search` · `neliti_search` · `brin_search` · `google_scholar_search` · `nssd_search` · `baidu_scholar_search` ᵏ · `aminer_search` ᵏ · `sciencedb_search` · `cstr_resolve` ᵏ |
| People | `orcid_works` |

ᵏ = needs an env var (see below)
</details>

<details>
<summary><b>🔑 API keys</b> — all optional; 18 sources need none</summary>

| Env var | Source | Note |
|---|---|---|
| `S2_API_KEY` | Semantic Scholar | removes the 429 rate limit |
| `OPENALEX_API_KEY` | OpenAlex | dedicated daily budget |
| `NCBI_API_KEY` | PubMed E-utilities | 3 → 10 req/s (free registration) |
| `UNPAYWALL_EMAIL` | Unpaywall | politeness email (optional) |
| `CORE_API_KEY` | CORE | **free registration** — deepest OA full-text index |
| `ADS_TOKEN` | NASA ADS | free for researchers |
| `ALPHAXIV_API_KEY` | AlphaXiv | or add [their official MCP](https://api.alphaxiv.org/mcp/v1) directly |
| `SCOPUS_API_KEY` | Scopus | needs institutional entitlement |
| `LENS_TOKEN` / `DIMENSIONS_TOKEN` / `WOS_API_KEY` | Lens / Dimensions / WoS | subscription/approval-based |
| `BAIDU_API_KEY` / `AMINER_API_KEY` / `CSTR_CLIENT_ID`+`CSTR_SECRET` | Baidu / AMiner / CSTR | China platforms |

Wire them via your client's `env` block or [`.env.example`](.env.example).
</details>

## 🧩 Companion skill: `research`

[`skills/research/`](skills/research/) ships with the repo — copy it into your agent's
skills directory and it auto-triggers on research-grade tasks:

- 🔎 **Literature scans** — field→source routing, two time windows, reading order, gap finding
- ✅ **Claim verification** — does a claimed result exist, and what is its *real* status?
- 🧮 **Proof & argument verification** — math, formal logic, CS correctness, legal reasoning, philosophy — validity vs soundness
- ⚔️ **Counterexample / falsification hunts** — formal, doctrinal, empirical
- 🔢 **Numeric sanity checks** — falsify fast; never prove

```bash
git clone https://github.com/DranxX/scholarmesh && cd scholarmesh
cp -r skills/research ~/.zcode/skills/     # or ~/.claude/skills/ etc.
```

Details: [skills/README.md](skills/README.md).

## 🏗 Architecture

```
pyproject.toml                ← uv package ([project.scripts] scholarmesh)
└── src/scholarmesh/
    ├── server.py             ← MCP stdio entry (official `mcp` SDK, lowlevel Server)
    ├── registry.py           ← flat SOURCES list, auth-gating, universal year post-filter
    ├── federation.py         ← search_papers: queries×sources parallel (pool 8), dedup, provenance
    ├── core.py               ← httpx w/ timeout, standardized item schema, envelopes, year filter
    └── sources/              ← grouped by FUNCTION; geography = metadata per source
        ├── indexes.py    (8)  OpenAlex Crossref DOAJ S2 Lens Dimensions Scopus WoS
        ├── preprints.py  (4)  arXiv OpenReview(2) AlphaXiv HF Papers
        ├── archives.py   (6)  Unpaywall Zenodo DataCite OSF OpenAIRE CORE
        ├── domain.py     (8)  INSPIRE ERIC zbMATH ProofWiki(2) PwC EuropePMC(2) PubMed ADS
        ├── regional.py  (13)  GARUDA SINTA OneSearch RAMA Moraref Neliti BRIN GScholar NSSD Baidu AMiner ScienceDB CSTR
        └── people.py     (1)  ORCID
```

## 🧪 Testing

```bash
uv run python tests/light_smoke.py       # no-key smoke: gates + stdio + 3 tiny calls
uv run python tests/light_smoke.py --offline   # zero network
uv run python tests/e2e_all_tools.py     # full live suite (44 tools + federation + stdio)
```

The full suite runs **~48 checks** — every connector tool one by one (envelope-shape
validation + per-category status expectations), three federation modes, year-filter
leak checks, and the MCP stdio handshake. Scraper sources returning `blocked` count
as PASS: **the envelope is the contract, not the network mood**. Last run: **47/47 PASS**.

## ❓ FAQ

<details>
<summary>Why does a source come back <code>blocked</code>?</summary>

Some platforms (Google Scholar, ProofWiki, several regional portals) sit behind bot
protection. ScholarMesh doesn't pretend otherwise — you get a structured envelope
explaining what happened plus the exact URL to try manually. It's a working answer,
not an error.
</details>

<details>
<summary>Do I need any API key?</summary>

No. 18 sources work keyless. Keys only raise rate limits (Semantic Scholar, PubMed)
or unlock premium curated indexes (Scopus, WoS, Lens…).
</details>

<details>
<summary>What happened to <code>paper-research-mcp</code>?</summary>

That was this project's first name. The package was renamed to **scholarmesh**; the
old PyPI name is retired and no longer updated. Install via `uv tool install scholarmesh`.
</details>

## 🤝 Contributing

Issues and PRs welcome — see [CONTRIBUTING.md](CONTRIBUTING.md) for the probe-first
connector checklist, the test suite, and the release process.

## 📄 License

MIT. Connector plan distilled from a curated reference doc (`Reference.md`) plus
live-verified additions (Europe PMC, PubMed, OpenAIRE, Zenodo, DataCite, OSF, zbMATH,
HF Papers, CORE).

<div align="center">

**Built by [DranxX](https://github.com/DranxX)** — if ScholarMesh saved you a research all-nighter, a ⭐ is appreciated.

</div>
