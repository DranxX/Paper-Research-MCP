# Workflow — Theorem Hunt

**Tujuan:** sebelum membuktikan ulang apa pun, pastikan hasilnya belum ada — dan bila
sudah ada, pakai referensi + bukti terbaik yang tersedia.

## Langkah

### 1. Formalisasi klaim
Tulis klaim user sebagai pernyataan matematis satu baris: objek, hipotesis (semua
syarat), kesimpulan, kuantor eksplisit (`∀x ∈ A: P(x)`). Identifikasi area
(analisis/aljabar/kombinatorika/…) — ini menentukan istilah pencarian.

### 2. Cek ProofWiki (kanon + nama umum)
- `proofwiki_search` dengan **nama umum** + **sinonim**: "Pythagorean Theorem" juga
  dicari sebagai "right triangle hypotenuse", "Bayes' theorem" sebagai "Bayes rule".
- Bila ketemu halaman teorema → `proofwiki_get` → catat: **hipotesis persis**,
  status (bukti lengkap / bergantung aksioma tertentu), dan wikilink definisi
  prasyarat di wikitext (bentuk `[[Definition:X]]` / `[[Y Theorem]]`) — itu pohon
  dependensi bukti.
- Halaman berkategori `Definition:`/`Theorems`/`Proofs` — lihat
  [references/proofwiki-guide.md](../references/proofwiki-guide.md).

### 3. Cek paper (hasil modern/kevarian)
`search_papers` dengan `queries: [klaim informal, "proof of <nama>", "<nama> theorem generalization"]`
dan filter tahun bila relevan (mis. frontier 5 tahun terakhir: `year_from`).
Untuk preprint: `arxiv_search` dengan kategori `cat:math.*` yang sesuai
(`math.AG` geometri aljabar, `math.NT` teori bilangan, `math.PR` probabilitas, …).

### 4. Cek sumber khusus bila klaim bertipe khusus
- Barisan/bilangan bulat → OEIS (manual: https://oeis.org) — cocokkan deret awal.
- Fisika-matematika → `inspire_search`.
- Eksposisi/pengajaran → `eric_search`.

### 5. Bandingkan hipotesis persis
Klaim yang mirip bukan klaim yang sama. Contoh perbedaan yang mengubah segalanya:
`finite` vs `infinite` dimensi, `real` vs `complex`, `continuous` vs `uniformly
continuous`, `convergent` vs `absolutely convergent`, syarat `compact` yang hilang.
Buat tabel perbandingan hipotesis klaim user vs hasil yang ditemukan.

### 6. Output: tabel status

| Klaim | Status | Referensi terbaik | Bukti tersedia di |
|---|---|---|---|
| … | `terbukti` / `terbukti dengan syarat tambahan` / `konjektur terbuka` / `tidak ditemukan` | nama + tahun + DOI/URL | ProofWiki page / arXiv id / paywall? |

**Keputusan lanjut:**
- Ada bukti publik → serahkan ke [proof-verification.md](proof-verification.md) untuk
  validasi, jangan buktikan ulang dari nol tanpa alasan.
- Hanya ada bukti dengan syarat lebih kuat → tandai gap: "hasilnya yang lemah ada;
  yang user minta belum ditemukan".
- Tidak ditemukan di semua sumber → laporkan "tidak ditemukan di: <daftar sumber>"
  (aturan 0.2 di SKILL.md) dan lanjut ke pembuktian dengan
  [references/proof-techniques.md](../references/proof-techniques.md).

## Fallback tanpa MCP
ProofWiki → buka `https://proofwiki.org/wiki/Special:Search?search=<q>` di browser;
paper → Google Scholar / zbMATH Open (https://zbmath.org) / arXiv listing manual.
