<div align="center">

# ScholarMesh

**MCP server untuk pencarian paper akademik federasi** — 40 sumber, 46 tools, satu
skema hasil yang seragam. Dulu namanya `paper-research-mcp`; kini dengan **Europe PMC,
PubMed, OpenAIRE, Zenodo, DataCite, OSF, zbMATH, Hugging Face Papers, CORE** + skill
pendamping riset (`skills/research`).

[![PyPI](https://img.shields.io/pypi/v/scholarmesh)](https://pypi.org/project/scholarmesh/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org)
[![MCP](https://img.shields.io/badge/protocol-MCP_2024--11--05-orange)](https://modelcontextprotocol.io)
[![Sources](https://img.shields.io/badge/sources-40-blueviolet)](#-connectors)
[![Tools](https://img.shields.io/badge/tools-46-brightgreen)](#-tools)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow)](#-license)

**🇬🇧 [English Version](README.md)**

</div>

---

## 📜 Apa itu ScholarMesh?

MCP server yang meneriarkan satu (atau banyak) keyword ke **40 sumber akademik secara
paralel**, mendedup hasil via DOI → title, dan menandai provenance (`alsoIn`,
`matchedQueries`). Tiap sumber punya connector-nya sendiri; federation layer ada di
atasnya. Di kode, sumber dikelompokkan per **fungsi** — negara cuma metadata
(`countries`) di tiap connector.

- 🔓 **Free-first** — 18 sumber jalan tanpa key sama sekali; 10 connector key baru
  aktif setelah env-nya diisi
- 🧵 **Federated** — `search_papers` fan-out, dedup, provenance
- 📅 **Batas tanggal** — `year_from`/`year_to` native di yang mendukung, post-filter
  universal di semua
- 🟢 **Gagal dengan jujur** — bot-wall balik envelope `blocked` terstruktur plus URL
  fallback manual, bukan error diam-diam
- 🏷 **Katalog terquery** — `list_sources` memaparkan kategori, disiplin, negara, dan
  status env per sumber

## 📦 Install

**Butuh:** [uv](https://docs.astral.sh/uv/). Tanpa API key untuk mulai.

```bash
uv tool install scholarmesh
```

Selesai — binary server `scholarmesh` sekarang ada di PATH lu. (Install lama
`paper-research-mcp` tetap jalan: paket ini mengirim alias command
`paper-research-mcp`. Nama PyPI lama deprecated dan tidak lagi diupdate.)

### Sambungkan ke client MCP lu

Tambahkan satu blok ke config MCP client lu, lalu **restart client**. Ini bentuk yang
sudah dites dan jalan (ZCode & client modern yang nerima bare server map):

```jsonc
{
  "scholarmesh": {
    "type": "stdio",
    "command": "uvx",
    "args": ["scholarmesh"]
  }
}
```

Client yang membungkus server di bawah key `mcpServers` (Claude Desktop, Cursor):

```jsonc
{
  "mcpServers": {
    "scholarmesh": { "command": "uvx", "args": ["scholarmesh"] }
  }
}
```

File config-nya di mana:

| Client | Lokasi config |
|---|---|
| **ZCode** | Settings → MCP servers |
| **Claude Desktop** | macOS: `~/Library/Application Support/Claude/claude_desktop_config.json` · Windows: `%APPDATA%\Claude\claude_desktop_config.json` |
| **Cursor** | `~/.cursor/mcp.json` (Settings → MCP) |
| **VS Code (Copilot)** | `.vscode/mcp.json` — server ditaruh di bawah key `"servers"` |
| **Codex CLI** | `~/.codex/config.toml` → `[mcp_servers.scholarmesh]` dengan `command = "uvx"`, `args = ["scholarmesh"]` |

Sudah `uv tool install` dan binary-nya ada di PATH client lu? Nunjuk langsung juga
bisa: `"command": "scholarmesh"` (bentuk `type`/`args` sama).

**Cek:** restart client — semua 46 tool muncul otomatis. Dari terminal juga bisa
probe: `scholarmesh` mencetak `46 tools, 40 sources ready (stdio)` lalu menunggu
(Ctrl+C untuk keluar).

**Update / hapus:**

```bash
uv tool upgrade scholarmesh
uv tool uninstall scholarmesh
```

**Dari checkout lokal (development):** `uv run scholarmesh` di dalam folder repo,
atau arahkan client ke `uv --directory <path>/ScholarMesh run scholarmesh`. Lihat
[CONTRIBUTING.md](CONTRIBUTING.md).

## 🚀 Usage

Connect, lalu tinggal minta agent lu dengan bahasa sehari-hari:

| Lu minta | Yang jalan |
|---|---|
| *"Survey paper 2024+ soal LLM watermarking **dan** deteksi teks AI — semua sumber free"* | `search_papers` dengan parallel `queries:[]` + `year_from`, dedup lintas sumber |
| *"Cari bukti teorema Pythagoras beserta prasyaratnya"* | `proofwiki_search` → `proofwiki_get` |
| *"Full text paper ini: PMC7159299"* | `europepmc_fulltext` (JATS XML OA → teks) |
| *"Paper biomed soal CRISPR base editing, 2025+ saja"* | `europepmc_search` / `pubmed_search` dengan filter tahun |
| *"Reviewer bilang apa soal submission OpenReview ini?"* | `openreview_search` → `openreview_notes` |
| *"Cari implementasi kode paper image-classification"* | `pwc_search` |
| *"Resolve DOI ini dan cari salinan open-access"* | `crossref_doi` → `unpaywall_resolve` |
| *"Cari jurnal Indonesia soal pertanian"* | `garuda_search` / `neliti_search` / `brin_search` |
| *"Paper matematika soal Ricci flow"* | `zbmath_search` |

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

18 sumber jalan tanpa key. Sumber key-gated baru aktif setelah env-nya diisi (lihat
[`.env.example`](.env.example)):

| Env var | Sumber | Catatan |
|---|---|---|
| `S2_API_KEY` | Semantic Scholar | menghilangkan batas 429 |
| `OPENALEX_API_KEY` | OpenAlex | jatah harian jadi milik sendiri |
| `NCBI_API_KEY` | PubMed E-utilities | 3 → 10 req/s (registrasi gratis) |
| `UNPAYWALL_EMAIL` | Unpaywall | email politeness (opsional) |
| `CORE_API_KEY` | CORE | **registrasi gratis** — full-text OA terdalam |
| `ADS_TOKEN` | NASA ADS | gratis untuk peneliti |
| `ALPHAXIV_API_KEY` | alphaXiv | ATAU langsung pakai MCP resmi: https://api.alphaxiv.org/mcp/v1 |
| `SCOPUS_API_KEY` | Scopus | perlu entitlement institusi juga |
| `LENS_TOKEN`, `DIMENSIONS_TOKEN`, `WOS_API_KEY` | Lens, Dimensions, WoS | berbasis langganan/approval |
| `BAIDU_API_KEY`, `AMINER_API_KEY`, `CSTR_CLIENT_ID`+`CSTR_SECRET` | Baidu, AMiner, CSTR | platform China |

## 🌐 Sumber (40)

| Kategori | Sumber |
|---|---|
| **FREE** (18, default on) | OpenAlex · Crossref · arXiv · DOAJ · OpenReview · Hugging Face Papers · Unpaywall · Zenodo · DataCite · OSF · OpenAIRE · INSPIRE-HEP · ERIC · zbMATH Open · Europe PMC · PubMed · NSSD (SSH China) · ORCID |
| **FREE, bot-wall** (12, default on, error jujur) | Semantic Scholar · Papers with Code · Google Scholar · GARUDA · SINTA · OneSearch · RAMA · Moraref · Neliti · BRIN · ProofWiki (bukti matematika) · ScienceDB |
| **API KEY** (10, baru aktif setelah env diisi) | CORE (registrasi gratis) · NASA ADS · AlphaXiv · Scopus · The Lens · Dimensions · Web of Science · Baidu Scholar · AMiner · CSTR |

> 🇮🇩🇨🇳 Sumber regional (Indonesia `ID`, China `CN`) adalah connector biasa yang
> metadata `countries`-nya menyebut asalnya — tiap sumber juga membawa metadata
> `disciplines` (bisa difilter via `list_sources`).

## 🛠 Tools

**46 tools** otomatis terdeteksi oleh client MCP lewat `tools/list`. Tiga entry point
yang penting:

- `search_papers` — pencarian federasi. Mendukung `query` tunggal atau parallel
  `queries: ["k1", "k2"]`, batas tanggal `year_from`/`year_to`, pemilihan sumber,
  dedup DOI → title, dan provenance (`alsoIn` + `matchedQueries`).
- `list_sources` — semua sumber: kategori, disiplin, negara, status env.
- `europepmc_fulltext` — full-text OA (JATS XML → teks bersih) satu PMCID.

Tools per sumber (misalnya `openalex_search`, `pubmed_search`, `zbmath_search`,
`proofwiki_get`, `garuda_search`) muncul otomatis di client setelah terhubung.

## 🧩 Skills

[`skills/research/`](skills/research/) — skill agent pendamping (SKILL.md router +
`workflows/` + `references/`) untuk kerja riset di semua bidang: **survei literatur**
(rute sumber per bidang), **verifikasi klaim**, **verifikasi bukti & argumen**
(matematika, logika, CS, hukum, filosofi), **hunting counterexample/falsifikasi**, dan
**sanity check numerik**. Skill ini memakai tools ScholarMesh saat terhubung dan
fallback ke pencarian manual saat tidak — install satu perintah ada di
[`skills/README.md`](skills/README.md).

## 🏗 Arsitektur

```
pyproject.toml                ← paket uv ([project.scripts] scholarmesh)
└── src/scholarmesh/
    ├── server.py             ← pintu masuk MCP stdio (SDK `mcp` resmi, lowlevel Server)
    ├── registry.py           ← daftar SOURCES flat, auth-gating, post-filter tahun universal
    ├── federation.py         ← search_papers: queries×sources paralel (pool 8), dedup, provenance
    ├── core.py               ← httpx dengan timeout, skema item standar, envelope, year filter
    └── sources/              ← dikelompokkan per FUNGSI; negara = metadata per sumber
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

Suite live berisi ~48 pengecekan: seluruh 44 tool connector satu per satu, validasi
bentuk envelope, ekspektasi status per kategori, ketiga mode federasi, cek kebocoran
filter tahun, dan handshake protokol MCP stdio di subprocess. Hasil terakhir:
**47/47 PASS** (1 pengecekan conditional sengaja di-skip).

Tool scraper yang `blocked` (bot-wall, maintenance, DNS) dihitung PASS. Kontraknya
adalah envelope yang benar, bukan mood jaringan.

## 🤝 Kontribusi

Lihat [CONTRIBUTING.md](CONTRIBUTING.md) — cara menjalankan test, menambah sumber,
dan proses rilis.

## 📄 License

MIT. Rencana connector disaring dari `Collection/Markdown/Refer/Reference.md`
(ekosistem paper-search-mcp + indonesia_research + platform China + connector premium)
plus tambahan yang diverifikasi live (Europe PMC, PubMed, OpenAIRE, Zenodo, DataCite,
OSF, zbMATH, HF Papers, CORE).
