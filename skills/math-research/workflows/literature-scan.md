# Workflow — Literature Scan (matematika)

**Tujuan:** survei satu topik matematika → annotated bibliography + reading order +
research gap yang terlihat.

## Langkah

### 1. Petakan ruang topik
- Area + sub-area (mis. "optimal transport" ⊂ analisis fungsional/geometri).
- Dua set kata kunci: **istilah kanonik** (nama teorema/buku yang sudah dikenal) dan
  **varian informal** (istilah yang dipakai paper berbeda-beda). Matematika terkenal
  dengan sinonim tak sinkron ("cobordism" vs " bordism", "graph" vs "network").

### 2. Dua jendela waktu
Jalankan `search_papers` dengan `queries:` multi-keyword, dua putaran:
- **Akar**: `year_to` (mis. 5 tahun pertama setelah area lahir) → paper-paper fondasi,
  urut sitasi (`cited_by_count` di `extra` openalex/crossref).
- **Frontier**: `year_from` (5 tahun terakhir) → arah penelitian sekarang.
Untuk preprint frontier: `arxiv_search` dengan kategori `cat:math.*` spesifik.

### 3. Kanon definisi & teorema
`proofwiki_search` untuk definisi standar + teorema inti — berguna untuk menyamakan
terminologi antar paper (aturan 0.1 SKILL.md). Buktinya sering lengkap → pintu masuk
termurah ke materi baru.

### 4. Sumber tambahan bertipe khusus
- Monografi/survey: cari "survey"/"review" pada `queries` frontier.
- Fisika-matematika: `inspire_search`.
- Pendidikan/eksposisi: `eric_search`.
- zbMATH Open (https://zbmath.org, gratis) & MathSciNet (butuh langganan) — review
  matematis yang mengklasifikasi per MSC2020 (kode klasifikasi); pakai kode MSC
  sebagai keyword tambahan (mis. `49Q22`).

### 5. Cek akses full-text
`unpaywall_resolve` per DOI kandidat inti — tandai mana yang terbaca langsung vs
yang perlu institutional access. Paper tak terjangkau cukup masuk daftar + abstraknya.

### 6. Susun reading order
1. **Buku teks / definisi** (ProofWiki `Definition:` + buku standar yang muncul di sitasi)
2. **Survey** terbaru yang bagus
3. **Paper inti** (sitasi tertinggi jendela "akar")
4. **Frontier** (jendela 5 tahun, grup per arah/garis riset)

### 7. Output

| # | Judul | Tahun | Sumber | Peran (fondasi/survey/frontier) | Akses | Catatan 1-2 baris |
|---|---|---|---|---|---|---|

Plus: **terminology map** (istilah yang sama di paper berbeda) dan **gap terlihat**
("tidak ada yang menggabungkan X dan Y — keduanya aktif tapi tidak saling sitasi").

## Fallback tanpa MCP
Google Scholar → zbMATH Open → arXiv listing manual; jangan mengandalkan satu situs
untuk "tidak ada".
