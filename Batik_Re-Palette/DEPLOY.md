# Panduan Deploy ke Hugging Face Spaces

Dokumen ini menjelaskan cara men-deploy aplikasi **Batik Re-Palette** (termasuk
fitur **Cultural Fusion 2 Budaya**) ke **Hugging Face Spaces** dan cara
men-upload file LoRA `.safetensors` ke Hugging Face Model Hub.

> **TL;DR** — Setelah deploy, user cukup:
> 1. Membuka link Space
> 2. Mengisi dua daerah budaya
> 3. Mengisi `Hugging Face Repo ID` + `Nama File .safetensors`
> 4. Klik **Buat Template Fusion**
>
> Tidak perlu edit kode lagi saat ganti LoRA.

---

## 1. Prasyarat

- Akun Hugging Face (gratis, daftar di <https://huggingface.co/join>)
- `huggingface_hub` terinstall di mesin lokal:
  ```bash
  pip install -U "huggingface_hub>=0.20.0"
  ```
- File LoRA `.safetensors` hasil training Anda (mis. dari
  `training2daerah.ipynb` -> `madura-jawa_barat-joint-lora-000XXX.safetensors`)

---

## 2. Login ke Hugging Face

```bash
huggingface-cli login
```

Tempelkan **Write Token** Anda (bukan yang read-only) dari
<https://huggingface.co/settings/tokens>.

Atau set env var:
```bash
# Windows PowerShell
$env:HF_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Linux/macOS
export HF_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

---

## 3. Push Kode Web ke Space (sekali jalan)

```bash
cd Batik_Re-Palette
python push_to_hf.py space --space-id username/batik-fusion-space
```

Ganti `username/batik-fusion-space` dengan `<hf-username>/<nama-space-anda>`.

**Apa yang terjadi:**
1. Script membuat Space baru (jika belum ada) dengan `sdk=gradio`
2. Upload seluruh isi folder `Batik_Re-Palette/` ke Space (skip file `.safetensors`)
3. Tunggu ~1-3 menit, Space akan live di:
   `https://huggingface.co/spaces/username/batik-fusion-space`

> **Tips:** Space butuh GPU T4 (free-tier tersedia). Pilih hardware **CPU basic**
> dulu kalau hanya untuk testing UI; pilih **T4 small** untuk inference SDXL+LoRA.

---

## 4. Upload LoRA ke Model Hub (per file LoRA)

```bash
python push_to_hf.py lora \
    --repo-id username/batik-joint-lora \
    --file "madura-jawa_barat-joint-lora-000004.safetensors"
```

Ganti:
- `username/batik-joint-lora` dengan `<hf-username>/<nama-repo-anda>`
- `madura-jawa_barat-joint-lora-000004.safetensors` dengan nama file Anda

**Atau upload beberapa file sekaligus** (glob pattern):
```bash
python push_to_hf.py lora \
    --repo-id username/batik-joint-lora \
    --file "*joint-lora*.safetensors"
```

File LoRA di repo model akan tampil di:
`https://huggingface.co/username/batik-joint-lora`

---

## 5. Jalankan Sekaligus (space + lora)

```bash
python push_to_hf.py all \
    --space-id username/batik-fusion-space \
    --repo-id username/batik-joint-lora \
    --file "*.safetensors"
```

---

## 6. Pakai di Web App

1. Buka Space Anda (mis. `https://huggingface.co/spaces/username/batik-fusion-space`)
2. Klik tab **"[FUSION] Cultural Fusion (2 Budaya)"**
3. Di kolom kiri, isi **HF Repo ID** = `username/batik-joint-lora`
4. Isi **Nama File .safetensors** = `madura-jawa_barat-joint-lora-000004.safetensors`
5. Pilih 2 budaya (mis. dropdown Madura + textbox "jawa_barat")
6. Isi tema & prompt tambahan (opsional)
7. Klik **"[FUSION] Buat Template Fusion"**
8. Hasil gambar fusion + narasi akan muncul di tengah
9. Klik **"[PAKAI] Kenakan ke Pakaian"** untuk simulasi di pojok kanan

**Tips berikutnya (ganti LoRA tanpa edit kode):**
- Upload LoRA baru ke repo model yang **sama**
- Di Space, tinggal ganti `Nama File .safetensors` ke nama file baru
- Klik Generate lagi — tidak perlu redeploy Space

---

## 7. Struktur File yang Di-upload ke Space

```
Batik_Re-Palette/
├── app.py                      # main entrypoint (wajib nama ini)
├── fusion_engine.py            # modul fusion 2 budaya
├── lora_generator.py           # modul SDXL + LoRA + HF download
├── requirements.txt            # dependency
├── README.md                   # metadata Space (sdk: gradio)
└── push_to_hf.py               # CLI untuk upload (tidak wajib di Space)
```

File yang **TIDAK** boleh di-upload ke Space (sudah di-skip otomatis):
- `*.safetensors` (terlalu besar, lebih baik di Model Hub)
- `__pycache__/`, `.git/`, `*.zip`

---

## 8. Troubleshooting

### ❌ Space error: `ModuleNotFoundError: No module named 'huggingface_hub'`
Pastikan `requirements.txt` mengandung `huggingface_hub>=0.20.0`. Rebuild Space.

### ❌ Space error: `Can't find networks.lora_diffusers`
Loader kohya-ss perlu repo `sd-scripts` di-clone. Di HF Space,
Anda perlu menambahkan repo itu sebagai submodule atau vendoring file
`networks/lora_diffusers.py` ke folder Space.

**Cara termudah:** download `lora_diffusers.py` dari
<https://github.com/kohya-ss/sd-scripts/blob/main/networks/lora_diffusers.py>
dan taruh di `Batik_Re-Palette/networks/lora_diffusers.py`. Modul
`lora_generator.py` akan otomatis menambah `./networks/` ke `sys.path`.

### ❌ Image generated flat/satu warna
VAE fp16-fix belum terpasang dengan benar. `lora_generator.py` sudah default
ke `madebyollin/sdxl-vae-fp16-fix` — pastikan tidak ditimpa.

### ❌ LoRA tidak berpengaruh di output
- Cek trigger token di prompt (harus ada `madurabatik jawa_baratbatik` atau sesuai key dataset)
- Cek `lora_scale` di slider (default 0.85, coba naikkan ke 1.0)
- Cek nama file `.safetensors` benar (case-sensitive, tanpa path folder)

### ❌ `Repository Not Found` saat download LoRA
- Pastikan repo model di-set **public** (atau set token dengan permission `read`)
- Cek penulisan `username/nama-repo` di input Space

---

## 9. Hardware & Biaya

| Hardware Space | Bisa SDXL+LoRA? | Biaya |
|---|---|---|
| CPU basic | Lambat (±60 detik/gambar) | Gratis |
| T4 small (16GB VRAM) | ✅ Recommended | Gratis (terbatas kuota) |
| A10G small (24GB VRAM) | ✅ Cepat | ~$3/jam |
| T4 medium | ✅ | Berbayar |

Untuk demo lomba, **T4 small** sudah cukup. Kuota GPU gratis Hugging Face
sekitar ~2 jam/hari (periksa halaman Space untuk status kuota).

---

## 10. Ringkasan Perintah

```bash
# Install dependency (sekali)
pip install -U "huggingface_hub>=0.20.0"

# Login (sekali)
huggingface-cli login

# Push kode web ke Space
python push_to_hf.py space --space-id USER/batik-fusion-space

# Upload LoRA ke Model Hub
python push_to_hf.py lora \
    --repo-id USER/batik-joint-lora \
    --file "nama-file.safetensors"

# (opsional) Push keduanya sekaligus
python push_to_hf.py all \
    --space-id USER/batik-fusion-space \
    --repo-id USER/batik-joint-lora \
    --file "*.safetensors"
```

Setelah langkah di atas, web app langsung bisa dipakai — cukup isi
`HF Repo ID` + `Nama File .safetensors` di UI.
