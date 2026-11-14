<div align="center">

# Paper-Research-MCP

**MCP server untuk pencarian paper akademik** — 30 connector, 34 tools, satu skema hasil
yang seragam.

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org)
[![MCP](https://img.shields.io/badge/protocol-MCP_2024--11--05-orange)](https://modelcontextprotocol.io)
[![Connectors](https://img.shields.io/badge/connectors-30-blueviolet)](#-connectors)
[![Tools](https://img.shields.io/badge/tools-34-brightgreen)](#-tools)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow)](#-license)

**🇬🇧 [English Version](README.md)** · **📦 [PyPI](https://pypi.org/project/paper-research-mcp/)**

</div>

---

## 📜 Apa itu Paper-Research-MCP?

Server MCP untuk mencari paper akademik dari banyak sumber sekaligus. Rencana connector-nya
disaring dari dokumen `Refer/Reference.md`. Tujuannya: riset lewat agent jadi lebih luas,
bukan cuma lebih dalam.

Aturan desain utamanya: **jangan samakan semua sumber jadi satu `search_papers()`**. Tiap
sumber punya connector sendiri dengan tools-nya sendiri (discovery, conference review,
paper↔code mapping, metadata resolution, resolusi open-access). Di atasnya ada federation
layer untuk pencarian lintas sumber, deduplikasi, dan provenance.

- 🔓 **Free-first** — semua connector jalan tanpa API key. Connector premium terdaftar,
  tapi baru aktif setelah env-nya diisi.
- 🧵 **Federated** — pencarian lintas sumber dengan dedup DOI → title. Hasil membawa
  provenance: `alsoIn` (sumber) dan `matchedQueries` (keyword).
- 📅 **Batas tanggal** — `year_from`/`year_to` diteruskan langsung ke API yang mendukung
  (OpenAlex, Crossref, arXiv, Semantic Scholar). Sumber lain melewati post-filter.
- 📦 **Dikemas dengan uv** — Python 3.10+, dependensi hanya `mcp` dan `httpx`.
- 🟢 **Gagal dengan jujur** — bot-wall dan rate limit dikembalikan sebagai envelope
  terstruktur plus saran fallback manual, bukan error diam-diam.

## 📦 Install

Butuh Python 3.10 ke atas dan [uv](https://docs.astral.sh/uv/). Dependensinya hanya `mcp`
dan `httpx`.

**Dari PyPI** — setelah paket ini rilis:

```jsonc
// ZCode / Claude Desktop / Cursor / client MCP apa pun
{
  "mcpServers": {
    "paper-research": { "command": "uvx", "args": ["paper-research-mcp"] }
  }
}
```

**Dari checkout lokal** — tanpa publish:

```jsonc
{
  "mcpServers": {
    "paper-research": {
      "command": "uv",
      "args": ["--directory", "<path>/Paper-Research-MCP", "run", "paper-research-mcp"]
    }
  }
}
```

## 🔑 API key opsional

Semua connector free jalan tanpa key. Connector premium baru aktif setelah env-nya diisi
(lihat [`.env.example`](.env.example)):

| Env var | Connector | Catatan |
|---|---|---|
| `S2_API_KEY` | Semantic Scholar | menghilangkan batas 429 |
| `OPENALEX_API_KEY` | OpenAlex | jatah harian jadi milik sendiri |
| `ADS_TOKEN` | NASA ADS | gratis untuk peneliti |
| `ALPHAXIV_API_KEY` | AlphaXiv | atau tambahkan [MCP resmi mereka](https://api.alphaxiv.org/mcp/v1) langsung |
| `SCOPUS_API_KEY` | Scopus | butuh entitlement institusi |
| `LENS_TOKEN`, `DIMENSIONS_TOKEN`, `WOS_API_KEY` | Lens, Dimensions, WoS | berbasis langganan |
| `BAIDU_API_KEY`, `AMINER_API_KEY`, `CSTR_CLIENT_ID` + `CSTR_SECRET` | Baidu, AMiner, CSTR | platform China |

## 🌐 Connectors

| Kategori | Sumber |
|---|---|
| **FREE** (default on) | OpenAlex · Crossref · arXiv · DOAJ · OpenReview · INSPIRE-HEP · ERIC · Unpaywall · ORCID · NSSD (SSH China) · ScienceDB |
| **FREE, bot-wall/rate-limit** (default on, error jujur) | Semantic Scholar · Papers with Code · Google Scholar · Baidu Scholar · GARUDA · SINTA · OneSearch · RAMA · Moraref · Neliti · BRIN |
| **API KEY** (baru aktif setelah env diisi) | NASA ADS · AlphaXiv · Scopus · The Lens · Dimensions · Web of Science · AMiner · CSTR |

> 🇮🇩 Blok `indonesia_research` mengikuti peringatan Reference.md: platform ini tidak punya
> API resmi. Connector-nya scraper best-effort, dan kegagalannya dilaporkan apa adanya.

## 🛠 Tools

**34 tools** otomatis terdeteksi oleh client MCP lewat `tools/list`. Tidak perlu konfigurasi
tambahan. Dua entry point yang penting:

- `search_papers` — pencarian federasi. Mendukung `query` tunggal atau parallel
  `queries: ["k1", "k2"]`, batas tanggal `year_from`/`year_to`, pemilihan sumber, dedup
  DOI → title, dan provenance (`alsoIn` + `matchedQueries`).
- `list_sources` — daftar semua connector, kategori aksesnya, dan status env.

Tools per sumber (misalnya `openalex_search`, `openreview_notes`, `garuda_search`) muncul
otomatis di client setelah terhubung.

## 🏗 Arsitektur

```
pyproject.toml                      ← paket uv ([project.scripts] paper-research-mcp)
└── src/paper_research_mcp/
    ├── server.py                   ← pintu masuk MCP stdio (SDK `mcp` resmi, lowlevel Server)
    ├── registry.py                 ← 30 connector, auth-gating, post-filter tahun universal
    ├── federation.py               ← search_papers: queries×sources paralel (pool 8), dedup, provenance
    ├── core.py                     ← httpx dengan timeout, skema item standar, envelope, year filter
    └── sources/
        ├── free.py        (11)  OpenAlex Crossref arXiv DOAJ S2 OpenReview INSPIRE ERIC Unpaywall ORCID PwC
        ├── indonesia.py    (8)  GARUDA SINTA OneSearch RAMA Moraref Neliti BRIN Google Scholar
        ├── china.py        (5)  NSSD Baidu Scholar AMiner ScienceDB CSTR
        └── premium.py      (6)  ADS AlphaXiv Scopus Lens Dimensions WoS
```

## 🧪 Testing

```bash
uv run python tests/e2e_all_tools.py
```

Suite live berisi 36 pengecekan: seluruh 34 tool satu per satu, validasi bentuk envelope,
ekspektasi status per kategori, ketiga mode federasi, cek kebocoran filter tahun, dan
handshake protokol MCP stdio di subprocess. Hasil terakhir: 36/36 PASS.

Tool scraper yang `blocked` (bot-wall, maintenance, DNS) dihitung PASS. Kontraknya adalah
envelope yang benar, bukan mood jaringan.

## 🚀 Publishing

```bash
# 1. Buat akun PyPI → Account Settings → API token
# 2. Dry-run ke TestPyPI (opsional):
uv publish --publish-url https://test.pypi.org/legacy/ --token pypi-XXXX
# 3. Rilis:
uv build
uv publish --token pypi-XXXX
# 4. Setelah itu siapa pun bisa langsung jalankan:
uvx paper-research-mcp
```

Rilis otomatis dari GitHub juga bisa lewat Trusted Publishing — lihat
[`.github/workflows/publish.yml`](.github/workflows/publish.yml).

## 📄 License

MIT. Sumber rencana connector: `Refer/Reference.md` — ekosistem paper-search-mcp,
blok `indonesia_research`, platform China, dan connector premium.
