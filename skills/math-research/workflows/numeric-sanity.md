# Workflow — Numeric Sanity

**Tujuan:** uji cepat klaim konkret dengan angka — untuk **gugurkan cepat, temukan
pola, dan uji batas**. TIDAK PERNAH membuktikan (aturan 0.3 SKILL.md).

## Prinsip
- Numerik yang setuju ≠ bukti. Numerik yang BEDA = klaim palsu ATAU salah konstanta
  / salah batas / salah definisi di argumen — dua-duanya temuan berharga.
- Selalu laporan: "lolos di N kasus termasuk kasus degenerat" + disclaimer bahwa ini
  bukan bukti.

## Langkah

### 1. Konkretkan klaim
Ubah klaim menjadi fungsi terhitung: input (objek + parameternya), output ekspektasi.
Bila klaim tak bisa dikonkretkan → bukan kandidat numerik, kembali ke
[proof-verification.md](proof-verification.md).

### 2. Kasus uji bertingkat
1. **Kanonik**: contoh paling standar (mistar teori — harus benar, kalau tidak:
   implementasi/transkripsi yang salah).
2. **Acak**: 100–1000 instans random dari ruang parameter.
3. **Degenerat**: `0, 1, -1`, himpunan kosong, dimensi 1, singular/hampir-singular.
4. **Adversarial**: nilai yang biasanya memicu kegagalan — sangat besar/kecil, tanda
   bergantian, bilangan irasional (π, √2) di tempat yang mengandaikan rasional.

### 3. Skrip kecil, satu file
Python murni atau SymPy bila tersedia (bila MCP/jaringan mati, ini tetap jalan —
eksekusi lokal). Bentuknya selalu sama:

```python
def claim(x): ...        # transkripsi persis klaim
def expectation(x): ...  # apa yang klaim prediksi
cases = [kanonik] + [random_cases(200)] + [degenerate] + [adversarial]
for c in cases: compare(claim(c), expectation(c), tol=...)
```

- Bandingkan dengan toleransi eksplisit (`tol`) — dan laporkan toleransinya.
- Ketidakcocokan kecil yang konsisten (mis. selalu ≈ 10⁻¹⁰ relatif) = sinyal salah
  konstanta/normalisasi di transkripsi atau di klaim — telusuri, jangan abaikan.

### 4. Cek invarian (bila klaim struktural)
Banyak klaim lebih mudah diuji sebagai invarian: "hasilnya selalu positif", "monoton
di parameter", "simetris terhadap pertukaran", "massa total terjaga". Uji invarian
di semua kasus uji.

### 5. Output

| Kasus | Ekspektasi | Hasil | Status |
|---|---|---|---|

Verdict numerik yang boleh dilaporkan:
- ❌ "klaim GAGAL di kasus: … (konkret, reproduksiibel)" → langsung ke
  [counterexample-hunt.md](counterexample-hunt.md) untuk formalisasi.
- ✅ "lolos di N kasus (kanonik + acak + degenerat + adversarial, tol=…)" — dengan
  disclaimer numerik, lanjut pembuktian via [proof-techniques.md](../references/proof-techniques.md).
