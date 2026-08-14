# Panduan Menjalankan Batik Fusion SECARA LOKAL (di PC Sendiri)

> 🎯 **Target:** Menjalankan aplikasi Batik Fusion **100% offline** di PC Anda sendiri, tanpa upload ke mana pun. Bisa Gradio interaktif (perlu GPU) atau HTML showcase (tanpa GPU).
>
> ⏱️ **Estimasi waktu:** 5-15 menit (tergantung punya GPU atau tidak)
>
> 💡 **Ada 2 mode:** (1) Showcase statis (HTML) — tanpa GPU, (2) Gradio interaktif — perlu GPU/CPU kuat

---

## 📋 Pertanyaan Umum

### "Aku tidak punya GPU, bisa jalan lokal?"
**BISA!** Ada 2 opsi:
- **Mode Demo (HTML statis)** → Tidak perlu GPU sama sekali, generator sintetis otomatis. Cocok untuk demo/showcase.
- **Mode Interaktif (Gradio)** → Bisa jalan di CPU tapi sangat lambat (~2-5 menit per gambar). Tidak disarankan.

### "PC aku spek rendah, bisa apa?"
Pakai **Mode Demo (HTML statis)** saja. Anda tetap bisa:
- Melihat gallery semua fusion (gambar batik sintetis)
- Membaca narasi markdown penjelasan tiap fusion
- Mengubah-ubah isi HTML/CSS sesuai selera
- Upload ke mana pun (GitHub Pages, Netlify, Hugging Face Static Space)

### "Pakai GPU, mau coba yang interaktif (Gradio)?"
Pakai **Mode Interaktif (Gradio)** — install diffusers, torch, dan jalankan `python app.py`. Browser otomatis terbuka di `http://localhost:7860`.

---

## 🎯 DAFTAR ISI

1. [Persiapan: Install Python](#1-persiapan)
2. [Mode Demo: Showcase HTML Statis](#2-mode-demo)
3. [Mode Interaktif: Gradio (perlu GPU)](#3-mode-interaktif)
4. [Troubleshooting Lokal](#4-troubleshooting)
5. [Deployment ke Internet (opsional)](#5-deployment)

---

## 1. Persiapan: Install Python

### 1.1. Cek apakah Python sudah terinstall

Buka **PowerShell** atau **Command Prompt**, ketik:
```bash
python --version
```

**Kalau muncul** `Python 3.10.x` atau lebih baru → lanjut ke step 1.3.

**Kalau muncul** "Python was not found" → lanjut ke step 1.2.

### 1.2. Install Python (kalau belum ada)

1. Buka <https://www.python.org/downloads/>
2. Klik **"Download Python 3.12.x"** (versi stabil terbaru)
3. Jalankan installer
4. **PENTING:** Centang **"Add Python to PATH"** di layar pertama installer
5. Klik **"Install Now"**
6. Tunggu selesai, klik **"Close"**
7. **Restart PowerShell/Command Prompt**, ulangi step 1.1 untuk verifikasi

### 1.3. Buka Terminal di folder Batik_Re-Palette

1. Buka **File Explorer**, masuk ke folder `Batik_Re-Palette`
2. Klik kanan di area kosong → **"Open in Terminal"** (Windows 11)
   - Atau buka PowerShell, ketik: `cd "D:\Riset MBKM\model results\Batik_Re-Palette"`
3. Anda akan lihat prompt path folder Batik_Re-Palette

---

## 2. Mode Demo: Showcase HTML Statis (TANPA GPU)

> ⭐ **Rekomendasi untuk PC tanpa GPU / spek rendah.** Hanya butuh Python dasar, tidak perlu install library ML berat.

### 2.1. Install dependency minimal

```bash
pip install Pillow numpy
```

### 2.2. Generate showcase

```bash
python generate_showcase.py
python generate_index_html.py
```

**Apa yang terjadi:**
- `generate_showcase.py` membuat 4 gambar fusion (mode sintetis — gambar batik dummy yang menarik)
- `generate_index_html.py` membuat HTML gallery

**Waktu:** ~1-2 menit (mode sintetis sangat cepat, tanpa GPU).

### 2.3. Lihat hasilnya

1. Buka File Explorer → masuk ke folder `Batik_Re-Palette/showcase/`
2. **Double-click `index.html`** → otomatis terbuka di browser default
3. Anda akan lihat gallery dengan 4 fusion:
   - `madura_jawa_barat`
   - `madura_pola_kompleks_jawa_barat`
   - `madura_jawa_tengah`
   - `madura_yogyakarta`
4. Klik card → akan download/tampilkan narasi markdown

### 2.4. Edit HTML/CSS sesuai selera

Buka folder `showcase/` di VSCode:
- **`index.html`** — struktur HTML (header, gallery, footer)
- **`styles.css`** — warna, font, layout
- **`descriptions/*.md`** — narasi penjelasan tiap fusion
- **`images/*.png`** — gambar fusion (bisa diganti dengan gambar asli Anda)

**Misalnya:**
- Mau ganti judul? Edit `<h1>` di `index.html`
- Mau ganti warna? Edit `.fusion-card` di `styles.css`
- Mau tambah fusion? Tambah gambar baru di `images/` + entry baru di `metadata.json` → jalankan `generate_index_html.py` lagi

---

## 3. Mode Interaktif: Gradio (PERLU GPU)

> ⚠️ **PENTING:** Mode ini butuh GPU yang kuat (min 6GB VRAM untuk SDXL). Tanpa GPU, sangat lambat.

### 3.1. Install dependency lengkap (PENTING: pakai virtual environment!)

**Mengapa pakai venv?** Supaya library ML tidak bentrok dengan sistem Python.

```bash
# Buat virtual environment
python -m venv venv

# Aktifkan (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Kalau error ExecutionPolicy, jalankan ini dulu:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Aktifkan (Windows CMD)
venv\Scripts\activate.bat

# Aktifkan (Linux/macOS)
source venv/bin/activate
```

### 3.2. Install semua dependency

```bash
pip install -r requirements.txt
```

**Estimasi:** 5-15 menit (download torch, diffusers, rembg, dll. ~3-5 GB).

### 3.3. Download model SDXL + LoRA

**Otomatis dari Hugging Face (pakai internet):**
- SDXL base: otomatis di-download oleh `lora_generator.py` (~6 GB)
- VAE fp16-fix: otomatis (~300 MB)
- LoRA Anda: upload dulu ke Hugging Face Model Hub, lalu isi di UI

**Manual dari lokal (kalau sudah download):**
- Letakkan file SDXL di: `C:\Users\user\.cache\huggingface\hub\models--stabilityai--stable-diffusion-xl-base-1-0\snapshots\<hash>\`
- Letakkan LoRA di folder `Batik_Re-Palette/` (mis. `lora.safetensors`)

### 3.4. Jalankan aplikasi

```bash
python app.py
```

**Output di terminal:**
```
Running on local URL:  http://127.0.0.1:7860
Running on public URL: https://xxxxx.gradio.live  (opsional)
```

**Browser akan otomatis terbuka** ke `http://127.0.0.1:7860`. Kalau tidak, buka manual di Chrome/Edge/Firefox.

### 3.5. Pertama kali generate

1. Klik tab **"[FUSION] Cultural Fusion (2 Budaya)"**
2. Isi `Hugging Face Repo ID` (mis. `username/batik-joint-lora`) + nama file `.safetensors`
3. Klik **"[FUSION] Buat Template Fusion"**
4. **Tunggu 5-10 menit** untuk download SDXL + LoRA pertama kali
5. Setelah cached, generate berikutnya **~20-30 detik** per gambar

### 3.6. Akses dari device lain di jaringan lokal

Setelah `python app.py` jalan, aplikasi listen di `http://127.0.0.1:7860`.
Device lain di WiFi yang sama bisa akses lewat IP laptop Anda, mis.
`http://192.168.1.100:7860`.

Cara cek IP laptop:
```bash
# PowerShell
ipconfig
# Cari "IPv4 Address" di adapter WiFi
```

### 3.7. Matikan aplikasi

Di terminal, tekan **Ctrl+C** 2x.

---

## 4. Troubleshooting Lokal

### ❌ `python` not found
- Install Python dari <https://python.org/downloads/>
- **Pastikan centang "Add Python to PATH"** saat install
- Restart terminal

### ❌ `pip` not found
Coba pakai:
```bash
python -m pip install ...
```

### ❌ `Microsoft Visual C++ 14.0 or greater is required`
Install Build Tools:
1. Download dari <https://visualstudio.microsoft.com/visual-cpp-build-tools/>
2. Pilih **"Desktop development with C++"**
3. Install (butuh ~3 GB)

### ❌ `pip install torch` sangat lama / gagal
Ganti index URL:
```bash
pip install torch --index-url https://download.pytorch.org/whl/cu121
```
(ganti `cu121` dengan versi CUDA Anda; atau `cpu` untuk tanpa GPU)

### ❌ Gradio error `Address already in use`
Port 7860 sudah dipakai. Matikan proses lain atau ganti port:
```bash
python -c "import gradio as gr; print(gr.__version__)"
# Di app.py cari demo.launch(server_name="0.0.0.0", server_port=7861)
```

### ❌ `OutOfMemoryError` saat generate
- Turunkan slider **Kekuatan LoRA** ke 0.5
- Turunkan **Langkah Inferensi** ke 15
- Tutup aplikasi lain yang makan RAM/GPU

### ❌ Browser tidak otomatis terbuka
Manual buka <http://127.0.0.1:7860>

### ❌ `LoRA file not found`
- Pastikan nama file `.safetensors` benar (case-sensitive)
- Kalau pakai path lokal: gunakan forward slash atau double backslash
  ```python
  lora_path = "C:/Users/user/lora.safetensors"
  # atau
  lora_path = "C:\\Users\\user\\lora.safetensors"
  ```

### ❌ `Cannot connect to host 127.0.0.1`
- Aplikasi belum jalan / crash di startup
- Lihat error di terminal, fix dulu

---

## 5. Deployment ke Internet (Opsional, dari Lokal)

Setelah showcase jalan lokal, kalau mau share ke internet:

### 5.1. Cara paling cepat: LocalTunnel (pakai terminal)

```bash
# Install
npm install -g localtunnel

# Setelah python app.py jalan, buka terminal baru:
lt --port 7860
```

Output:
```
your url is: https://random-name-12345.loca.lt
```

Bagikan URL itu ke siapa pun — mereka bisa akses Gradio Anda lewat internet!

**Tanpa perlu akun, tanpa upload.**

### 5.2. Cara cepat: ngrok

1. Daftar di <https://ngrok.com/> (gratis)
2. Download & install
3. Jalankan:
   ```bash
   ngrok http 7860
   ```
4. Dapat URL publik, mis. `https://abc-123.ngrok-free.app`

### 5.3. Cara permanen: Deploy hasil lokal

Lihat `PANDUAN_STATIC.md` untuk opsi upload HTML statis gratis ke Hugging Face / GitHub Pages / Netlify.

---

## 🎉 Cheat Sheet Lokal

```bash
# ---- Setup sekali ----
cd "D:\Riset MBKM\model results\Batik_Re-Palette"
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# ---- Generate showcase HTML (tanpa GPU) ----
pip install Pillow numpy
python generate_showcase.py
python generate_index_html.py
# Buka: Batik_Re-Palette/showcase/index.html

# ---- Jalankan Gradio interaktif (perlu GPU) ----
python app.py
# Otomatis buka browser ke http://127.0.0.1:7860

# ---- Share ke internet ----
# Terminal baru (sambil app.py jalan):
lt --port 7860
# atau
ngrok http 7860
```

---

## ❓ FAQ

**Q: Python apa yang supported?**
A: Python 3.10 - 3.13 (tested dengan 3.12).

**Q: Bisa di Mac/Linux?**
A: Bisa! Sama, hanya beda syntax aktivasi venv (`source venv/bin/activate`).

**Q: RAM minimum?**
A: Mode demo: 4 GB cukup. Mode Gradio tanpa GPU: 16 GB. Mode Gradio + GPU: 8 GB system RAM + 6 GB VRAM.

**Q: Bisa dual boot dengan CUDA?**
A: Bisa, tapi setup CUDA di Windows ribet. Rekomendasi: pakai Linux (Ubuntu) atau WSL2 untuk pengalaman terbaik.

**Q: Bisa jalan di Raspberry Pi?**
A: Bisa untuk mode demo HTML showcase. Tidak untuk Gradio (perlu CPU kuat).

**Q: Bisa tanpa internet?**
A: Mode demo showcase: bisa. Mode Gradio interaktif: tidak (perlu download SDXL saat first run).