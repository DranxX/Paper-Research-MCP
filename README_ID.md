<div align="center">

# Paper-Research-MCP

**MCP server untuk pencarian paper akademik** — 31 connector, 36 tools, satu skema hasil
yang seragam. Kini dengan **ProofWiki** + skill pendamping riset (`skills/research`).

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org)
[![MCP](https://img.shields.io/badge/protocol-MCP_2024--11--05-orange)](https://modelcontextprotocol.io)
[![Connectors](https://img.shields.io/badge/connectors-31-blueviolet)](#-connectors)
[![Tools](https://img.shields.io/badge/tools-36-brightgreen)](#-tools)
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
dan `httpx`. Tanpa API key untuk mulai.

**Dari PyPI** — tambahkan satu blok ke config client MCP lu (ZCode / Claude Desktop /
Cursor / client MCP apa pun):

```jsonc
{
  "mcpServers": {
    "paper-research": { "command": "uvx", "args": ["paper-research-mcp"] }
  }
}
```

<details>
<summary>Alternatif: yang install via <code>uv tool install paper-research-mcp</code></summary>

Arahkan client ke binary yang sudah terinstall:

```jsonc
{ "mcpServers": { "paper-research": { "command": "paper-research-mcp" } } }
```

Catatan WSL: binary ada di `~/.local/bin/` — client Windows bisa panggil lewat
`wsl.exe` atau pakai varian `uvx` di atas.
</details>

<details>
<summary>Checkout lokal (untuk development)</summary>

```jsonc
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
</details>

## 🚀 Usage

Connect, restart client lu — semua 36 tool terdeteksi otomatis (`tools/list`), tanpa
konfigurasi tambahan. Lalu tinggal minta agent lu dengan bahasa sehari-hari:

| Lu minta | Yang jalan |
|---|---|
| *"Survey paper 2024+ soal LLM watermarking **dan** deteksi teks AI — semua sumber free"* | `search_papers` dengan parallel `queries:[]` + `year_from`, dedup lintas sumber |
| *"Cari bukti teorema Pythagoras beserta prasyaratnya"* | `proofwiki_search` → `proofwiki_get` |
| *"Reviewer bilang apa soal submission OpenReview ini?"* | `openreview_search` → `openreview_notes` |
| *"Cari implementasi kode paper image-classification"* | `pwc_search` |
| *"Resolve DOI ini dan cari salinan open-access"* | `crossref_doi` → `unpaywall_resolve` |
| *"Cari jurnal Indonesia soal pertanian"* | `garuda_search` / `neliti_search` / `brin_search` |
| *"Paper fisika soal muon g-2"* | `inspire_search` |

<details>
<summary>Contoh respons (dipotong)</summary>

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

`alsoIn` = sumber lain yang juga memuat paper yang sama (sudah didedup),
`matchedQueries` = keyword lu yang mana yang match. Sumber bot-wall balik sebagai
`{"status": "blocked"}` plus URL fallback manual — jujur, bukan error diam-diam.
</details>

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
| **FREE, bot-wall/rate-limit** (default on, error jujur) | Semantic Scholar · Papers with Code · Google Scholar · Baidu Scholar · GARUDA · SINTA · OneSearch · RAMA · Moraref · Neliti · BRIN · ProofWiki (bukti matematika) |
| **API KEY** (baru aktif setelah env diisi) | NASA ADS · AlphaXiv · Scopus · The Lens · Dimensions · Web of Science · AMiner · CSTR |

> 🇮🇩 Blok `indonesia_research` mengikuti peringatan Reference.md: platform ini tidak punya
> API resmi. Connector-nya scraper best-effort, dan kegagalannya dilaporkan apa adanya.

## 🛠 Tools

**36 tools** otomatis terdeteksi oleh client MCP lewat `tools/list`. Tidak perlu konfigurasi
tambahan. Tiga entry point yang penting:

- `search_papers` — pencarian federasi. Mendukung `query` tunggal atau parallel
  `queries: ["k1", "k2"]`, batas tanggal `year_from`/`year_to`, pemilihan sumber, dedup
  DOI → title, dan provenance (`alsoIn` + `matchedQueries`).
- `list_sources` — daftar semua connector, kategori aksesnya, dan status env.

Sumber matematika: `proofwiki_search` / `proofwiki_get` (ProofWiki — definisi, teorema,
bukti lengkap; Cloudflare best-effort dengan envelope `blocked` yang jujur).

Tools per sumber (misalnya `openalex_search`, `openreview_notes`, `garuda_search`) muncul
otomatis di client setelah terhubung.

## 🧩 Skills

[`skills/research/`](skills/research/) — skill agent pendamping (SKILL.md router +
`workflows/` + `references/`) untuk kerja riset di semua bidang: **survei literatur**
(rute sumber per bidang ke seluruh 31 connector), **verifikasi klaim** (apakah hasil
yang diklaim benar-benar ada dan apa statusnya), **verifikasi bukti & argumen** —
matematika, logika formal, correctness CS, penalaran hukum, filosofi — dengan rigor
checklist yang memisahkan validitas dari soundness, **hunting
counterexample/falsifikasi** (formal, doktrinal, empiris), dan **sanity check
numerik**. Skill ini memakai tools MCP ini saat terhubung dan fallback ke pencarian
manual saat tidak — install satu perintah ada di
[`skills/README.md`](skills/README.md) (salin folder skill ke direktori skills agent-mu).

## 🏗 Arsitektur

```
pyproject.toml                      ← paket uv ([project.scripts] paper-research-mcp)
└── src/paper_research_mcp/
    ├── server.py                   ← pintu masuk MCP stdio (SDK `mcp` resmi, lowlevel Server)
    ├── registry.py                 ← 31 connector, auth-gating, post-filter tahun universal
    ├── federation.py               ← search_papers: queries×sources paralel (pool 8), dedup, provenance
    ├── core.py                     ← httpx dengan timeout, skema item standar, envelope, year filter
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

Suite live berisi 38 pengecekan: seluruh 36 tool satu per satu, validasi bentuk envelope,
ekspektasi status per kategori, ketiga mode federasi, cek kebocoran filter tahun, dan
handshake protokol MCP stdio di subprocess. Hasil terakhir: 38/38 PASS.

Tool scraper yang `blocked` (bot-wall, maintenance, DNS) dihitung PASS. Kontraknya adalah
envelope yang benar, bukan mood jaringan.

## 🤝 Kontribusi

Lihat [CONTRIBUTING.md](CONTRIBUTING.md) — cara menjalankan test, menambah connector,
dan proses rilis.

## 📄 License

MIT. Sumber rencana connector: `Refer/Reference.md` — ekosistem paper-search-mcp,
blok `indonesia_research`, platform China, dan connector premium.
