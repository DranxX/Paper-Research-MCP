# Reference — Rigor Checklist

Katalog kegagalan klasik dalam bukti/klaim matematis. **Wajib dimuat saat
proof-verification (langkah 4)** — jalankan satu per satu terhadap bukti.

Cara pakai: untuk tiap butir, cari kemunculannya di bukti. Temuan = tandai langkah +
kutip teks ASLI. Bukan semua butir relevan tiap bukti — skip yang tak berlaku, catat
skip-nya.

## 1. Kuantor
- [ ] **Tukar urutan kuantor**: `∀x ∃y` ≠ `∃y ∀x`. Bukti yang menganggap satu `y`
  berlaku untuk semua `x` padahal `y` bergantung `x` (atau sebaliknya) — kesalahan
  nomor satu di level ini.
- [ ] **Negasi kuantor ganda**: `¬(∀x P(x)) = ∃x ¬P(x)` dan `¬(∃x P(x)) = ∀x ¬P(x)`
  — negasi yang salah arah merusak kontradiksi.
- [ ] **Domain kuantifikasi menyempit diam-diam**: "untuk semua x" yang lama-lama
  "untuk semua x ≠ 0".

## 2. Pembagian & invertibilitas
- [ ] **Pembagian nol / faktor nol**: membagi kedua ruas dengan ekspresi yang bisa 0.
- [ ] **Objek non-invertibel**: matriks singular, fungsi tak bijektif dianggap punya
  invers, modulo tanpa gcd 1.
- [ ] **Keberadaan diandaikan**: "ambil z sedemikian sehingga …" tanpa konstruksi/
  eksistensi (supremum tak tercapai di ruang tak-kompak; "pilih basis" butuh AC di
  ruang umum).

## 3. Kasus degenerat & endpoint
- [ ] **Himpunan kosong / struktur trivial**: klaim "untuk semua" yang buktinya
  mulai dari contoh tak-trivial.
- [ ] **`n = 0, 1`**: banyak teorema benar `n ≥ 2` saja; bukti yang tak menahan
  kasus kecil.
- [ ] **Endpoint interval**: inklusif vs eksklusif (`[0,1)` vs `(0,1]`), `≤` vs `<`
  — cek tiap ketidaksamaan yang dipakai.
- [ ] **Kasus vakue**: implikasi dengan premis palsu otomatis benar — klaim "benar"
  yang hanya benar-vakue di kasus yang menarik.

## 4. Limit, konvergensi, pertukaran
- [ ] **Pertukaran limit/integral/derajat** tanpa uniformitas (dominated convergence,
  uniform convergence) — `lim f_n ≠ f_lim` tanpa syarat.
- [ ] **Suku → 0 ⇒ deret konvergen**: klasik `∑ 1/n`.
- [ ] **Konvergen ≠ absolut konvergen**: pertukaran urutan penjumlahan butuh absolut.
- [ ] **"Cukup besar" tanpa eksistensi**: "untuk n cukup besar" — n₀ mana, dan
  mengapa eksis?

## 5. Struktur logika
- [ ] **Siklus logika**: langkah memakai teorema yang sedang dibuktikan (atau versi
  ekuivalennya yang belum dibuktikan).
- [ ] **Induksi off-by-one**: langkah `n → n+1` benar tapi basisnya mulai di `n₀`
  yang salah / tidak dicakup.
- [ ] **Pemisahan kasus tidak tuntas**: kasus yang didaftar tidak menutup semua
  kemungkinan (kasus `<`, `=`, `>` yang salah satu terlewat).
- [ ] **"Jelas"/"mudah dilihat"/"standar"**: frasa ini = langkah tanpa dasar — rombak
  sampai inferensinya eksplisit (proof-verification langkah 3).

## 6. Definisi & istilah
- [ ] **Dua definisi untuk satu istilah**: kekontinuan (ε-δ vs sequential),
  integrabilitas (Riemann vs Lebesgue), "versi" definisi antar buku — bukti memakai
  definisi A, klaim dipakai di konteks definisi B.
- [ ] **Kontinu vs uniform-continu**, **konvergen vs Cauchy**, **terbatas vs
  konvergen** — pasangan yang hanya ekuivalen di ruang khusus (compact/complete).
- [ ] **Klaim lebih kuat dari yang dibutuhkan**: membuktikan versi lemah tapi
  menyimpulkan versi kuat (atau sebaliknya, mengutip versi kuat tanpa syaratnya).

## 7. Probabilitas & ukuran
- [ ] **Independensi diandaikan** tanpa syarat.
- [ ] **Union bound terbalik** / probabilitas kondisional salah arah.
- [ ] **"Hampir pasti" dikacaukan dengan "pasti"**; himpunan ukuran nol ≠ himpunan
  kosong.

## 8. Finite vs infinite
- [ ] **Argumen finite dipakai di infinite**: penjumlahan terurut-ulang, "pilih yang
  terbesar" di himpunan tak terbatas, induksi atas himpunan tak terhingga.
- [ ] **Cardinality silap**: countable dianggap finite, uncountable dianggap countable.
- [ ] **Kompaktness hilang**: ekuivalensi yang hanya berlaku di ruang kompakt
  dipakai di ruang umum.

## 9. Numerik (kaitan numeric-sanity)
- [ ] **Presisi floating point menyamarkan kesalahan**: selisih konsisten kecil =
  sinyal, bukan noise.
- [ ] **Kasus uji semuanya kanonik**: tanpa degenerat/adversarial, "lolos" tidak
  bermakna.

## Output audit
Untuk tiap butir yang gagal: `langkah L → butir (mis. 4.2) → kutipan teks asli →
dampak (fatal/perbaikan rutin)`. Semua butir dicek tanpa temuan → tulis "audit 9
kategori: bersih" di verdict — audit yang tidak tercatat = audit yang diragukan.
