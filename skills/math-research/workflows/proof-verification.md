# Workflow — Proof Verification

**Tujuan:** validasi bukti langkah demi langkah — milik user, dari paper, atau dari
ProofWiki — sampai verdict berlabel, bukan kesan "kelihatannya benar".

**Muat dulu:** [references/rigor-checklist.md](../references/rigor-checklist.md) (katalog
kegagalan klasik — wajib untuk langkah 4).

## Input
`klaim + bukti` (teks). Bila bukti hanya di paper/PDF, ambil dulu:
`unpaywall_resolve`/`crossref_doi` untuk DOI, atau bukti dari ProofWiki via
`proofwiki_get` (wikitext — wikilink prasyaratnya berguna di langkah 2).

## Langkah

### 1. Formalisasi ulang
- Tulis ulang klaim dengan kuantor eksplisit: `∀/∃`, domain kuantifikasi, urutan
  kuantor. **Urutan `∀∃` vs `∃∀` berbeda makna** — cek apakah klaim yang dimaksud
  user memang itu (kesalahan paling umum di level ini).
- Untuk setiap istilah: definisi persisnya dari mana? ProofWiki (`Definition:` page
  via `proofwiki_search`/`proofwiki_get`), buku teks standar, atau definisi user.
  **Definisi ambigu = berhenti**, tandai, pakai definisi eksplisit yang disepakati.

### 2. Susun pohon dependensi
Daftar semua hasil yang dipakai bukti (aksioma, definisi, teorema sebelumnya).
Untuk bukti ProofWiki: ekstrak wikilink dari wikitext. Untuk tiap hasil yang dipakai:
- apakah pernyataannya persis seperti yang dibutuhkan di sini (bukan varian)?
- apakah hipotesisnya terpenuhi di konteks pemakaian? (INI sumber gap paling sering:
  teorema dipakai di luar hipotesisnya.)

### 3. Trace per langkah
Tabel: `langkah → pernyataan → dasar (definisi/aksioma/teorema/langkah sebelumnya) → status`.
- Tiap inferensi wajib punya dasar eksplisit. Lompatan = tandai ⚠️, bukan ditutupi
  dengan "jelas bahwa" / "mudah diperiksa" — itu persis frasa yang harus dibuka.
- Frasa berbahaya yang selalu dirombak: "it is obvious", "clearly", "one easily shows",
  "by a standard argument", "similarly".

### 4. Audit asumsi tersembunyi
Jalankan katalog [references/rigor-checklist.md](../references/rigor-checklist.md)
untuk: pembagian nol/non-invertibel, tukar urutan kuantor, kasus vakue/himpunan
kosong, endpoint interval, pertukaran limit/integral tanpa uniformitas, induksi yang
basisnya gagal, siklus logika (pakai teorema itu sendiri), ` sufficiently large`
yang tidak pernah dibuktikan, objek yang keberadaannya diandaikan tanpa konstruksi.

### 5. Uji batas (degenerasi)
Substitusikan kasus degenerat ke tiap langkah: `0, 1, -1`, himpunan kosong, dimensi 1,
struktur trivial, `→ ∞`. Langkah yang meledak di kasus degenerat biasanya menyembunyikan
asumsi tersembunyi. Untuk klaim konkret, sambungkan
[numeric-sanity.md](numeric-sanity.md) di sini.

### 6. Cross-check bukti referensi
Bila theorem-hunt menemukan bukti alternatif (ProofWiki/buku/paper): bandingkan
**struktur** bukti. Divergensi struktur bukan kesalahan otomatis — tapi tiap
divergensi adalah titik pemeriksaan ekstra. Bukti yang menyimpang DI TEMPAT yang
sama dengan bukti referensi punya gap → prioritas tinggi.

### 7. Verdict

| Label | Syarat |
|---|---|
| ✅ valid | semua langkah berdasar eksplisit + audit bersih + batas aman |
| ✅ valid dengan perbaikan | ada langkah tanpa dasar, tapi perbaikannya rutin (daftar perbaikan) |
| ⚠️ gap | lompatan logika/asumsi tersembunyi yang tidak rutin — daftar per langkah + kandidat strategi |
| ❌ terbantahkan | counterexample ditemukan (formalisasi via [counterexample-hunt.md](counterexample-hunt.md)) |

Output akhir pakai format VERDICT di SKILL.md §4. Kutip teks langkah ASLI saat
menandai gap — jangan parafrase sampai risikonya hilang.
