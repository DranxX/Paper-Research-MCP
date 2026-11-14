# Workflow — Counterexample Hunt

**Tujuan:** menyanggah klaim dengan counterexample eksplisit dan persis — bukan
intuisi "sepertinya salah".

## Langkah

### 1. Pahami serangan
- Hipotesis = daftar syarat. **Tiap syarat adalah potensi titik serangan**: hilangkan
  satu syarat → biasanya counterexample klasik muncul (klaim tanpa syarat komutatif,
  tanpa kelengkapan, tanpa kompaktness, tanpa kekontinuan, …).
- Identifikasi ruang parameter: dimensi, ukuran, kelas fungsi, tipe struktur.

### 2. Kasus kecil & degenerat dulu
Urutan murah → mahal: `n = 0, 1, 2` · dimensi 1 · himpunan kosong / singleton ·
struktur trivial · konstanta `0, 1, -1, π` · tanda negatif. Banyak klaim "terbukti"
di paper benar hanya untuk `n ≥ 2` dan gagal diam-diam di `n = 1`.

### 3. Parameter ekstrem
`→ 0`, `→ ∞`, fungsi yang tak terdiferensialkan di satu titik, barisan yang konvergen
sangat lambat, objek hampir-degenerate (determinan ≈ 0, jarak antar titik ≈ 0).

### 4. Keluarga terkenal (bila klaim berbau analisis/struktur)
Cocokkan klaim dengan keluarga yang didesain untuk mematahkan intuisi serupa:

| Keluarga | Mematahkan klaim tipe |
|---|---|
| Weierstrass function | "kontinu ⇒ terdiferensialkan hampir di mana pun (secara klasik)" |
| Cantor set | "himpunan tak terhingga ⇒ mengandung interval" |
| Dirichlet function | "Riemann-integrabel untuk fungsi apa pun" |
| `x ↦ sin(1/x)` dekat 0 | "limit selalu ada bila fungsi terbatas" |
| `∑ 1/n` | "suku → 0 ⇒ deret konvergen" |
| bilangan prima besar / pasangan kembar kecil | klaim teori bilangan "untuk semua" |
| graf siklus / bipartit / lengkap kecil | klaim kombinatorik "untuk semua graf" |

### 5. Numerik dulu, formal kemudian
Pakai [numeric-sanity.md](numeric-sanity.md) untuk mencari kandidat dengan skrip kecil
(random search + adversarial cases). Kandidat numerik **bukan** counterexample final.

### 6. Formalisasi counterexample
- Konstruksi EKSPLISIT (bukan "ada" tanpa konstruksi).
- Verifikasi balik: tunjukkan objek memenuhi SEMUA hipotesis klaim, lalu tunjukkan
  kesimpulan gagal untuk objek itu. Kedua arah wajib — counterexample yang tidak
  memenuhi hipotesis tidak menyanggah apa-apa.
- Cek ulang definisi: counterexample harus dipakai definisi yang SAMA dengan klaim
  (kesalahan klasik: menyanggah versi kontinu dengan versi uniform).

### 7. Bila tidak ketemu
"Tidak menemukan counterexample di N kandidat" ≠ klaim benar — laporkan apa adanya,
lalu lanjut [proof-verification.md](proof-verification.md) (klaim mungkin memang benar,
dan usaha menyanggah sering memperlihatkan di hipotesis mana kekuatannya).

### 8. Output
```
COUNTEREXAMPLE: <konstruksi eksplisit>
HIPOTESIS TERPENUHI: <bukti tiap syarat>
KESIMPULAN GAGAL DI: <evaluasi eksplisit>
STATUS KLAIM: ❌ terbantahkan (persis seperti diklaim) / ⚠️ terbantahkan hanya tanpa syarat X (syarat itu wajib ditambahkan ke klaim)
```
