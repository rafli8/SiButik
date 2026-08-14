# Panduan Deployment STATIS (100% GRATIS - Tanpa GPU)

> 🎯 **Target:** Deploy showcase batik fusion sebagai website statis (HTML + gambar) yang **GRATIS TOTAL** — tidak perlu bayar GPU, tidak perlu T4, tidak ada kuota harian.
>
> ⏱️ **Estimasi waktu:** 20-30 menit (generate gambar 1x, lalu upload static forever)
>
> 💡 **Konsep:** Generate gambar fusion **sekali** di Kaggle (gratis GPU), simpan ke folder, upload sebagai HTML statis ke Hugging Face Static Space / GitHub Pages / Netlify.

---

## 📋 Kenapa Pakai Static?

| Opsi | Biaya | Generate Ulang? | Cocok Untuk |
|---|---|---|---|
| **Hugging Face Gradio (CPU)** | Gratis tapi **sangat lambat** | Ya, on-demand | ❌ Tidak cocok |
| **Hugging Face Gradio (T4 GPU)** | Gratis + kuota ~2 jam/hari | Ya, on-demand | ✅ Lomba interaktif |
| **Hugging Face Static Space** | **GRATIS SELAMANYA** | ❌ Tidak (gambar tetap) | ✅ Demo lomba |
| **GitHub Pages** | **GRATIS SELAMANYA** | ❌ Tidak (gambar tetap) | ✅ Demo lomba |
| **Netlify / Vercel** | **GRATIS SELAMANYA** | ❌ Tidak (gambar tetap) | ✅ Demo lomba |

**Strategi untuk lomba:** Generate gambar fusion di **Kaggle (gratis GPU)** sekali, simpan sebagai showcase statis, upload ke **GitHub Pages** atau **HF Static Space**.

---

## 🎯 DAFTAR ISI

1. [Konsep: Hybrid Kaggle + Static Hosting](#1-konsep)
2. [Step 1: Generate Gambar di Kaggle](#2-step1-kaggle)
3. [Step 2: Download Hasil ke Lokal](#3-step2-download)
4. [Step 3: Buat HTML Gallery Lokal](#4-step3-html)
5. [Step 4: Deploy ke Hugging Face Static Space](#5-step4-hf-static)
6. [Alternatif: Deploy ke GitHub Pages](#6-github-pages)
7. [Alternatif: Deploy ke Netlify (Drag & Drop)](#7-netlify)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Konsep: Hybrid Kaggle + Static Hosting

```
┌─────────────────────┐        ┌──────────────────┐        ┌──────────────────┐
│   KAGGLE NOTEBOOK    │        │   LOKAL (PC)     │        │  STATIC HOSTING  │
│  ─────────────────  │        │  ──────────────  │        │  ──────────────  │
│  • GPU T4 GRATIS     │  ───►  │ • Download PNG   │  ───►  │ • HTML statis    │
│  • Load SDXL+LoRA   │  ZIP   │ • Generate HTML  │  UPLOAD│ • Gratis forever │
│  • Generate 4 fusion │        │ • Generate CSS   │        │ • Loading cepat   │
│  • Save ke /kaggle/  │        │ • Preview lokal  │        │ • Publik         │
│   working/output/   │        │                  │        │                  │
└─────────────────────┘        └──────────────────┘        └──────────────────┘
```

**Workflow:**
1. **Sekali:** Generate 4 gambar fusion di Kaggle (pakai GPU gratis T4)
2. **Sekali:** Download hasil ke PC, generate HTML gallery
3. **Upload 1x:** HTML statis ke Hugging Face / GitHub Pages
4. **Selesai:** Showcase live selamanya, **tidak perlu GPU lagi**

---

## 2. Step 1: Generate Gambar di Kaggle (Pakai GPU Gratis)

### 2.1. Buat Kaggle Notebook baru

1. Buka <https://www.kaggle.com/code>
2. Klik **"+ New Notebook"**
3. Klik **"Add Input"** (kanan atas), tambahkan 2 input:
   - **Repo dataset LoRA** (mis. `username/batik-joint-lora` di Kaggle Datasets)
   - **Base model SDXL** (`stabilityai/stable-diffusion-xl-base-1-0`)
4. Klik **"Add Input"** lagi, tambahkan **VAE fp16-fix** (`madebyollin/sdxl-vae-fp16-fix`)
5. **Set Accelerator: GPU T4 x1** (di sidebar kanan)

### 2.2. Buat Sel Notebook untuk Install

**Sel 1:** Install dependencies
```python
!pip install -q diffusers==0.32.1 transformers accelerate safetensors
```

**Sel 2:** Clone sd-scripts (untuk loader LoRA native)
```python
!git clone -q https://github.com/kohya-ss/sd-scripts.git
import sys
sys.path.insert(0, "/kaggle/working/sd-scripts")
```

### 2.3. Buat Sel untuk Load Model + LoRA

**Sel 3:** Load SDXL pipeline + LoRA
```python
import torch
from diffusers import StableDiffusionXLPipeline, AutoencoderKL
from safetensors.torch import load_file
from networks.lora_diffusers import create_network_from_weights

BASE_MODEL = "/kaggle/input/stable-diffusion-xl-base-1-0"  # sesuaikan path
VAE_ID = "/kaggle/input/sdxl-vae-fp16-fix"  # sesuaikan path
LORA_FILE = "/kaggle/input/your-lora-repo/madura-madura_pola_kompleks-joint-lora-000001.safetensors"

fixed_vae = AutoencoderKL.from_pretrained(VAE_ID, torch_dtype=torch.float16)

pipe = StableDiffusionXLPipeline.from_pretrained(
    BASE_MODEL,
    vae=fixed_vae,
    torch_dtype=torch.float16,
    variant="fp16",
    use_safetensors=True,
).to("cuda")
pipe.set_progress_bar_config(disable=True)

text_encoders = [pipe.text_encoder, pipe.text_encoder_2]
lora_sd = load_file(LORA_FILE)
network = create_network_from_weights(text_encoders, pipe.unet, lora_sd, multiplier=1.0)
network.load_state_dict(lora_sd)
network.to("cuda", dtype=pipe.unet.dtype)
print("SDXL + LoRA siap!")
```

### 2.4. Buat Sel untuk Generate Fusion

**Sel 4:** Generate 4 gambar fusion untuk showcase
```python
import os
from PIL import Image

OUTPUT_DIR = "/kaggle/working/showcase/images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

PASANGAN = [
    ("madura", "jawa_barat"),
    ("madura_pola_kompleks", "jawa_barat"),
    ("madura", "jawa_tengah"),
    ("madura", "yogyakarta"),
]

NEGATIVE = "blurry, low quality, deformed, watermark, text, extra limbs"
TEMPLATE = "a {tr1} {tr2} batik pattern, fusion of {n1} and {n2} culture, {tema}, intricate detail, symmetrical composition, traditional indonesian textile art"

for d1, d2 in PASANGAN:
    prompt = TEMPLATE.format(
        tr1=f"{d1}batik", tr2=f"{d2}batik",
        n1=d1.replace("_", " ").title(), n2=d2.replace("_", " ").title(),
        tema="harmoni budaya nusantara",
    )
    print(f"\n[Generating] {d1} x {d2}")
    print(f"  Prompt: {prompt}")

    network.set_multiplier(1.0)
    network.merge_to()
    try:
        gen = torch.Generator(device="cuda").manual_seed(42)
        img = pipe(prompt, negative_prompt=NEGATIVE, num_inference_steps=25,
                   guidance_scale=7.0, height=1024, width=1024, generator=gen).images[0]
    finally:
        network.restore_from()

    nama_file = f"{d1}_{d2}.png".replace(" ", "_")
    img.save(os.path.join(OUTPUT_DIR, nama_file))
    print(f"  [OK] Saved: {nama_file}")

print("\nSelesai! Semua gambar ada di:", OUTPUT_DIR)
```

### 2.5. Zip & Download

**Sel 5:** Zip output untuk download
```python
!cd /kaggle/working/showcase && zip -r /kaggle/working/showcase_images.zip images/
print("Download file: /kaggle/working/showcase_images.zip")
```

**Download dari Kaggle:**
1. Klik tab **"Output"** (kanan panel)
2. Klik kanan file `showcase_images.zip` → **Download**
3. Simpan ke folder `Batik_Re-Palette/showcase/`
4. Ekstrak ZIP — pastikan struktur: `Batik_Re-Palette/showcase/images/*.png`

---

## 3. Step 2: Download Hasil ke Lokal

Setelah download ZIP dan ekstrak, struktur folder Anda:

```
Batik_Re-Palette/
└── showcase/
    └── images/
        ├── madura_jawa_barat.png
        ├── madura_pola_kompleks_jawa_barat.png
        ├── madura_jawa_tengah.png
        └── madura_yogyakarta.png
```

Pastikan nama file **persis** seperti itu (format `<daerah1>_<daerah2>.png`).

---

## 4. Step 3: Buat HTML Gallery Lokal

### 4.1. Generate HTML otomatis

```bash
cd Batik_Re-Palette
python generate_showcase.py
python generate_index_html.py
```

**Output:** folder `showcase/` sekarang berisi:
```
showcase/
├── index.html         ← Gallery siap upload
├── styles.css         ← Styling
├── images/            ← 4 gambar PNG
├── descriptions/      ← 4 markdown penjelasan
└── metadata.json      ← Info untuk generate_index_html
```

> **Note:** `generate_showcase.py` akan coba download LoRA dari HF Hub. Kalau gagal, otomatis pakai generator sintetis (gambar batik dummy — bukan hasil asli LoRA). Untuk hasil asli, **pakai Kaggle (Step 1)** sebagai gantinya.

### 4.2. Preview lokal

1. Buka File Explorer → masuk ke `Batik_Re-Palette/showcase/`
2. Klik 2x `index.html` → terbuka di browser default
3. Anda akan lihat gallery statis dengan 4 gambar fusion
4. Klik salah satu card → akan download/tampilkan file markdown penjelasan

### 4.3. (Opsional) Edit sebelum upload

Buka `index.html` di VSCode, edit:
- **Footer** — ganti `Riset MBKM` dengan nama Anda
- **Header** — tambahkan logo atau deskripsi
- **Style** — edit `styles.css` sesuai branding Anda

---

## 5. Step 4: Deploy ke Hugging Face STATIC Space (100% GRATIS)

### 5.1. Buat Static Space baru

1. Buka <https://huggingface.co/new-space>
2. Isi formulir:
   - **Space name:** `batik-fusion-showcase` (nama bebas)
   - **Space SDK:** pilih **Static** ← PENTING! bukan Gradio/Streamlit
   - **Visibility:** Public
3. Klik **Create Space**

Anda akan dibawa ke `https://huggingface.co/spaces/USERNAME/batik-fusion-showcase`

### 5.2. Upload file showcase

1. Di Space, klik tab **"Files"** (atas)
2. Klik tombol **"+ Add file"** → **"Upload files"**
3. **Drag & drop** semua file dari folder `Batik_Re-Palette/showcase/`:
   - `index.html`
   - `styles.css`
4. Klik **"Add file"** → **"Upload folder"** untuk upload folder `images/` dan `descriptions/`

**Atau lebih mudah, upload sekaligus:**
1. Klik **"+ Add file"** → **"Upload folder"**
2. Pilih folder `Batik_Re-Palette/showcase/`
3. Commit

### 5.3. Konfigurasi index.html sebagai entrypoint

1. Di tab **"Files"**, klik file `README.md`
2. Klik icon pensil (Edit)
3. Ganti isinya dengan:
   ```yaml
   ---
   title: Batik Fusion Showcase
   emoji: 🎨
   colorFrom: yellow
   colorTo: orange
   sdk: static
   pinned: false
   license: mit
   ---
   ```
4. Klik **"Commit changes"**

5. Klik tab **"Settings"** → **"Source"** (jika ada) atau langsung cek apakah sudah otomatis detect `index.html` sebagai entrypoint

### 5.4. Selesai!

Showcase live di:
```
https://huggingface.co/spaces/USERNAME/batik-fusion-showcase
```

**Biaya:** **GRATIS SELAMANYA**, tidak perlu GPU, tidak ada kuota.

---

## 6. Alternatif: Deploy ke GitHub Pages (100% GRATIS)

### 6.1. Buat GitHub Repository

1. Buka <https://github.com/new>
2. Isi:
   - **Repository name:** `batik-fusion-showcase` (atau nama bebas)
   - **Visibility:** Public
3. Klik **"Create repository"**

### 6.2. Push folder showcase

Cara termudah dengan GitHub Desktop:

1. Download & install **GitHub Desktop** dari <https://desktop.github.com>
2. **File** → **New Repository** → **Local path** pilih `Batik_Re-Palette/showcase/`
3. Klik **"Create repository"**
4. Klik **"Publish repository"** (kanan atas) → pilih akun Anda
5. Selesai!

### 6.3. Aktifkan GitHub Pages

1. Buka repo GitHub Anda: `https://github.com/USERNAME/batik-fusion-showcase`
2. Klik tab **"Settings"** (kanan atas)
3. Klik **"Pages"** di sidebar kiri
4. **Source:** pilih **"Deploy from a branch"**
5. **Branch:** pilih `main` (atau `master`), folder `/ (root)`
6. Klik **"Save"**
7. Tunggu 1-2 menit untuk deploy

Showcase live di:
```
https://USERNAME.github.io/batik-fusion-showcase/
```

**Biaya:** **GRATIS SELAMANYA**.

---

## 7. Alternatif: Deploy ke Netlify (Drag & Drop)

Cara **paling cepat** tanpa Git/GitHub:

1. Buka <https://app.netlify.com/drop>
2. **Drag & drop** folder `Batik_Re-Palette/showcase/` langsung ke halaman
3. Tunggu 10-30 detik
4. Netlify otomatis generate URL publik

Showcase live di:
```
https://random-name-12345.netlify.app
```

**Bonus:** Bisa custom domain gratis.

**Biaya:** **GRATIS SELAMANYA**.

---

## 8. Troubleshooting

### ❌ Kaggle: `LORA_FILE` not found
Path ke file `.safetensors` salah. Cek:
- Sudah upload LoRA ke Kaggle Datasets?
- Sudah "Add Input" di notebook?
- Path lengkapnya: `/kaggle/input/<slug-dataset>/<nama-file>.safetensors`

### ❌ Kaggle: `Can't find networks.lora_diffusers`
Sel `!git clone` belum dijalankan. Jalankan dulu sebelum import.

### ❌ Hugging Face Static: `404 Not Found`
- Pastikan `index.html` ada di root Space (bukan di subfolder)
- Tunggu 1-2 menit setelah upload — kadang propagation lambat

### ❌ Gambar tidak muncul di gallery
- Cek path di `index.html`: `<img src="images/madura_jawa_barat.png">` (relative)
- Pastikan file gambar ada di folder `images/` di Space
- Hard refresh browser (Ctrl+Shift+R)

### ❌ GitHub Pages: `404`
- Tunggu 1-3 menit setelah enable Pages
- Cek tab **"Actions"** di repo — pastikan workflow deploy sukses
- Pastikan branch `main` dan folder `/ (root)` dipilih

### ❌ Netlify: `Page Not Found`
- Refresh halaman
- Cek di dashboard Netlify → tab **"Deploys"** → pastikan status "Published"

---

## 🎉 Selesai!

Anda sekarang punya showcase batik fusion yang **GRATIS SELAMANYA** dengan 3 pilihan hosting:

| Hosting | URL | Biaya |
|---|---|---|
| Hugging Face Static | `https://huggingface.co/spaces/USER/batik-fusion-showcase` | GRATIS |
| GitHub Pages | `https://USER.github.io/batik-fusion-showcase/` | GRATIS |
| Netlify | `https://xxx.netlify.app` | GRATIS |

Kalau ada error spesifik, kasih tahu detail pesan error + langkah mana yang gagal, nanti saya bantu debug. 🎨