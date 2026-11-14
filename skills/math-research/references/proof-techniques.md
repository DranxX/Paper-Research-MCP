# Reference — Proof Techniques

Taksonomi strategi pembuktian + kapan dipakai + jebakan masing-masing. Muat saat
membuktikan sesuatu yang belum ada buktinya (setelah theorem-hunt kosong), atau saat
memilih kandidat perbaikan untuk gap di proof-verification.

## Pemilih cepat

| Bentuk klaim | Strategi pertama | Strategi cadangan |
|---|---|---|
| `P(n)` untuk semua n ∈ ℕ | induksi (weak) | strong induction / minimal counterexample |
| "tidak ada x dengan P(x)" | kontradiksi | extrema/well-ordering |
| `P ⇒ Q` langsung | direct | kontraposisi (`¬Q ⇒ ¬P`) — sering lebih mulus |
| "ada x dengan P(x)" | konstruksi eksplisit | eksistensi non-konstruktif (hanya kalau perlu) |
| "untuk semua struktur, X invarian" | invarian/monovarian | klasifikasi kasus |
| "himpunan uncountable" | diagonalisasi | bijeksi Cantor–Schröder–Bernstein |
| "ada dua dengan properti sama" | pigeonhole | probabilistic method |
| "batas atas terkecil" | supremum/ekstremal | konstruksi berurutan |
| identitas antar fungsi/barisan | generating functions | transformasi (Fourier/Laplace) |

## Strategi dengan detail

### Direct & kontraposisi
Mulai dari definisi, dorong ke depan. **Jebakan:** diam-diam memakai kebalikan
hipotesis (`P ⇒ Q` berbeda dengan `Q ⇒ P` — cek arah setiap implikasi).

### Kontradiksi
Asumsikan `¬Q`, turunkan absurditas. **Jebakan:** absurditas yang diturunkan ternyata
bukan kontradiksi logis melainkan hanya "aneh"; dan asumsi `¬Q` yang salah ketik
(menandasikan bagian Q yang justru mau ditolak).

### Induksi (weak / strong / structural)
- Basis + langkah, keduanya WAJIB diperiksa eksplisit. **Jebakan:** langkah benar
  untuk `n ≥ k` tapi basis `n₀` tidak sesuai `k` (off-by-one induksi).
- Strong induction dipakai saat rekursi memanggil nilai lebih kecil yang tak
  berurutan. Structural untuk definisi rekursif atas struktur (pohon, formula).
- Induksi berbasis "minimal counterexample" = strong induction terbalik — berguna
  untuk klaim "tidak ada".

### Konstruksi
Kasus eksistensi: berikan objeknya + verifikasi objek memenuhi SEMUA syarat (dua arah,
seperti di counterexample-hunt langkah 6). **Jebakan:** konstruksi yang menyamarkan
pemakaian axiom of choice — boleh dipakai, tapi sebutkan.

### Diagonalisasi & pigeonhole
Diagonalisasi untuk "lebih banyak" (uncountability, undecidability). Pigeonhole untuk
"pasti tabrakan". **Jebakan:** menghitung kotak/burung salah satu (m/salah arah
pembulatan).

### Invarian / monovarian
Cari kuantitas yang tak berubah (invarian) atau hanya berubah satu arah (monovarian)
di bawah operasi — untuk klaim "tidak mungkin sampai", "proses selalu berhenti".
Klasik: parity, mod m, jumlah total, luas. **Jebakan:** invarian yang dipilih tidak
membedakan keadaan awal vs akhir (invarian benar tapi tak berguna).

### Ekstremal / supremum
Ambil objek ekstrem, tunjukkan ekstremnya memenuhi properti. **Jebakan:** asumsi
ekstremnya ADA (keberadaan butuh kompaktness/kelengkapan — di ruang tak-kompak,
supremum bisa tidak tercapai).

### Probabilistic method
Untuk eksistensi: tunjukkan peluang properti > 0. **Jebakan:** lupa bahwa ini
non-konstruktif (objeknya dijamin ada tapi tidak diberikan).

### Generating functions & transformasi
Untuk identitas kombinatorik/recurrence: encode jadi koefisien. **Jebakan:** pertukaran
jumlah–limit tanpa cek konvergensi radius.

## Kaitan ke workflow lain
- Membuktikan ulang hasil yang ada → mulai dari sini SETELAH theorem-hunt kosong.
- Strategi gagal terus → biasanya klaim butuh hipotesis tambahan; cek dengan
  counterexample-hunt (hilangkan satu syarat, lihat yang mana yang menahan bukti).
- Setelah punya draft bukti → proof-verification, selalu.
