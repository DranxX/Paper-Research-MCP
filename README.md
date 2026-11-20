<div align="center">

# ScholarMesh

**Federated academic research retrieval over MCP** — 40 sources, 46 tools, one
standardized result schema. Formerly `paper-research-mcp`; now with **Europe PMC,
PubMed, OpenAIRE, Zenodo, DataCite, OSF, zbMATH, Hugging Face Papers, CORE** and a
companion research skill (`skills/research`).

[![PyPI](https://img.shields.io/pypi/v/scholarmesh)](https://pypi.org/project/scholarmesh/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org)
[![MCP](https://img.shields.io/badge/protocol-MCP_2024--11--05-orange)](https://modelcontextprotocol.io)
[![Sources](https://img.shields.io/badge/sources-40-blueviolet)](#-connectors)
[![Tools](https://img.shields.io/badge/tools-46-brightgreen)](#-tools)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow)](#-license)

**🇮🇩 [Versi Bahasa Indonesia](README_ID.md)**

</div>

---

## 📜 What is ScholarMesh?

An MCP server that fans one (or many) keywords out to **40 academic sources in
parallel**, deduplicates results by DOI → title, and tags provenance (`alsoIn`,
`matchedQueries`). Each source is its own connector with its own tools; a federation
layer sits on top. Sources are grouped by **function** in the codebase — geography is
just metadata (`countries`) on each connector.

- 🔓 **Free-first** — 18 sources work with no key at all; 10 premium/key connectors
  wake up only when you set their env vars
- 🧵 **Federated** — `search_papers` fans out, dedups, provenances
- 📅 **Date-bounded** — `year_from`/`year_to` native where supported, universal
  post-filter everywhere else
- 🟢 **Honest failures** — bot-walls return structured `blocked` envelopes with a
  manual-fallback URL, never silent lies
- 🏷 **Queryable catalog** — `list_sources` exposes category, disciplines, countries,
  and env status per source

## 📦 Install

**Requires:** [uv](https://docs.astral.sh/uv/). No API key needed to start.

```bash
uv tool install scholarmesh
```

That's it — the server binary `scholarmesh` is now on your PATH. (Legacy installs of
`paper-research-mcp` keep working: the package ships a `paper-research-mcp` command
alias. The old PyPI name is deprecated and no longer updated.)

### Connect it to your MCP client

Add one block to your client's MCP config, then **restart the client**. Tested,
working shape (ZCode & modern clients that take a bare server map):

```jsonc
{
  "scholarmesh": {
    "type": "stdio",
    "command": "uvx",
    "args": ["scholarmesh"]
  }
}
```

Clients that wrap servers under a `mcpServers` key (Claude Desktop, Cursor):

```jsonc
{
  "mcpServers": {
    "scholarmesh": { "command": "uvx", "args": ["scholarmesh"] }
  }
}
```

Where the config file lives:

| Client | Config location |
|---|---|
| **ZCode** | Settings → MCP servers |
| **Claude Desktop** | macOS: `~/Library/Application Support/Claude/claude_desktop_config.json` · Windows: `%APPDATA%\Claude\claude_desktop_config.json` |
| **Cursor** | `~/.cursor/mcp.json` (Settings → MCP) |
| **VS Code (Copilot)** | `.vscode/mcp.json` — servers sit under a `"servers"` key |
| **Codex CLI** | `~/.codex/config.toml` → `[mcp_servers.scholarmesh]` with `command = "uvx"`, `args = ["scholarmesh"]` |

Already `uv tool install`ed and the binary is on your client's PATH? Pointing
straight at it also works: `"command": "scholarmesh"` (same `type`/`args` shape).

**Verify:** restart your client — all 46 tools appear automatically. From a terminal
you can also probe it: `scholarmesh` prints `46 tools, 40 sources ready (stdio)` and
waits (Ctrl+C exits).

**Update / remove:**

```bash
uv tool upgrade scholarmesh
uv tool uninstall scholarmesh
```

**From a local checkout (development):** `uv run scholarmesh` inside the repo, or
point the client at `uv --directory <path>/ScholarMesh run scholarmesh`. See
[CONTRIBUTING.md](CONTRIBUTING.md).

## 🚀 Usage

Connect, then just ask your agent in plain language:

| You ask | What runs |
|---|---|
| *"Survey 2024+ work on LLM watermarking **and** detecting AI-generated text — all free sources"* | `search_papers` with parallel `queries:[]` + `year_from`, cross-source dedup |
| *"Find the proof of the Pythagorean theorem and its prerequisites"* | `proofwiki_search` → `proofwiki_get` |
| *"Full text of this paper: PMC7159299"* | `europepmc_fulltext` (OA JATS XML → text) |
| *"Biomed papers on CRISPR base editing, 2025+ only"* | `europepmc_search` / `pubmed_search` with year filter |
| *"What did reviewers say about this OpenReview submission?"* | `openreview_search` → `openreview_notes` |
| *"Find code implementations of image-classification papers"* | `pwc_search` |
| *"Resolve this DOI and find an open-access copy"* | `crossref_doi` → `unpaywall_resolve` |
| *"Cari jurnal Indonesia soal pertanian"* | `garuda_search` / `neliti_search` / `brin_search` |
| *"Math papers reviewing Ricci flow"* | `zbmath_search` |

<details>
<summary>Example response (trimmed)</summary>

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

`alsoIn` = other sources holding the same paper (deduped), `matchedQueries` = which
of your keywords matched. Bot-walled sources come back as `{"status": "blocked"}`
with a manual-fallback URL — honest, never silent.
</details>

## 🔑 Optional API keys

18 sources run with no key at all. Key-gated sources stay dormant until their env var
is set (see [`.env.example`](.env.example)):

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

## 🌐 Sources (40)

| Category | Sources |
|---|---|
| **FREE** (18, default on) | OpenAlex · Crossref · arXiv · DOAJ · OpenReview · Hugging Face Papers · Unpaywall · Zenodo · DataCite · OSF · OpenAIRE · INSPIRE-HEP · ERIC · zbMATH Open · Europe PMC · PubMed · NSSD (China SSH) · ORCID |
| **FREE, bot-wall** (12, default on, honest errors) | Semantic Scholar · Papers with Code · Google Scholar · GARUDA · SINTA · OneSearch · RAMA · Moraref · Neliti · BRIN · ProofWiki (math proofs) · ScienceDB |
| **API KEY** (10, dormant until env set) | CORE (free registration) · NASA ADS · AlphaXiv · Scopus · The Lens · Dimensions · Web of Science · Baidu Scholar · AMiner · CSTR |

> 🇮🇩🇨🇳 Regional sources (Indonesia `ID`, China `CN`) are regular connectors whose
> `countries` metadata says where they come from — every source also carries
> `disciplines` metadata (filterable via `list_sources`).

## 🛠 Tools

**46 tools** are auto-discovered by any MCP client via `tools/list`. Three entry
points worth knowing:

- `search_papers` — federated search; supports single `query` or parallel
  `queries: ["k1","k2"]`, date bounds `year_from`/`year_to`, source selection,
  dedup by DOI → title, and provenance (`alsoIn` + `matchedQueries`)
- `list_sources` — every source with category, disciplines, countries, env status
- `europepmc_fulltext` — OA full text (JATS XML → clean text) for one PMCID

Full per-source tools (e.g. `openalex_search`, `pubmed_search`, `zbmath_search`,
`proofwiki_get`, `garuda_search`) are listed by your client automatically.

## 🧩 Skills

[`skills/research/`](skills/research/) — a companion agent skill (SKILL.md router +
`workflows/` + `references/`) for research-grade work in any field: **literature
scans** (field→source routing), **claim verification**, **proof & argument
verification** (math, logic, CS, law, philosophy), **counterexample /
falsification hunts**, and **numeric sanity checks**. It uses ScholarMesh tools when
connected and falls back to manual search when not — see
[`skills/README.md`](skills/README.md) for the one-command install.

## 🏗 Architecture

```
pyproject.toml                ← uv package ([project.scripts] scholarmesh)
└── src/scholarmesh/
    ├── server.py             ← MCP stdio entry (official `mcp` SDK, lowlevel Server)
    ├── registry.py           ← flat SOURCES list, auth-gating, universal year post-filter
    ├── federation.py         ← search_papers: queries×sources parallel (pool 8), dedup, provenance
    ├── core.py               ← httpx w/ timeout, standardized item schema, envelopes, year filter
    └── sources/              ← grouped by FUNCTION; geography = metadata per source
        ├── indexes.py    (8)   OpenAlex Crossref DOAJ S2 Lens Dimensions Scopus WoS
        ├── preprints.py  (4)   arXiv OpenReview(2) AlphaXiv HF Papers
        ├── archives.py   (6)   Unpaywall Zenodo DataCite OSF OpenAIRE CORE
        ├── domain.py     (8)   INSPIRE ERIC zbMATH ProofWiki(2) PwC EuropePMC(2) PubMed ADS
        ├── regional.py  (13)   GARUDA SINTA OneSearch RAMA Moraref Neliti BRIN GScholar NSSD Baidu AMiner ScienceDB CSTR
        └── people.py     (1)   ORCID
```

## 🧪 Testing

```bash
uv run python tests/e2e_all_tools.py
```

Live suite with **~48 checks**: all 44 connector tools one by one (envelope-shape
validation + per-category status expectations), all three federation modes, year-filter
leak checks, and the MCP stdio handshake in a subprocess. Scraper sources returning
`blocked` count as PASS — the envelope is the contract, not the network mood.
Last run: **47/47 PASS** (1 conditional check skipped by design).

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) — how to run the tests, add a source, and the
release process.

## 📄 License

MIT. Connector plan distilled from `Collection/Markdown/Refer/Reference.md`
(paper-search-mcp ecosystem + indonesia_research + China platforms + premium
connectors) plus live-verified additions (Europe PMC, PubMed, OpenAIRE, Zenodo,
DataCite, OSF, zbMATH, HF Papers, CORE).
