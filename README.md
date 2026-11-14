<div align="center">

# Paper-Research-MCP

**Federated academic research retrieval over MCP** — 31 connectors, 36 tools,
one standardized result schema. Now with **ProofWiki** + a companion research
skill (`skills/research`).

[![PyPI](https://img.shields.io/pypi/v/paper-research-mcp)](https://pypi.org/project/paper-research-mcp/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org)
[![MCP](https://img.shields.io/badge/protocol-MCP_2024--11--05-orange)](https://modelcontextprotocol.io)
[![Connectors](https://img.shields.io/badge/connectors-31-blueviolet)](#-connectors)
[![Tools](https://img.shields.io/badge/tools-36-brightgreen)](#-tools)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow)](#-license)

**🇮🇩 [Versi Bahasa Indonesia](https://github.com/DranxX/Paper-Research-MCP/blob/main/README_ID.md)**

</div>

---

## 📜 What is Paper-Research-MCP?

A brand-new **MCP server for academic paper search**: 31 sources behind 36 tools
with one standardized result schema — multi-source discovery, conference peer
reviews, paper↔code mapping, DOI/OA resolution, and a federation layer on top that
searches many sources at once, deduplicates, and tracks provenance.

- 🔓 **Free-first** — everything works without an API key; premium connectors wake
  up only if you set their env vars
- 🧵 **Federated** — `search_papers` fans one or many keywords out to every source
  in parallel, dedups by DOI → title, tags `alsoIn` (sources) and `matchedQueries`
  (keywords) per result
- 📅 **Date-bounded** — `year_from`/`year_to` enforced natively where the API
  supports it, universally everywhere else
- 🟢 **Honest failures** — bot-walls and rate limits come back as structured
  envelopes with a manual-fallback URL, never silent lies

Sources: OpenAlex, Crossref, arXiv, DOAJ, OpenReview, INSPIRE-HEP, ERIC, Unpaywall,
ORCID, Papers with Code, Semantic Scholar, ProofWiki (math proofs), NSSD/Baidu
Scholar/AMiner/ScienceDB (China), GARUDA/SINTA/OneSearch/RAMA/Moraref/Neliti/BRIN
(Indonesia), Google Scholar, and premium ones (ADS, AlphaXiv, Scopus, Lens,
Dimensions, WoS). Full table below.

## 📦 Install

**Requires:** [uv](https://docs.astral.sh/uv/). No API key needed to start.

```bash
uv tool install paper-research-mcp
```

That's it — the server binary `paper-research-mcp` is now on your PATH.

### Connect it to your MCP client

Add one block to your client's MCP config, then **restart the client**. This is the
tested, working shape (ZCode & modern clients that take a bare server map):

```jsonc
{
  "paper-research": {
    "type": "stdio",
    "command": "uvx",
    "args": ["paper-research-mcp"]
  }
}
```

Clients that wrap servers under a `mcpServers` key (Claude Desktop, Cursor):

```jsonc
{
  "mcpServers": {
    "paper-research": { "command": "uvx", "args": ["paper-research-mcp"] }
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
| **Codex CLI** | `~/.codex/config.toml` → `[mcp_servers.paper-research]` with `command = "uvx"`, `args = ["paper-research-mcp"]` |

Already `uv tool install`ed and the binary is on your client's PATH? Pointing
straight at it also works: `"command": "paper-research-mcp"` (same `type`/`args`
shape as above).

**Verify:** restart your client — all 36 tools appear automatically. From a
terminal you can also probe it: `paper-research-mcp` prints
`36 tools, 5 connector packs ready (stdio)` and waits (Ctrl+C exits).

**Update / remove:**

```bash
uv tool upgrade paper-research-mcp
uv tool uninstall paper-research-mcp
```

**From a local checkout (development):** `uv run paper-research-mcp` inside the
repo, or point the client at `uv --directory <path>/Paper-Research-MCP run
paper-research-mcp`. See [CONTRIBUTING.md](CONTRIBUTING.md).

## 🚀 Usage

Connect, then just ask your agent in plain language:

| You ask | What runs |
|---|---|
| *"Survey 2024+ work on LLM watermarking **and** detecting AI-generated text — all free sources"* | `search_papers` with parallel `queries:[]` + `year_from`, cross-source dedup |
| *"Find the proof of the Pythagorean theorem and its prerequisites"* | `proofwiki_search` → `proofwiki_get` |
| *"What did reviewers say about this OpenReview submission?"* | `openreview_search` → `openreview_notes` |
| *"Find code implementations of image-classification papers"* | `pwc_search` |
| *"Resolve this DOI and find an open-access copy"* | `crossref_doi` → `unpaywall_resolve` |
| *"Cari jurnal Indonesia soal pertanian"* | `garuda_search` / `neliti_search` / `brin_search` |
| *"Physics papers mentioning muon g-2"* | `inspire_search` |

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

[`skills/research/`](skills/research/) — a companion agent skill (SKILL.md router +
`workflows/` + `references/`) for research-grade work in any field: **literature
scans** (field→source routing across all 31 connectors), **claim verification** (is
a claimed result real, and what's its actual status), **proof & argument
verification** — math, formal logic, CS correctness, legal reasoning, philosophy —
with a rigor checklist that separates validity from soundness, **counterexample /
falsification hunts** (formal, doctrinal, empirical), and **numeric sanity
checks**. It uses this MCP's tools when connected and falls back to manual search
when not — see [`skills/README.md`](skills/README.md) for the one-command install
(copy the folder into your agent's skills directory).

## 🏗 Architecture

```
pyproject.toml                      ← uv package ([project.scripts] paper-research-mcp)
└── src/paper_research_mcp/
    ├── server.py                   ← MCP stdio entry (official `mcp` SDK, lowlevel Server)
    ├── registry.py                 ← 31 connectors, auth-gating, universal year post-filter
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

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) — how to run the tests, add a connector, and
the release process.

## 📄 License

MIT. Source of the connector plan: `Collection/Markdown/Refer/Reference.md`
(paper-search-mcp ecosystem + indonesia_research + China platforms + premium connectors).
