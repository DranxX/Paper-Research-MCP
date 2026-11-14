<div align="center">

# Paper-Research-MCP

**Federated academic research retrieval over MCP** — 31 connectors, 36 tools,
one standardized result schema. Now with **ProofWiki** + a companion skill for
math research (`skills/math-research`).

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org)
[![MCP](https://img.shields.io/badge/protocol-MCP_2024--11--05-orange)](https://modelcontextprotocol.io)
[![Connectors](https://img.shields.io/badge/connectors-31-blueviolet)](#-connectors)
[![Tools](https://img.shields.io/badge/tools-36-brightgreen)](#-tools)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow)](#-license)

**🇮🇩 [Versi Bahasa Indonesia](https://github.com/DranxX/Paper-Research-MCP/blob/main/README_ID.md)** · 📦 **Source code:** [github.com/DranxX/Paper-Research-MCP](https://github.com/DranxX/Paper-Research-MCP)

</div>

---

## 📜 What is Paper-Research-MCP?

A brand-new **MCP server for academic paper search**, distilled from the expansion plan
in `Collection/Markdown/Refer/Reference.md` — absorbed while curating three upstream
collections plus that additional reference, to make agent-side research *broader*, not
just deeper.

It implements the document's core design rule: **don't flatten every source into one
`search_papers()`**. Each source is its own connector with its own tools (discovery,
conference review, paper↔code mapping, metadata resolution, OA resolution), and a
federation layer on top handles cross-source search, deduplication, and provenance.

- 🔓 **Free-first** — everything runs without an API key; premium connectors are
  registered but dormant until you set their env vars
- 🧵 **Federated** — cross-source search with DOI → title dedup and `alsoIn`/`matchedQueries`
  provenance
- 📅 **Date-bounded** — `year_from`/`year_to` passed natively to APIs that support it,
  universal post-filter for the rest
- 📦 **uv-packaged** — Python ≥ 3.10, deps only `mcp` + `httpx`
- 🟢 **Honest failures** — bot-walls and rate limits return structured envelopes with
  manual-fallback suggestions, never silent lies

## 📦 Install

**Requires:** Python ≥ 3.10 and [uv](https://docs.astral.sh/uv/). Deps: `mcp` + `httpx`.

**Local checkout** — point your MCP client at the folder:

```jsonc
// ZCode / Claude Desktop / Cursor / any MCP client
{
  "mcpServers": {
    "paper-research": {
      "command": "uv",
      "args": ["--directory", "<path>/Paper-Research-MCP", "run", "paper-research-mcp"],
      "env": { "S2_API_KEY": "", "ADS_TOKEN": "", "SCOPUS_API_KEY": "" }
    }
  }
}
```

**Published on PyPI** — after release (see 🚀 Publishing below) it becomes one line:

```jsonc
{ "mcpServers": { "paper-research": { "command": "uvx", "args": ["paper-research-mcp"] } } }
```

## 🔑 Optional API keys

All free connectors work without any key. Premium connectors stay dormant until their
env var is set (see [`.env.example`](.env.example)):

| Env var | Connector | Note |
|---|---|---|
| `S2_API_KEY` | Semantic Scholar | removes the 429 rate limit |
| `OPENALEX_API_KEY` | OpenAlex | dedicated daily budget |
| `ADS_TOKEN` | NASA ADS | free for researchers |
| `ALPHAXIV_API_KEY` | AlphaXiv | or add [their official MCP](https://api.alphaxiv.org/mcp/v1) directly |
| `SCOPUS_API_KEY` | Scopus | needs institutional entitlement |
| `LENS_TOKEN` / `DIMENSIONS_TOKEN` / `WOS_API_KEY` | Lens / Dimensions / WoS | subscription-based |
| `BAIDU_API_KEY` / `AMINER_API_KEY` / `CSTR_CLIENT_ID`+`CSTR_SECRET` | Baidu / AMiner / CSTR | China platforms |

## 🌐 Connectors

| Category | Sources |
|---|---|
| **FREE** (default on) | OpenAlex · Crossref · arXiv · DOAJ · OpenReview · INSPIRE-HEP · ERIC · Unpaywall · ORCID · NSSD (China SSH) · ScienceDB |
| **FREE, bot-wall/rate-limited** (default on, honest errors) | Semantic Scholar · Papers with Code · Google Scholar · Baidu Scholar · GARUDA · SINTA · OneSearch · RAMA · Moraref · Neliti · BRIN · ProofWiki (math proofs) |
| **API KEY** (dormant until env set) | NASA ADS · AlphaXiv · Scopus · The Lens · Dimensions · Web of Science · AMiner · CSTR |

> 🇮🇩 The `indonesia_research` block follows the Reference.md warning: these platforms
> have **no official APIs** — they are best-effort scrapers with truthful failure envelopes.

## 🛠 Tools

**36 tools** are auto-discovered by any MCP client via `tools/list` — no configuration
needed. Three entry points worth knowing:

- `search_papers` — federated search; supports single `query` or parallel
  `queries: ["k1","k2"]`, date bounds `year_from`/`year_to`, source selection,
  dedup by DOI → title, and provenance (`alsoIn` + `matchedQueries`)
- `list_sources` — every connector with its access category and env status

Math sources: `proofwiki_search` / `proofwiki_get` (ProofWiki — definitions, theorems,
complete proofs; Cloudflare best-effort with honest `blocked` envelopes).

Full per-source tools (e.g. `openalex_search`, `openreview_notes`, `garuda_search`) are
listed by your client automatically after connecting.

## 🧩 Skills

[`skills/math-research/`](skills/math-research/) — a companion agent skill (SKILL.md
router + `workflows/` + `references/`) for mathematical research: **theorem hunting**
(check existing results via ProofWiki before reproving), **step-by-step proof
verification** with a rigor checklist, **counterexample hunting**, **literature
scans**, and **numeric sanity checks**. It uses this MCP's tools when connected and
falls back to manual search when not — see [`skills/README.md`](skills/README.md)
for the one-command install (copy the folder into your agent's skills directory).

## 🏗 Architecture

```
pyproject.toml                      ← uv package ([project.scripts] paper-research-mcp)
└── src/paper_research_mcp/
    ├── server.py                   ← MCP stdio entry (official `mcp` SDK, lowlevel Server)
    ├── registry.py                 ← 30 connectors, auth-gating, universal year post-filter
    ├── federation.py               ← search_papers: queries×sources parallel (pool 8), dedup, provenance
    ├── core.py                     ← httpx w/ timeout, standardized item schema, envelopes, year filter
    └── sources/
        ├── free.py        (11)  OpenAlex Crossref arXiv DOAJ S2 OpenReview INSPIRE ERIC Unpaywall ORCID PwC
        ├── indonesia.py    (8)  GARUDA SINTA OneSearch RAMA Moraref Neliti BRIN Google Scholar
        ├── china.py        (5)  NSSD Baidu Scholar AMiner ScienceDB CSTR
        ├── premium.py      (6)  ADS AlphaXiv Scopus Lens Dimensions WoS
        └── proofwiki.py    (1)  ProofWiki search/get (MediaWiki API, CC BY-SA)
```

## 🧪 Testing

```bash
uv run python tests/e2e_all_tools.py
```

Live suite with **38 checks**: all 36 tools one by one (envelope-shape validation +
per-category status expectations), all three federation modes, year-filter leak checks,
and the MCP stdio handshake in a subprocess. Scraper sources returning `blocked` count
as PASS — the envelope is the contract, not the network mood. Last run: **38/38 PASS**.

## 🚀 Publishing

```bash
# 1. Create a PyPI account → Account Settings → API token
# 2. Dry-run against TestPyPI (optional):
uv publish --publish-url https://test.pypi.org/legacy/ --token pypi-XXXXXXXX
# 3. Release:
uv build
uv publish --token pypi-XXXXXXXX
# 4. Anyone can now run it:
uvx paper-research-mcp
```

## 📄 License

MIT. Source of the connector plan: `Collection/Markdown/Refer/Reference.md`
(paper-search-mcp ecosystem + indonesia_research + China platforms + premium connectors).
