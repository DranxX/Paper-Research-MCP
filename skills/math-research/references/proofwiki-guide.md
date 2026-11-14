# Reference — ProofWiki Guide

Apa itu ProofWiki, cara memakainya via MCP, konvensi halaman, dan lisensinya.

## Apa itu
[ProofWiki](https://proofwiki.org) — wiki komunitas yang berisi **definisi, teorema,
dan bukti lengkap** matematika klasik sampai intermediate. Kekuatan: setiap bukti
terstruktur, mengandung wikilink ke definisi & lema prasyarat, dan hasilnya bisa
dipakai sebagai referensi lintas-buku. Kelemahan (jujur): bukan peer-review formal —
teorema kanonik sangat teruji, topik niche bisa punya gap; untuk pekerjaan
publishable, cross-check ke sumber primer tetap wajib.

## Akses via paper-research-mcp
Dua tool connector `proofwiki` (MediaWiki API `api.php`, gratis tanpa key):

| Tool | Untuk | Catatan |
|---|---|---|
| `proofwiki_search {query, limit}` | cari judul halaman (teorema/definisi) | return snippet + wordcount + `last_edit` |
| `proofwiki_get {page}` | ambil wikitext lengkap satu halaman | wikilink prasyarat terlihat di wikitext |

**Cloudflare:** ProofWiki di depan Cloudflare. Dari jaringan ber-IP bersih biasanya
200; dari jaringan lain kena JS challenge → envelope `blocked` + URL fallback manual.
Itu bukan kegagalan workflow: buka URL di browser atau coba lagi nanti. Probes
14 Nov 2026 (jaringan sandbox): challenge → blocked.

## Konvensi halaman (penting untuk `proofwiki_get`)
- Judul harus **persis**. Corak umum:
  - Teorema: `Pythagorean Theorem`, `Cantor's Theorem`, `Hahn-Banach Theorem`
  - Definisi: `Definition:Metric Space`, `Definition:Eigenvector`
  - Kategori: `Category:Proofs`, `Category:Theorems`, `Category:Axioms` — untuk
    browsing struktur, bukan `proofwiki_get`.
- Karena itu alur yang benar: **search dulu → ambil judul persis → get**.
  (Kesalahan umum: langsung `get` dengan judul versi sendiri → `empty`.)

## Wikitext & pohon dependensi
Wikitext bukan HTML mati — ia berisi struktur yang bisa diekstrak:
- `[[Definition:Metric Space]]`, `[[Hahn-Banach Theorem]]` — wikilink ke **prasyarat**:
  kumpulkan untuk pohon dependensi bukti (dipakai workflow proof-verification langkah 2).
- Bagian `Proof` biasanya dipisah per kasus/varian (`Proof 1`, `Proof 2`, `Proof for
  finite case`) — cocokkan varian dengan klaim yang divalidasi.
- Tautan kategori di bagian bawah halaman → teorema sejenis untuk cross-check.

## Lisensi & atribusi (WAJIB — aturan 0.4 SKILL.md)
Konten ProofWiki berlisensi **CC BY-SA 3.0 / GFDL dual-license**. Saat mengutip atau
mengadaptasi (bukan hanya membaca): sebut
`"Sumber: ProofWiki — <judul halaman> (<URL>), CC BY-SA 3.0"` — envelope `ok` sudah
membawa string atribusi ini di `meta` dan `extra.attribution`.
- Mengadaptasi bukti untuk publikasi → hasil turunan ikut terikat BY-SA; verifikasi
  juga ke sumber primer (buku teks standar).
- Membaca untuk validasi sendiri → tidak ada kewajiban publikasi, tetap baik mencantumkan.

## Batasan yang harus disebut ke user
1. Bukan peer-review formal — cross-check kanonik ke buku standar untuk pekerjaan serius.
2. Cakupan condong ke matematika "kurikulum klasik" — riset frontier ada di arXiv.
3. Nama teorema bervariasi antar tradisi (UK/US, matematika/fisika) — search dengan
   sinonim (workflow theorem-hunt langkah 2).
