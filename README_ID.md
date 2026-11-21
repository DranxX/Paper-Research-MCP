<div align="center">

# 🎓 ScholarMesh

### *Satu query. Empat puluh sumber akademik. Nol API key buat mulai.*

**MCP server untuk pencarian paper akademik federasi** — teriarkan satu (atau banyak)
keyword ke 40 sumber scholarly secara paralel, dedup via DOI, provenance terjaga, dan
kegagalan yang jujur saat sebuah sumber bilang tidak.

[![PyPI](https://img.shields.io/pypi/v/scholarmesh)](https://pypi.org/project/scholarmesh/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org)
[![MCP](https://img.shields.io/badge/protocol-MCP_2024--11--05-orange)](https://modelcontextprotocol.io)
[![Sources](https://img.shields.io/badge/sources-40-8A2BE2)](#-40-sumber--46-tools)
[![Tools](https://img.shields.io/badge/tools-46-brightgreen)](#-40-sumber--46-tools)
[![Tests](https://img.shields.io/badge/e2e-47%20PASS-success)](#-testing)
[![License](https://img.shields.io/badge/license-MIT-yellow)](#-license)

[🇬🇧 English](README.md) · **🇮🇩 Bahasa Indonesia** · [📦 PyPI](https://pypi.org/project/scholarmesh/)

</div>

---

## ✨ Kenapa ScholarMesh?

| | |
|---|---|
| 🧵 **Federated sejak desain** | `search_papers` menjalankan 1–8 keyword × 30+ sumber **paralel** (pool 8), dedup via DOI → judul ternormalisasi, dan menandai tiap hasil dengan `alsoIn` (muncul di sumber mana saja) dan `matchedQueries` (keyword mana yang kena) |
| 🔓 **Free-first** | 18 sumber jalan **tanpa key sama sekali**; 10 lagi terbuka dengan registrasi gratis; index premium tidur sampai env lu diisi |
| 📅 **Batas tanggal di mana pun** | `year_from` / `year_to` dipass native ke API yang mendukung dan jadi post-filter universal di yang lain — tanpa kebocoran |
| 🏷 **Katalog yang bisa diquery** | tiap sumber bawa metadata `category` (free / bot-wall / key), `disciplines`, dan `countries` — `list_sources` memfilter ketiganya |
| 🟢 **Gagal dengan jujur** | bot-wall dan rate limit balik sebagai envelope `blocked` terstruktur **plus URL fallback manual** — bukan kebohongan diam-diam |
| 🧩 **Skill agent ikut dikirim** | `skills/research` — survei literatur, verifikasi klaim, verifikasi bukti & argumen, hunting falsifikasi, sanity check numerik |

---

## 🚀 Mulai dalam 60 detik

**Langkah 1 — install** (butuh [uv](https://docs.astral.sh/uv/)):

```bash
uv tool install scholarmesh
```

**Langkah 2 — sambungkan** ke client MCP lu, lalu restart client:

```jsonc
// ZCode & client modern (bentuk yang sudah dites)
{
  "scholarmesh": {
    "type": "stdio",
    "command": "uvx",
    "args": ["scholarmesh"]
  }
}
```

<details>
<summary><b>Client lain</b> — Claude Desktop, Cursor, VS Code, Codex CLI</summary>

```jsonc
// Claude Desktop & Cursor (pembungkus mcpServers)
{
  "mcpServers": {
    "scholarmesh": { "command": "uvx", "args": ["scholarmesh"] }
  }
}
```

| Client | Lokasi config |
|---|---|
| **ZCode** | Settings → MCP servers |
| **Claude Desktop** | macOS: `~/Library/Application Support/Claude/claude_desktop_config.json` · Windows: `%APPDATA%\Claude\claude_desktop_config.json` |
| **Cursor** | `~/.cursor/mcp.json` (Settings → MCP) |
| **VS Code (Copilot)** | `.vscode/mcp.json` — server ditaruh di bawah key `"servers"` |
| **Codex CLI** | `~/.codex/config.toml` → `[mcp_servers.scholarmesh]` dengan `command = "uvx"`, `args = ["scholarmesh"]` |

Aplikasi GUI sering tidak mewarisi PATH shell lu — bentuk `uvx` di atas langsung
melewati masalah itu. Sudah `uv tool install`? `"command": "scholarmesh"` juga bisa.

</details>

**Langkah 3 — cek & pakai.** Restart client dan semua **46 tools** muncul otomatis
(`tools/list`). Dari terminal juga bisa diprobe:

```bash
scholarmesh           # mencetak: 46 tools, 40 sources ready (stdio) — Ctrl+C keluar
uv tool upgrade scholarmesh
uv tool uninstall scholarmesh
```

## 💬 Apa saja yang bisa lu *tanyakan*

| Lu bilang | ScholarMesh menjalankan |
|---|---|
| *"Survey paper 2024+ soal LLM watermarking **dan** deteksi teks AI — semua sumber free"* | `search_papers` — parallel `queries:[]` + `year_from`, dedup lintas sumber |
| *"Full text PMC7159299"* | `europepmc_fulltext` — JATS XML OA → teks bersih |
| *"Paper biomed soal CRISPR base editing, 2025+"* | `europepmc_search` / `pubmed_search` + filter tahun |
| *"Bukti teorema Pythagoras + prasyaratnya"* | `proofwiki_search` → `proofwiki_get` |
| *"Paper matematika soal Ricci flow"* | `zbmath_search` (review berkode MSC) |
| *"Kata reviewer soal submission OpenReview ini?"* | `openreview_search` → `openreview_notes` |
| *"Implementasi kode paper image-classification"* | `pwc_search` |
| *"Resolve DOI ini + cari salinan OA"* | `crossref_doi` → `unpaywall_resolve` |
| *"Cari jurnal Indonesia soal pertanian"* | `garuda_search` / `neliti_search` / `brin_search` |

<details>
<summary>📦 Bentuk hasil sebenarnya (dipotong)</summary>

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

Semua tool balik dengan **envelope yang sama**: `status · source · count · items[] · meta`.
`alsoIn` = sumber lain yang memuat paper yang sama (didedup); `matchedQueries` =
keyword lu yang mana yang match. Sumber bot-wall balik `{"status": "blocked"}`
beserta URL fallback manual.
</details>

## 🌐 40 sumber · 46 tools

| Kategori | Sumber |
|---|---|
| 🟢 **FREE** — 18, default on | OpenAlex · Crossref · arXiv · DOAJ · OpenReview · Hugging Face Papers · Unpaywall · Zenodo · DataCite · OSF · OpenAIRE · INSPIRE-HEP · ERIC · zbMATH Open · Europe PMC · PubMed · NSSD (SSH China) · ORCID |
| 🟡 **FREE, bot-wall** — 12, default on, error jujur | Semantic Scholar · Papers with Code · Google Scholar · GARUDA 🇮🇩 · SINTA 🇮🇩 · OneSearch 🇮🇩 · RAMA 🇮🇩 · Moraref 🇮🇩 · Neliti 🇮🇩 · BRIN 🇮🇩 · ProofWiki · ScienceDB 🇨🇳 |
| 🔑 **API KEY** — 10, tidur sampai env diisi | CORE *(registrasi gratis)* · NASA ADS · AlphaXiv · Scopus · The Lens · Dimensions · Web of Science · Baidu Scholar 🇨🇳 · AMiner 🇨🇳 · CSTR 🇨🇳 |

<details>
<summary><b>Daftar 46 tools</b></summary>

| Kelompok | Tools |
|---|---|
| Federation | `search_papers` · `list_sources` |
| Indexes | `openalex_search` · `crossref_search` · `crossref_doi` · `doaj_search` · `semantic_scholar_search` · `lens_search` ᵏ · `dimensions_search` ᵏ · `scopus_search` ᵏ · `wos_search` ᵏ |
| Preprints | `arxiv_search` · `openreview_search` · `openreview_notes` · `alphaxiv_search` ᵏ · `hf_search` |
| Archives | `unpaywall_resolve` · `zenodo_search` · `datacite_search` · `osf_search` · `openaire_search` · `core_search` ᵏ |
| Domain | `inspire_search` · `eric_search` · `zbmath_search` · `proofwiki_search` · `proofwiki_get` · `pwc_search` · `europepmc_search` · `europepmc_fulltext` · `pubmed_search` · `ads_search` ᵏ |
| Regional | `garuda_search` · `sinta_search` · `onesearch_search` · `rama_search` · `moraref_search` · `neliti_search` · `brin_search` · `google_scholar_search` · `nssd_search` · `baidu_scholar_search` ᵏ · `aminer_search` ᵏ · `sciencedb_search` · `cstr_resolve` ᵏ |
| People | `orcid_works` |

ᵏ = butuh env var (lihat di bawah)
</details>

<details>
<summary><b>🔑 API key</b> — semuanya opsional; 18 sumber butuh nol</summary>

| Env var | Sumber | Catatan |
|---|---|---|
| `S2_API_KEY` | Semantic Scholar | menghilangkan batas 429 |
| `OPENALEX_API_KEY` | OpenAlex | budget harian sendiri |
| `NCBI_API_KEY` | PubMed E-utilities | 3 → 10 req/s (registrasi gratis) |
| `UNPAYWALL_EMAIL` | Unpaywall | email politeness (opsional) |
| `CORE_API_KEY` | CORE | **registrasi gratis** — full-text OA terdalam |
| `ADS_TOKEN` | NASA ADS | gratis untuk peneliti |
| `ALPHAXIV_API_KEY` | AlphaXiv | atau tambahkan [MCP resmi mereka](https://api.alphaxiv.org/mcp/v1) langsung |
| `SCOPUS_API_KEY` | Scopus | butuh entitlement institusi |
| `LENS_TOKEN` / `DIMENSIONS_TOKEN` / `WOS_API_KEY` | Lens / Dimensions / WoS | berbasis langganan/approval |
| `BAIDU_API_KEY` / `AMINER_API_KEY` / `CSTR_CLIENT_ID`+`CSTR_SECRET` | Baidu / AMiner / CSTR | platform China |

Hubungkan lewat blok `env` di client lu atau [`.env.example`](.env.example).
</details>

## 🧩 Skill pendamping: `research`

[`skills/research/`](skills/research/) dikirim bareng repo — salin ke direktori skills
agent lu dan skill ini auto-trigger pada tugas riset:

- 🔎 **Survei literatur** — rute sumber per bidang, dua jendela waktu, reading order, temuan gap
- ✅ **Verifikasi klaim** — apakah hasil yang diklaim ada, dan apa *status aslinya*?
- 🧮 **Verifikasi bukti & argumen** — matematika, logika formal, correctness CS, penalaran hukum, filosofi — validitas vs soundness
- ⚔️ **Hunting counterexample / falsifikasi** — formal, doktrinal, empiris
- 🔢 **Sanity check numerik** — gugurkan cepat; tidak pernah membuktikan

```bash
git clone https://github.com/DranxX/scholarmesh && cd scholarmesh
cp -r skills/research ~/.zcode/skills/     # atau ~/.claude/skills/ dll.
```

Detail: [skills/README.md](skills/README.md).

## 🏗 Arsitektur

```
pyproject.toml                ← paket uv ([project.scripts] scholarmesh)
└── src/scholarmesh/
    ├── server.py             ← pintu masuk MCP stdio (SDK `mcp` resmi, lowlevel Server)
    ├── registry.py           ← daftar SOURCES flat, auth-gating, post-filter tahun universal
    ├── federation.py         ← search_papers: queries×sources paralel (pool 8), dedup, provenance
    ├── core.py               ← httpx dengan timeout, skema item standar, envelope, year filter
    └── sources/              ← dikelompokkan per FUNGSI; negara = metadata per sumber
        ├── indexes.py    (8)  OpenAlex Crossref DOAJ S2 Lens Dimensions Scopus WoS
        ├── preprints.py  (4)  arXiv OpenReview(2) AlphaXiv HF Papers
        ├── archives.py   (6)  Unpaywall Zenodo DataCite OSF OpenAIRE CORE
        ├── domain.py     (8)  INSPIRE ERIC zbMATH ProofWiki(2) PwC EuropePMC(2) PubMed ADS
        ├── regional.py  (13)  GARUDA SINTA OneSearch RAMA Moraref Neliti BRIN GScholar NSSD Baidu AMiner ScienceDB CSTR
        └── people.py     (1)  ORCID
```

## 🧪 Testing

```bash
uv run python tests/light_smoke.py       # smoke tanpa key: gate + stdio + 3 call mini
uv run python tests/light_smoke.py --offline   # zero network
uv run python tests/e2e_all_tools.py     # suite live penuh (44 tools + federasi + stdio)
```

Suite penuh menjalankan **~48 pengecekan** — semua tool connector satu per satu
(validasi bentuk envelope + ekspektasi status per kategori), tiga mode federasi, cek
kebocoran filter tahun, dan handshake MCP stdio. Tool scraper yang `blocked` dihitung
PASS: **kontraknya adalah envelope yang benar, bukan mood jaringan**. Run terakhir:
**47/47 PASS**.

## ❓ FAQ

<details>
<summary>Kenapa ada sumber yang balik <code>blocked</code>?</summary>

Beberapa platform (Google Scholar, ProofWiki, beberapa portal regional) ada di balik
bot protection. ScholarMesh tidak berpura-pura sebaliknya — lu dapat envelope
terstruktur yang menjelaskan apa yang terjadi plus URL persis buat dicoba manual.
Itu jawaban yang bekerja, bukan error.
</details>

<details>
<summary>Apakah saya butuh API key?</summary>

Tidak. 18 sumber jalan tanpa key. Key hanya menaikkan rate limit (Semantic Scholar,
PubMed) atau membuka index premium terkurasi (Scopus, WoS, Lens…).
</details>

<details>
<summary>Apa yang terjadi dengan <code>paper-research-mcp</code>?</summary>

Itu nama pertama project ini. Paketnya di-rename jadi **scholarmesh**; nama PyPI lama
dipensiunkan dan tidak lagi diupdate. Install via `uv tool install scholarmesh`.
</details>

## 🤝 Kontribusi

Issues dan PR diterima — lihat [CONTRIBUTING.md](CONTRIBUTING.md) untuk checklist
connector probe-first, test suite, dan proses rilis.

## 📄 License

MIT. Rencana connector disaring dari dokumen referensi terkurasi (`Reference.md`)
plus tambahan yang diverifikasi live (Europe PMC, PubMed, OpenAIRE, Zenodo, DataCite,
OSF, zbMATH, HF Papers, CORE).

<div align="center">

**Dibangun oleh [DranxX](https://github.com/DranxX)** — kalau ScholarMesh menyelamatkan malam riset lu, ⭐ sangat dihargai.

</div>
