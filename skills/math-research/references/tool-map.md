# Reference — Tool Map (MCP → kebutuhan riset matematika)

Pemetaan kebutuhan → tool paper-research-mcp → fallback tanpa MCP. Semua workflow
skill ini memakai tabel ini; connector `blocked` bukan kegagalan workflow — lanjut
ke fallback (aturan 0.2 SKILL.md + §3 SKILL.md).

## Kebutuhan inti

| Kebutuhan | Tool MCP | Fallback tanpa MCP |
|---|---|---|
| Cari teorema/definisi kanonik | `proofwiki_search` | https://proofwiki.org/wiki/Special:Search?search=<q> |
| Baca bukti lengkap + prasyarat | `proofwiki_get` | buka URL halaman di browser |
| Paper multi-keyword paralel + filter tahun | `search_papers {queries:[], year_from, year_to}` | Google Scholar / zbMATH Open (https://zbmath.org) |
| Preprint + kategori math.* | `arxiv_search` (mis. `cat:math.NT AND all:<kata>`) | https://arxiv.org/list/math.* |
| Metadata paper besar (sitasi, OA status) | `openalex_search` | https://openalex.org |
| Metadata + sitasi (DOI-first) | `crossref_search` / `crossref_doi` | https://search.crossref.org |
| Resolusi DOI → metadata persis | `crossref_doi {doi}` | https://doi.org/<doi> |
| Full-text legal (OA) | `unpaywall_resolve {doi}` | cek versi OA di https://unpaywall.org |
| Semua sumber + status | `list_sources` | — |

## Kebutuhan bertipe khusus

| Kebutuhan | Tool MCP | Catatan |
|---|---|---|
| Barisan/bilangan bulat | — (manual: https://oeis.org) | cocokkan deret awal, hati-hati overfit |
| Fisika-matematika (hep) | `inspire_search` | INSPIRE-HEP |
| Pendidikan/eksposisi | `eric_search` | survey pengajaran |
| Review matematis + klasifikasi MSC | — (manual: https://zbmath.org, gratis) | MathSciNet berbayar; pakai kode MSC sebagai keyword di tool lain |
| Implementasi kode paper | `pwc_search` | Papers with Code |
| Review konferensi (AI/ML-math) | `openreview_search` / `openreview_notes` | rebuttal + decision terlihat |

## Pola pemakaian yang efisien

1. **Multi-keyword**: jangan satu query panjang — pecah jadi `queries: [istilah kanonik,
   sinonim, "proof of <nama>"]`; `search_papers` menjalankan SEMUA paralel dan
   menandai `matchedQueries` per item.
2. **Dua jendela tahun**: akar (`year_to`) + frontier (`year_from`) — lihat
   literature-scan langkah 2.
3. **Bot-wall**: `include_bot_wall: false` mempercepat (skip scraper ProofWiki/Google
   Scholar/Indonesia) bila hanya butuh sumber API resmi.
4. **proofwiki_get `empty`** = judul tidak persis → balik ke `proofwiki_search`
   (lihat proofwiki-guide §konvensi halaman).
5. **Konten ProofWiki** membawa lisensi CC BY-SA 3.0 di `meta` — ikutkan atribusi saat
   mengutip (aturan 0.4 SKILL.md).
