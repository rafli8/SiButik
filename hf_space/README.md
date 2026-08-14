---
title: SiButik - Silang Budaya Batik
emoji: 🎨
colorFrom: yellow
colorTo: yellow
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: mit
hardware: t4-small
---

# SiButik: Silang Budaya Batik Nusantara

Generator **Cultural Fusion Batik** yang menggabungkan dua tradisi batik
daerah Nusantara menjadi satu kain fusion, dengan memanfaatkan
**Stable Diffusion XL + LoRA Joint Training** (kohya-ss).

## 🎯 Fitur

1. **Generator** — pilih 2 budaya, tulis prompt tambahan, sistem akan
   menghasilkan deskripsi fusion dengan trigger token LoRA.
2. **Template Carousel** — slide 10 template fusion siap-pakai
   (image + narasi budaya + prompt SDXL).
3. **Terapkan ke Baju** — segmentasi area pakaian otomatis
   (rembg `u2net_cloth_seg`) + tiling Feathered Seams Half-Drop.

## 🧠 Model

| Komponen | Detail |
|---|---|
| Base model | `stabilityai/stable-diffusion-xl-base-1.0` |
| VAE | `madebyollin/sdxl-vae-fp16-fix` |
| LoRA | Joint training kohya-ss, network_dim=32, network_alpha=16 |
| LoRA file | `madura-madura_pola_kompleks-joint-lora-000004.safetensors` |

## ⚙️ Hardware

Disarankan **GPU T4 small** (Hugging Face Pro). Mode CPU basic gratis
bisa dipakai tapi inference SDXL lambat (~5–10 menit per gambar).

## 🚀 Cara Pakai

1. Buka tab **Generator**
2. Pilih **Budaya 1** (wajib) — mis. "Madura — Pola Kompleks"
3. Pilih **Budaya 2** (opsional) — mis. "Jawa Barat"
4. Opsional: tulis prompt filter di kolom Prompt
5. Klik salah satu template di carousel → klik **Pilih Template Ini**
6. Di tab **Terapkan ke Baju**, upload foto orang lalu klik **Terapkan ke Baju**

## 📁 Struktur Repo

```
.
├── app.py                     # Gradio entry point
├── requirements.txt
├── lora_generator.py          # SDXL + LoRA inference
├── fusion_engine.py           # Logika generator narasi fusion
├── fusion_matcher.py
├── networks/lora_diffusers.py # Custom kohya-ss LoRA loader (SDXL 2 text encoder)
├── fusion_descriptions.json   # Data 21 fusion
├── *.safetensors              # LoRA weights
└── showcase/                  # Hasil fusion statis (preview)
    ├── index.html
    ├── images/
    └── descriptions/
```

## 📝 Catatan

- Trigger token mengikuti format training: `{region}batik`
  (mis. `madurabatik`, `jawa_baratbatik`)
- Untuk fusion 2 daerah, sertakan **KEDUA** trigger di prompt.
- Folder `showcase/` hanya untuk preview statis — tidak diakses oleh `app.py`.