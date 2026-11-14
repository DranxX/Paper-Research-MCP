---
name: math-research
description: >
  Riset matematis berbasis AI: theorem-hunting (cek dulu apakah hasil sudah ada sebelum
  membuktikan ulang), verifikasi bukti langkah demi langkah, hunting counterexample untuk
  menyanggah klaim, survei literatur matematika (annotated bibliography + reading order),
  dan eksperimen numerik sebagai sanity check. Pair dengan MCP paper-research-mcp
  (search_papers, arxiv_search, proofwiki_search, proofwiki_get, crossref_doi,
  unpaywall_resolve) tapi tetap jalan tanpa MCP (fallback pencarian manual).
  Trigger saat user mengerjakan teorema, lemma, bukti/proof, konjektur, validasi matematis,
  "buktikan bahwa", "cek bukti ini", "apakah klaim ini benar", counterexample, atau survei
  topik matematika. JANGAN trigger untuk kalkulasi sekadar atau kode numerik biasa tanpa
  konteks riset.
user-invocable: true
---

# Math Research

Satu skill untuk pekerjaan matematika berbasis riset: mencari hasil yang sudah ada,
memvalidasi bukti, menyanggah klaim, dan menyurvei literatur — dengan sumber bukti
publik (ProofWiki, arXiv, OpenAlex, Crossref, Unpaywall) yang diakses via MCP
**paper-research-mcp** bila terhubung, atau fallback manual bila tidak.

Struktur: `workflows/` (prosedur eksekusi) + `references/` (knowledge base).

## 0. Aturan yang selalu berlaku

1. **Definisi dulu, selalu.** Sebelum menyentuh klaim apa pun, setiap istilah
   dinormalisasi ke definisi persisnya (ProofWiki `Definition:` pages, buku teks
   standar, atau definisi user). Klaim yang definisinya ambigu tidak boleh
   diverifikasi — tandai dan minta/milih definisi eksplisit dulu.
2. **"Belum ketemu" ≠ "tidak ada".** Hasil pencarian kosong dilaporkan apa adanya
   ("tidak ditemukan di sumber X") — jangan pernah menyimpulkan "belum ada yang
   membuktikan" hanya karena satu sumber gagal/bot-wall.
3. **Numerik tidak pernah membuktikan.** Eksperimen numerik hanya untuk (a) gugurkan
   cepat klaim palsu, (b) menemukan pola, (c) uji batas. Klaim "lolos di N kasus"
   selalu disertai disclaimer itu.
4. **Atribusi ProofWiki wajib.** Konten ProofWiki berlisensi CC BY-SA 3.0 / GFDL —
   saat mengutip/mengadaptasi bukti atau definisi, sebut judul halaman + URL + lisensi.
   Lihat [references/proofwiki-guide.md](references/proofwiki-guide.md).
5. **Status bukti jujur.** Setiap hasil dilabeli: `terbukti (referensi)` /
   `terbukti dengan syarat tambahan` / `konjektur terbuka` / `tidak ditemukan` /
   `terbantahkan (counterexample)`. Tanpa label, hasil tidak boleh disajikan.
6. **Gap dilaporkan per langkah.** Verifikasi bukti yang menemukan lompatan logika
   melaporkan langkah mana, apa yang kurang, dan kandidat perbaikannya — bukan
   kesimpulan samar "kelihatannya benar".

## 1. Rute tugas → workflow

| Situasi | Workflow |
|---|---|
| "Buktikan bahwa X" / butuh cek apakah X sudah ada | [workflows/theorem-hunt.md](workflows/theorem-hunt.md) |
| Ada bukti yang harus divalidasi (milik user, dari paper, atau dari ProofWiki) | [workflows/proof-verification.md](workflows/proof-verification.md) |
| Klaim dicurigai salah / diminta menyanggah | [workflows/counterexample-hunt.md](workflows/counterexample-hunt.md) |
| Survei topik / annotated bibliography / temuan research gap | [workflows/literature-scan.md](workflows/literature-scan.md) |
| Uji cepat klaim konkret dengan angka (sebelum/di tengah verifikasi) | [workflows/numeric-sanity.md](workflows/numeric-sanity.md) |

Workflow boleh di-rantai: urutan wajar adalah **theorem-hunt → proof-verification →
(counterexample-hunt bila curiga)** dengan numeric-sanity dipanggil kapan pun klaimnya
konkret. Literature-scan berdiri sendiri untuk tugas survei.

## 2. Referensi (muat saat dibutuhkan)

| Kebutuhan | Reference |
|---|---|
| Memakai ProofWiki: API, judul halaman, wikitext, lisensi | [references/proofwiki-guide.md](references/proofwiki-guide.md) |
| Memilih strategi membuktikan (induksi, kontradiksi, invarian, …) | [references/proof-techniques.md](references/proof-techniques.md) |
| Audit bukti — wajib dimuat saat proof-verification | [references/rigor-checklist.md](references/rigor-checklist.md) |
| Memilih tool MCP per kebutuhan + fallback tanpa MCP | [references/tool-map.md](references/tool-map.md) |

## 3. Pairing dengan paper-research-mcp

Skill ini didesain berpasangan dengan MCP **paper-research-mcp** (repo yang sama).
Tool yang paling sering dipakai:

- `proofwiki_search` / `proofwiki_get` — definisi, teorema, bukti lengkap
- `search_papers` — pencarian paper federasi (multi-keyword parallel + filter tahun)
- `arxiv_search` — preprint (kategori `math.*`), `openalex_search` / `crossref_search` — metadata
- `unpaywall_resolve` / `crossref_doi` — akses full-text legal & resolusi DOI

Bila MCP tidak terhubung: semua workflow tetap jalan dengan fallback manual
(lihat [references/tool-map.md](references/tool-map.md) — tabel per kebutuhan).
Jangan pernah menggagalkan workflow hanya karena satu connector `blocked`
(bot-wall) — lanjutkan ke sumber/fallback berikutnya.

> ⚠️ ProofWiki dari beberapa jaringan kena Cloudflare (`blocked` envelope) — itu bukan
> kegagalan workflow; buka URL manual di browser atau coba lagi nanti. Detail di
> [references/proofwiki-guide.md](references/proofwiki-guide.md).

## 4. Format hasil yang disarankan

Untuk tugas validasi, akhiri dengan verdict berlabel:

```
VERDICT: ✅ valid | ✅ valid dengan perbaikan | ⚠️ gap | ❌ terbantahkan
KLAIM  : <pernyataan formal satu baris>
LANGKAH: tabel langkah → dasar (definisi/teorema/aksioma) → status
GAP    : <daftar lompatan logika + kandidat perbaikan, bila ada>
SUMBER : <ProofWiki/paper/teks + URL + lisensi bila mengutip>
```
