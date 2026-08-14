---
title: Batik Fusion Showcase
emoji: 🎨
colorFrom: yellow
colorTo: orange
sdk: static
pinned: false
license: mit
---

# Batik Fusion Showcase - Cultural Fusion 2 Budaya

Showcase hasil **Cultural Fusion Batik** dari dua daerah Nusantara, di-generate
dengan **Stable Diffusion XL + LoRA Joint Training** (kohya-ss).

## 📦 Konten Showcase

- **13 daerah batik** Nusantara (Madura, Jawa Barat, Jawa Tengah, Yogyakarta, Bali, Kalimantan, Sulawesi, Papua, Sumatera, Nusa Tenggara, dll.)
- **Trigger token per daerah** mengikuti format training: `{region}batik`
- **Setiap fusion** menyertakan KEDUA trigger token, sehingga motif khas
  kedua daerah tercermin dalam satu kain batik fusion

## 🧠 Tentang Proyek

| Komponen | Detail |
|---|---|
| Base model | `stabilityai/stable-diffusion-xl-base-1.0` |
| VAE | `madebyollin/sdxl-vae-fp16-fix` |
| LoRA training | Joint training (kohya-ss), network_dim=32, network_alpha=16 |
| Captioning | Auto-captioning dengan Qwen3-VL-8B |
| Training dataset | 7 daerah (madura, madura_pola_kompleks, madura_pola_sederhana, jawa_barat, jawa_tengah, jawa_timur, yogyakarta) |

## 🚀 Cara Generate Sendiri (Opsional)

Prasyarat: GPU (Kaggle gratis / Google Colab / lokal).

```bash
# Di Kaggle Notebook (GPU T4) - lihat PANDUAN_STATIC.md untuk detail
!pip install -q diffusers==0.32.1 transformers accelerate safetensors
!git clone -q https://github.com/kohya-ss/sd-scripts.git

# Load SDXL + LoRA, generate fusion
# (lihat notebook template di PANDUAN_STATIC.md Step 1)
```

## 📚 Dokumentasi Lengkap

Lihat di folder ini:
- `PANDUAN_STATIC.md` — Deploy showcase **GRATIS** (HF Static / GitHub Pages / Netlify)
- `PANDUAN_WEB_HUGGINGFACE.md` — Deploy web interaktif (perlu GPU, opsional)
- `DEPLOY.md` — Panduan teknis + troubleshooting

## 📁 Struktur File Showcase (yang ditampilkan di Space ini)

```
showcase/
├── index.html         ← Gallery entrypoint
├── styles.css         ← Styling
├── images/            ← Gambar fusion (PNG)
└── descriptions/      ← Markdown penjelasan per fusion
```

## 🛠️ Development Lokal

```bash
# Install dependency
pip install -r requirements.txt

# Jalankan Gradio interaktif (perlu GPU)
python app.py

# Generate showcase statis (perlu GPU)
python generate_showcase.py
python generate_index_html.py
```

## 📜 Lisensi

MIT
