# 📖 Panduan Penggunaan Website SiButik

Website SiButik (Silang Budaya Batik) adalah aplikasi untuk membuat
**Cultural Fusion Batik** — menggabungkan dua tradisi batik daerah
Nusantara menjadi satu kain batik fusion, dengan bantuan
**Stable Diffusion XL + LoRA Joint Training**.

---

## 🚀 Akses Website

Buka URL Space Hugging Face yang sudah di-deploy, atau jika dijalankan
secara lokal:

```
http://127.0.0.1:8000/
```

Halaman utama terbagi menjadi **3 bagian utama** dari atas ke bawah.

---

## 1️⃣ Section Generator (Konfigurasi Budaya)

| Elemen | Fungsi |
|---|---|
| **Dropdown Budaya 1** (wajib) | Pilih budaya pertama yang akan difusion-kan |
| **Dropdown Budaya 2** (opsional) | Pilih budaya kedua. Kosongkan jika ingin 1 budaya saja |
| **Kolom Prompt** (opsional) | Kata kunci tambahan untuk memfilter template, mis. *"floral"*, *"navy"*, *"mega mendung"* |

### Cara Pakai:

1. Pilih **Budaya 1** — mis. *"Madura — Pola Kompleks"*
2. Pilih **Budaya 2** — mis. *"Jawa Barat"*
3. (Opsional) Ketik kata kunci di kolom Prompt untuk memfilter hasil
4. Section Template di bawah akan otomatis ter-filter sesuai pilihan

**Dropdown yang tersedia:**
- Jawa Barat
- Jawa Tengah
- Jawa Timur
- Yogyakarta
- Madura — Klasik
- Madura — Pola Kompleks
- Madura — Pola Sederhana

---

## 2️⃣ Section Template (Carousel Hasil Fusion)

Setelah memilih budaya, scroll ke bawah untuk melihat **Template**.

### Yang ditampilkan per slide:

- **Gambar batik** fusion (kiri)
- **Tag budaya** mis. `Yogyakarta × Jawa Barat` (warna berbeda per daerah)
- **Judul fusion** lengkap
- **Narasi** — penjelasan filosofi & harmoni budaya
- **Prompt** — kode prompt SDXL untuk re-generate
- **Tombol "Pilih Template Ini"** untuk dibawa ke langkah berikutnya

### Navigasi Slide:

| Cara | Aksi |
|---|---|
| Tombol **‹ Sebelumnya** / **› Berikutnya** | Geser 1 slide |
| Klik **dot** (titik) di bawah carousel | Lompat ke slide tertentu |
| **Scroll mouse** ke atas/bawah | Geser horizontal (di area carousel) |
| Tombol **← / →** pada keyboard | Geser (setelah fokus ke carousel) |

Status "Menampilkan N template" di atas carousel menunjukkan berapa
template yang cocok dengan filter.

---

## 3️⃣ Section Terapkan ke Baju

Setelah memilih template, scroll ke bawah.

### Cara Pakai:

1. Klik **"Pilih Template Ini"** pada salah satu slide carousel
2. Section ini akan terisi dengan preview template yang dipilih
3. **Upload foto orang** (format JPG/PNG, latar bebas)
4. Klik tombol **"Terapkan ke Baju"**
5. Tunggu beberapa detik — sistem akan:
   - Segmentasi area pakaian otomatis (`rembg u2net_cloth_seg`)
   - Tiling motif batik dengan teknik **Feathered Seams + Half-Drop**
   - Tempel motif ke baju dengan blending natural
6. Hasil akan muncul di preview kiri

> ⚠️ Untuk hasil terbaik: gunakan foto dengan pencahayaan cukup &
> subjek berpakaian lengkap (baju terlihat jelas).

---

## 💡 Tips & Trik

### Mendapatkan Fusion yang Bagus:

- Kombinasikan **2 budaya** yang saling kontras untuk hasil yang kaya,
  mis. *Madura (motif floral tegas)* × *Jawa Barat (mega mendung lembut)*
- Gunakan **prompt** untuk fokus pada elemen tertentu:
  - Warna: `"navy"`, `"merah"`, `"emas"`, `"krem"`
  - Motif: `"floral"`, `"mega mendung"`, `"bunga besar"`, `"pohon"`
  - Suasana: `"cerah"`, `"gelap"`, `"kontras"`

### Workflow Cepat:

```
Pilih budaya → (opsional) filter prompt → klik template → "Pilih Template Ini" → upload foto → "Terapkan ke Baju"
```

### Filter Reset:

- Untuk melihat **semua** template lagi, kosongkan semua dropdown & prompt

---

## 🛠️ Troubleshooting

| Masalah | Solusi |
|---|---|
| Template tidak muncul | Pastikan Budaya 1 sudah dipilih, atau cek koneksi |
| Foto tidak terproses | Pastikan foto JPG/PNG, ukuran <10 MB, ada baju yang terlihat |
| Hasil mirip salah satu budaya saja | Coba kombinasi budaya lain, atau gunakan prompt spesifik |
| Loading lambat | Inference SDXL butuh GPU; mode CPU gratis mungkin >5 menit |

---

## 🧠 Info Teknis (untuk yang penasaran)

| Komponen | Detail |
|---|---|
| Base model | Stable Diffusion XL 1.0 |
| VAE | `madebyollin/sdxl-vae-fp16-fix` |
| LoRA | Joint training kohya-ss (network_dim=32) |
| Trigger token | `{region}batik` (mis. `madurabatik`) |
| Segmentasi pakaian | `rembg` + `u2net_cloth_seg` |
| Tiling | Feathered Seams (alpha blending) + Half-Drop pattern |

Setiap fusion menggabungkan **KEDUA trigger token** dalam prompt SDXL,
mis.:
```
a madurabatik jawa_baratbatik batik pattern, Dark navy blue fabric,
dense flowing gold cloud-like swirls, scattered blue floral sprigs, white dot clusters.
```

---

## 📞 Butuh Bantuan Lebih?

- Buka tab **Logs** di Hugging Face Space untuk lihat error
- Baca `PANDUAN_WEB_HUGGINGFACE.md` untuk detail deployment
- Baca `README.md` Space untuk info teknis