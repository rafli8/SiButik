# Panduan Step-by-Step Upload LoRA Lewat WEB Hugging Face (Tanpa Terminal)

> 🎯 **Target:** Upload file `madura-madura_pola_kompleks-joint-lora-000001.safetensors` ke Hugging Face, lalu deploy web Batik Fusion, dan coba-coba dengan LoRA yang baru di-upload.
>
> ⏱️ **Estimasi waktu:** 10–15 menit (untuk pemula Hugging Face)
>
> 💡 **Catatan:** Semua langkah dilakukan lewat **browser** (Chrome / Edge / Firefox). Tidak perlu install Python / pip / Git.

---

## 📋 DAFTAR ISI

1. [Buat akun Hugging Face](#1-buat-akun-hugging-face)
2. [Buat token akses (kunci API)](#2-buat-token-akses-kunci-api)
3. [Upload file LoRA ke Model Hub](#3-upload-file-lora-ke-model-hub)
4. [Buat Space untuk web app](#4-buat-space-untuk-web-app)
5. [Upload kode web ke Space](#5-upload-kode-web-ke-space)
6. [Set hardware Space ke GPU](#6-set-hardware-space-ke-gpu)
7. [Konfigurasi di web app](#7-konfigurasi-di-web-app)
8. [Coba generate fusion](#8-coba-generate-fusion)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Buat Akun Hugging Face

1. Buka <https://huggingface.co/join>
2. Isi:
   - **Email** — email aktif Anda
   - **Password** — minimal 8 karakter
   - **Username** — nama unik yang akan jadi identitas publik Anda
3. Klik **Sign Up**
4. Buka **email Anda**, klik link konfirmasi dari Hugging Face
5. Setelah login, Anda akan dibawa ke <https://huggingface.co/>

> 💾 **Simpan info ini:**
> - Username: `__________________` (mis. `johndoe`)
> - Email: `__________________`

---

## 2. Buat Token Akses (Kunci API)

Token ini seperti "kunci rumah" — dipakai tiap kali Anda upload file atau push kode lewat web.

1. Buka <https://huggingface.co/settings/tokens>
2. Klik tombol **"+ Create new token"** (kanan atas)
3. Isi formulir:
   - **Token type:** pilih **Write** (penting! kalau pilih Read, tidak bisa upload)
   - **Token name:** ketik `batik-upload` (nama bebas, hanya untuk pengingat Anda)
   - **Description:** (opsional) ketik `Untuk upload LoRA batik & deploy web app`
4. Klik **Create token**
5. **TOKEN AKAN MUNCUL 1 KALI SAJA** — langsung di-copy ke clipboard atau dicatat manual
   - Contoh bentuknya: `hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
6. **Tempel & simpan token ini** di Notes / manajer password Anda

> 🔒 **Jangan bagikan token ini ke siapa pun**! Siapa pun yang punya token ini bisa upload file atas nama Anda.

> 💾 **Simpan token:**
> - Token: `hf________________________`

---

## 3. Upload File LoRA ke Model Hub

> 🎯 Tahap ini: file `.safetensors` Anda akan disimpan di URL publik, mis. `https://huggingface.co/johndoe/batik-joint-lora`

### 3.1. Buat repository baru untuk LoRA

1. Buka <https://huggingface.co/new>
2. Isi formulir **Create a new repository**:
   - **Owner:** otomatis terisi username Anda (jangan diubah)
   - **Repository name:** ketik `batik-joint-lora` (nama bebas, tanpa spasi)
   - **License:** pilih `mit` (atau `apache-2.0`, terserah)
   - **Visibility:** pilih **Public** (supaya Space bisa download gratis)
     - Kalau pilih **Private**, Anda harus set token di Space, lebih ribet
3. Klik **Create repository**

Anda akan dibawa ke halaman repo kosong: `https://huggingface.co/johndoe/batik-joint-lora`

### 3.2. Upload file `.safetensors`

Anda akan berada di halaman repo kosong. Sekarang upload file:

**Cara A: Drag & Drop (Termudah)**

1. Di halaman repo Anda (`https://huggingface.co/johndoe/batik-joint-lora`), cari section **"Files and versions"**
2. Anda akan lihat area **"Contribute"** atau tombol **"+ Add file"**
3. Drag & drop file `madura-madura_pola_kompleks-joint-lora-000001.safetensors` dari File Explorer Windows langsung ke area tersebut
4. Tunggu progress upload selesai (±1-3 menit untuk file 100-300 MB)

**Cara B: Klik tombol upload (Kalau drag & drop tidak jalan)**

1. Klik tombol **"+ Add file"** atau **"Upload files"**
2. Pilih **"Upload files"** (bukan "Upload folder")
3. Klik area **"Drop files here or click to browse"**
4. Pilih file `madura-madura_pola_kompleks-joint-lora-000001.safetensors` dari File Explorer
5. Tunggu upload selesai

### 3.3. Tulis commit message & upload

Setelah file dipilih:

1. Di kolom **"Commit message"** ketik: `Upload joint LoRA madura + jawa_barat`
2. Klik tombol **"Commit changes to main"** (warna hijau, bawah form)
3. Tunggu ~30 detik untuk processing
4. Setelah selesai, file akan muncul di daftar file repo

### 3.4. Verifikasi upload berhasil

1. Refresh halaman repo `https://huggingface.co/johndoe/batik-joint-lora`
2. Anda harus lihat:
   ```
   📁 Files and versions
      📄 madura-madura_pola_kompleks-joint-lora-000001.safetensors  ~200 MB
   ```
3. Klik file → akan terbuka halaman preview file dengan **Download** button

> 💾 **Simpan URL ini:**
> - URL LoRA: `https://huggingface.co/johndoe/batik-joint-lora`
> - **HF Repo ID**: `johndoe/batik-joint-lora` ← ini yang akan dipakai di web app
> - **Nama file**: `madura-madura_pola_kompleks-joint-lora-000001.safetensors`

---

## 4. Buat Space untuk Web App

> 🎯 Tahap ini: container kosong untuk menjalankan aplikasi Gradio Anda di Hugging Face

### 4.1. Buat Space baru

1. Buka <https://huggingface.co/new-space>
2. Isi formulir **Create a new Space**:
   - **Owner:** otomatis username Anda
   - **Space name:** ketik `batik-fusion-space` (nama bebas, tanpa spasi)
   - **License:** pilih `mit`
   - **Space SDK:** pilih **Gradio** ← PENTING! jangan pilih yang lain
   - **Space hardware:** pilih **CPU basic** dulu untuk test (bisa diubah nanti ke GPU)
     - Nanti di step 6 akan diubah ke **T4 small** untuk inference
   - **Visibility:** pilih **Public**
3. Klik **Create Space**

Anda akan dibawa ke halaman Space baru: `https://huggingface.co/spaces/johndoe/batik-fusion-space`

Space akan mulai building otomatis (pertama kali butuh 2-5 menit).

### 4.2. Tunggu build selesai, lalu matikan auto-start

1. Tunggu sampai tab **"Logs"** menunjukkan "Application startup complete" (build awal biasanya gagal karena file belum lengkap — tidak masalah)
2. Klik tab **"Settings"** (di bagian atas halaman Space)
3. Cari bagian **"Factory Reboot"** atau **"Sleep Time"**
4. Set **Sleep Time: Never** (supaya Space tetap hidup untuk debugging)
   - Nanti setelah konfigurasi, bisa set ke **Sleep after 48 hours of inactivity**

---

## 5. Upload Kode Web ke Space

> 🎯 Sekarang upload semua file `app.py`, `lora_generator.py`, `fusion_engine.py`, dll. ke Space

### 5.1. Buka tab Files di Space

1. Di Space Anda (`https://huggingface.co/spaces/johndoe/batik-fusion-space`), klik tab **"Files"** di bagian atas
2. Anda akan lihat struktur folder Space

### 5.2. Upload file-file penting (SATU PER SATU)

Untuk setiap file di bawah ini, lakukan langkah **"Add file → Upload files"**:

| File lokal | Keterangan |
|---|---|
| `app.py` | WAJIB — entrypoint utama |
| `lora_generator.py` | Modul SDXL + LoRA |
| `fusion_engine.py` | Modul fusion 2 budaya |
| `requirements.txt` | Daftar dependency Python |
| `README.md` | Metadata Space (sudah ada YAML di atas) |

**Cara upload per file:**

1. Klik tombol **"+ Add file"** (di kanan atas daftar file)
2. Pilih **"Upload files"** dari dropdown
3. Klik area upload atau drag file
4. Pilih file dari folder `Batik_Re-Palette/` di komputer Anda
5. Tunggu upload selesai
6. Kolom **Commit message**: ketik `Add app.py` (atau nama file yang di-upload)
7. Klik **"Commit changes to main"** (hijau)
8. Tunggu 5-10 detik sampai file muncul di daftar
9. Ulangi untuk file berikutnya

### 5.3. Tips urutan upload

Upload dengan urutan ini (supaya Space bisa build dengan benar):
1. `requirements.txt` ← dibaca duluan saat build
2. `lora_generator.py`
3. `fusion_engine.py`
4. `app.py` ← dibaca terakhir saat start
5. `README.md`

### 5.4. (Opsional) Upload folder `networks/`

Modul `lora_generator.py` butuh file `networks/lora_diffusers.py` dari repo `kohya-ss/sd-scripts`. Cara upload folder:

**Cara A: Upload satu per satu (dari dalam folder)**

1. Buka link ini di tab baru: <https://raw.githubusercontent.com/kohya-ss/sd-scripts/main/networks/lora_diffusers.py>
2. Klik kanan → **Save As** → simpan sebagai `lora_diffusers.py` di folder `Batik_Re-Palette/networks/`
3. Di Hugging Face Space → klik **"+ Add file"** → **"Upload folder"**
4. Pilih folder `Batik_Re-Palette/networks/`
5. Commit

**Cara B: Lewat Git (alternatif, lebih cepat)**

1. Buka terminal lokal Anda (PowerShell / Git Bash)
2. Jalankan:
   ```bash
   cd Batik_Re-Palette
   git clone https://github.com/kohya-ss/sd-scripts.git
   cp sd-scripts/networks/lora_diffusers.py networks/
   ```
3. Upload folder `networks/` lewat **"Upload folder"** di Space

> ⚠️ **Sangat disarankan** untuk upload `networks/lora_diffusers.py` — kalau tidak, Space akan error `ModuleNotFoundError: No module named 'networks.lora_diffusers'`

### 5.5. Verifikasi semua file sudah ter-upload

1. Di tab **"Files"**, Anda harus lihat minimal:
   ```
   📁 Files
      📄 README.md
      📄 app.py
      📄 lora_generator.py
      📄 fusion_engine.py
      📄 requirements.txt
      📁 networks/
         📄 lora_diffusers.py
   ```

---

## 6. Set Hardware Space ke GPU

> ⚠️ **PENTING!** Inference SDXL+LoRA tanpa GPU akan sangat lambat (>2 menit per gambar).

1. Klik tab **"Settings"** di halaman Space
2. Gulir ke bagian **"Space hardware"**
3. Pilih **T4 small** dari dropdown:
   ```
   Space hardware: [T4 small ▼]
   ```
   - Biayanya: **GRATIS** tapi ada **kuota harian ~2 jam**
   - Untuk demo lomba, sudah cukup
4. Klik **Save** di bagian bawah

> ⏳ Tunggu ~30 detik sampai Space restart dengan hardware baru.

---

## 7. Konfigurasi di Web App

1. Buka URL Space Anda: `https://huggingface.co/spaces/johndoe/batik-fusion-space`
2. Tunggu ~3-5 menit untuk first-time build (download SDXL, rembg, dll.)
   - Lihat tab **"Logs"** untuk memantau progress
   - Build sukses = ada pesan **"Running on local URL: http://0.0.0.0:7860"**
3. Setelah Space live, Anda akan lihat UI Gradio dengan 3 tab:
   - "Dari Gambar Referensi"
   - "Pilih Warna Manual"
   - **"[FUSION] Cultural Fusion (2 Budaya)"** ← yang kita pakai

4. Klik tab **"[FUSION] Cultural Fusion (2 Budaya)"**

### 7.1. Isi kolom di sebelah kiri

| Field | Isi dengan | Contoh |
|---|---|---|
| **Hugging Face Repo ID** | Username/nama-repo-anda | `johndoe/batik-joint-lora` |
| **Nama File .safetensors** | Nama file persis seperti yang di-upload | `madura-madura_pola_kompleks-joint-lora-000001.safetensors` |
| **Budaya 1** | Pilih dari dropdown | `madura` |
| **Prompt tambahan Budaya 1** | (Opsional) Deskripsi visual tambahan | `dark navy with floral sprigs and birds` |
| **Budaya 2** | Ketik manual atau pilih dropdown | `jawa_barat` |
| **Prompt tambahan Budaya 2** | (Opsional) Deskripsi visual tambahan | `gold cloud-like swirls on navy` |
| **Tema Fusion** | Tema naratif | `harmoni budaya nusantara` |
| **Kekuatan LoRA** | Slider 0.0-1.5 | `0.85` |
| **Langkah Inferensi** | Slider 10-50 | `25` |
| **Seed** | `-1` untuk acak | `-1` |

5. Klik tombol **[FUSION] Buat Template Fusion** (warna primary biru)

---

## 8. Coba Generate Fusion

### 8.1. Tunggu generate selesai

- Pertama kali klik tombol, Space akan download SDXL + LoRA dari HF Hub:
  ```
  ⏳ Download SDXL... (3-5 menit)
  ⏳ Download LoRA... (1-2 menit, cached setelah itu)
  ⏳ Generating fusion... (15-30 detik per gambar)
  ```
- Total: ~5-10 menit untuk pertama kali, ~20-30 detik setelah cached

### 8.2. Lihat hasil

Hasil akan muncul di **kolom tengah**:
- 🖼️ **Gambar fusion batik** (1024x1024 px)
- 📝 **Narasi markdown** yang menjelaskan:
  - Judul fusion
  - Deskripsi singkat
  - **Yang Diambil dari Daerah 1** (trigger token + warna + motif + pola)
  - **Yang Diambil dari Daerah 2**
  - Filosofi fusion
  - Penggunaan yang cocok
  - Prompt yang dipakai

### 8.3. Simulasi jadi pakaian (pojok kanan)

1. Upload foto orang berbaju (PNG/JPG, max ~5 MB) di **kolom kanan** "Foto Orang Berbaju"
2. Geser slider:
   - **Intensitas** = 1.0 (default)
   - **Ukuran Motif** = 1.0 (default)
3. Klik tombol **[PAKAI] Kenakan ke Pakaian**
4. Hasil simulasi batik di baju akan muncul di bawahnya (pojok kanan)

### 8.4. Eksperimen

Coba variasikan untuk eksplorasi:
- 🔄 **Ganti dropdown Budaya 1/2** ke daerah lain (Bali, Papua, dll.) — lihat apakah motifnya ikut berganti
- 🎲 **Ganti seed** (mis. `42`, `123`, dst) untuk lihat variasi prompt yang sama
- 📈 **Naikkan LoRA scale** ke 1.0 atau 1.2 untuk motif lebih kuat
- 📉 **Turunkan steps** ke 15 untuk hasil lebih cepat (kualitas turun dikit)

---

## 9. Troubleshooting

### ❌ Space stuck di "Building..."
1. Buka tab **Logs**
2. Lihat error message di paling bawah
3. Biasanya karena:
   - `requirements.txt` ada library yang salah nama
   - File Python missing
   - Space hardware T4 kehabisan kuota

**Solusi:** Edit `requirements.txt` di tab Files → klik icon pensil → Save → Space rebuild otomatis.

### ❌ Error: `ModuleNotFoundError: No module named 'huggingface_hub'`
**Penyebab:** Library `huggingface_hub` belum ada di `requirements.txt`.

**Solusi:**
1. Buka tab **Files** → klik `requirements.txt`
2. Klik icon pensil (Edit)
3. Pastikan isinya:
   ```
   gradio>=4.0.0
   Pillow
   numpy
   opencv-python-headless
   scipy
   rembg[cpu]
   huggingface_hub>=0.20.0
   ```
4. Klik **Commit changes**

### ❌ Error: `Can't find networks.lora_diffusers`
**Penyebab:** Folder `networks/` belum di-upload atau file `lora_diffusers.py` hilang.

**Solusi:** Lihat step 5.4 di atas — upload file `networks/lora_diffusers.py` ke Space.

### ❌ Error: `Repository Not Found` saat download LoRA
**Penyebab:** Penulisan repo ID salah, atau repo belum public.

**Solusi:**
1. Cek URL repo: buka `https://huggingface.co/johndoe/batik-joint-lora` di tab baru
2. Pastikan repo **Public** (bukan Private)
3. Salin persis username + nama repo ke field "HF Repo ID" (case-sensitive!)

### ❌ Error: `File not found in repo`
**Penyebab:** Nama file di field tidak sama dengan nama file di repo.

**Solusi:**
1. Buka URL repo LoRA di tab baru
2. Lihat persis nama file (case-sensitive, termasuk ekstensi `.safetensors`)
3. Salin ke field "Nama File .safetensors"

### ❌ Gambar yang di-generate flat / satu warna
**Penyebab:** VAE fp16-fix belum ter-load dengan benar.

**Solusi:**
1. Cek tab **Logs**, cari baris yang mengandung `vae`
2. Pastikan load VAE dari `madebyollin/sdxl-vae-fp16-fix` berhasil (tidak error 404)

### ❌ LoRA tidak nampak pengaruhnya
**Penyebab:**
- Trigger token salah
- LoRA scale terlalu rendah

**Solusi:**
1. Cek prompt di markdown hasil generate — pastikan ada trigger token (mis. `madurabatik jawa_baratbatik`)
2. Naikkan slider **Kekuatan LoRA** ke 1.0
3. Coba seed yang berbeda

### ❌ Space error: `Out of memory`
**Penyebab:** Kuota T4 small habis atau GPU memory tidak cukup untuk SDXL.

**Solusi:**
1. Coba turunkan **Langkah Inferensi** ke 15
2. Set hardware ke **T4 medium** atau **A10G small** (berbayar)
3. Tunggu 24 jam untuk reset kuota harian

### ❌ Hasil fusion bagus tapi simulasi baju error
**Penyebab:** Foto baju orang terlalu besar (>5 MB) atau background terlalu kompleks.

**Solusi:**
1. Upload foto yang lebih kecil (< 2 MB)
2. Pastikan orangnya terlihat jelas (tidak tertutup topi/kacamata besar)
3. Background polos lebih baik untuk deteksi rembg

---

## 🎉 Selesai!

Kalau semua step di atas sudah dijalankan, web app Anda sudah live dan bisa dipakai siapa saja lewat link:

```
https://huggingface.co/spaces/johndoe/batik-fusion-space
```

Untuk **ganti LoRA tanpa edit kode**:
1. Upload file `.safetensors` baru ke repo `johndoe/batik-joint-lora` lewat web HF
2. Di web app, ganti **Nama File .safetensors** ke nama file baru
3. Klik tombol lagi — tidak perlu rebuild Space 🚀

---

## 📌 Cheat Sheet — Info yang Perlu Disimpan

```
Username HF       : _________________________
HF Token          : hf_________________________
LoRA Repo URL     : https://huggingface.co/___/batik-joint-lora
LoRA Repo ID      : _________/batik-joint-lora
Nama file LoRA    : __________________________________________.safetensors
Space URL         : https://huggingface.co/spaces/___/batik-fusion-space
Space Hardware    : T4 small (gratis, ~2 jam/hari)
```

Semoga panduan ini membantu! Kalau ada step yang bingung atau error spesifik, kasih tahu detail error message + screenshot, nanti saya bantu debug. 🎨