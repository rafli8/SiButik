# Panduan Membuat Video Demo untuk Aplikasi Batik Re-Palette

> 🎯 **Target:** Video demo profesional untuk presentasi lomba / portofolio / showcase ke publik.
>
> ⏱️ **Estimasi waktu:** 1-3 jam (termasuk editing)
>
> 🎬 **Durasi ideal:** 1-3 menit (untuk lomba), 3-5 menit (untuk portofolio)

---

## 📋 Kenapa Video Demo Penting?

| Jenis | Fungsi |
|---|---|
| **Video demo lomba** | Meyakinkan juri bahwa aplikasimu berjalan & inovatif |
| **Video portofolio** | Menunjukkan skill &成果 ke recruiter / publik |
| **Video tutorial** | Mengedukasi user cara pakai aplikasimu |
| **Video showcase** | Promosi di media sosial (YouTube, TikTok, Instagram) |

---

## 🎯 DAFTAR ISI

1. [Persiapan: Software & Equipment](#1-persiapan)
2. [Storyboard & Naskah](#2-storyboard)
3. [Rekam Layar dengan OBS Studio (GRATIS)](#3-obs-studio)
4. [Edit Video dengan CapCut / DaVinci Resolve](#4-edit-video)
5. [Voice Over & Musik Latar](#5-voice-over-musik)
6. [Export & Upload ke YouTube](#6-export-upload)
7. [Tips Profesional](#7-tips-profesional)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Persiapan

### 1.1. Software yang Dibutuhkan (Semua GRATIS)

| Software | Fungsi | Download |
|---|---|---|
| **OBS Studio** | Rekam layar + webcam | <https://obsproject.com> |
| **CapCut Desktop** | Edit video (termudah) | <https://capcut.com> |
| **DaVinci Resolve** | Edit video (pro, gratis) | <https://blackmagicdesign.com/products/davinciresolve> |
| **Audacity** | Rekam & edit suara | <https://audacityteam.org> |
| **ShareX** | Rekam layar alternatif | <https://getsharex.com> |
| **Canva** | Bikin thumbnail | <https://canva.com> |

### 1.2. Equipment (Opsional, Boleh Pakai yang Ada)

| Equipment | Alternatif Gratis |
|---|---|
| Kamera / webcam | Laptop webcam, HP (pakai DroidCam) |
| Mikrofon | Headset bawaan HP, earphone laptop |
| Lighting | Lampu meja, jendela (pagi/siang) |

### 1.3. Persiapan Aplikasi

1. **Pastikan Space sudah live** di `https://huggingface.co/spaces/USER/batik-fusion-space`
2. **Siapkan 2-3 skenario demo** (mis. fusion Madura × Jawa Barat, Madura × Bali)
3. **Pre-load gambar referensi** (download dulu, jangan pakai URL random)
4. **Siapkan foto orang** untuk fitur simulasi pakaian (resize < 2 MB)
5. **Bersihkan browser**:
   - Tutup tab lain (biar tidak terlihat di screen recording)
   - Disable notifikasi
   - Set zoom browser 100%

---

## 2. Storyboard & Naskah

### 2.1. Template Storyboard (1-3 Menit)

```
[0:00-0:10] INTRO — Logo + judul aplikasi
            "Batik Re-Palette: Cultural Fusion Generator"

[0:10-0:30] PROBLEM — Masalah yang dijawab
            Visual: Slide / narasi tentang hilangnya budaya lokal

[0:30-0:50] SOLUSI — Perkenalan aplikasi
            Visual: Screenshot UI Space
            Voice: "Aplikasi ini menggabungkan 2 motif batik..."

[0:50-1:30] DEMO — Live demo
            Visual: Rekam layar Space
            Voice: Step-by-step pakai aplikasi

[1:30-1:50] SIMULASI PAKAIAN — Baju virtual
            Visual: Upload foto → hasil simulasi

[1:50-2:00] HASIL & IMPACT — Tampak depan
            Visual: Gallery hasil fusion

[2:00-2:30] PENUTUP — Terima kasih + CTA
            "Coba sendiri: [link Space]"
```

### 2.2. Template Naskah Voice Over

```
🎙️ SCENE 1 (10 detik)
"Indonesia memiliki ratusan motif batik nusantara, 
namun banyak yang belum terekspos ke generasi muda."

🎙️ SCENE 2 (20 detik)
"Batik Re-Palette adalah aplikasi AI yang membantu desainer 
menggabungkan dua motif batik dari daerah berbeda, 
menghasilkan pola fusion yang harmonis dan modern."

🎙️ SCENE 3 (40 detik)
"Caranya mudah: pilih dua budaya, klik 'Buat Template Fusion',
dan AI akan generate pola batik baru lengkap dengan narasi
filosofi, warna, dan motif yang diambil dari masing-masing daerah."

🎙️ SCENE 4 (20 detik)
"Bahkan, Anda bisa langsung melihat hasil fusion dipakai
di baju — cocok untuk preview sebelum produksi massal."

🎙️ SCENE 5 (10 detik)
"Coba sendiri di [link Space]. Mari lestarikan budaya
dengan teknologi."
```

### 2.3. Tips Storyboard

- **5 detik pertama** menentukan apakah penonton lanjut nonton atau skip
- **Tunjukkan, jangan cuma jelaskan** — visual > narasi
- **Pacing cepat** — jaga节奏, jangan monoton
- **CTA di akhir** — arahkan ke link Space

---

## 3. OBS Studio — Rekam Layar + Webcam

### 3.1. Install OBS

1. Download dari <https://obsproject.com/download>
2. Install → buka OBS

### 3.2. Setup Scene untuk Demo

**Langkah-langkah:**

1. **Tambah Scene**: klik **"+"** di panel **Scenes** (kiri bawah), beri nama `Demo Screen`
2. **Tambah Sources** (panel bawah):
   - **Display Capture** (tangkap seluruh layar)
     - Klik **"+"** → **Display Capture** → OK → pilih monitor
   - **Webcam** (opsional, untuk PIP — Picture in Picture)
     - Klik **"+"** → **Video Capture Device** → pilih webcam
     - Resize kecil, taruh di pojok kanan bawah
   - **Window Capture** (alternatif — hanya窗口 browser)
     - Lebih ringan dari Display Capture
     - Klik **"+"** → **Window Capture** → pilih window browser

### 3.3. Setting Rekam (PENTING untuk Kualitas)

Klik **Settings** (kanan bawah) → **Output**:

| Setting | Rekomendasi | Keterangan |
|---|---|---|
| **Output Mode** | Advanced | Untuk kontrol penuh |
| **Recording Format** | MKV (untuk edit) → remux ke MP4 | MKB lebih stabil |
| **Encoder** | x264 (CPU) atau NVENC (GPU) | NVENC lebih ringan untuk GPU |
| **Rate Control** | CBR | Constant bitrate |
| **Bitrate** | 6000-10000 kbps | 1080p: 6000+ ; 4K: 15000+ |
| **Recording Path** | `D:\Videos\batik-demo\` | Folder khusus |
| **Recording Format** | mp4 (langsung) | Lebih simple |

**Settings → Video:**

| Setting | Rekomendasi |
|---|---|
| **Base Resolution** | 1920x1080 |
| **Output Resolution** | 1920x1080 |
| **FPS** | 30 (standar) atau 60 (untuk animasi) |

### 3.4. Mulai Rekam

1. Siapkan browser Space di ukuran窗口 tertentu
2. Klik **"Start Recording"** (kanan bawah)
3. **Lakukan demo** sesuai storyboard
4. Klik **"Stop Recording"** setelah selesai
5. File tersimpan di folder yang ditentukan

### 3.5. Tips Rekam yang Bagus

- **Matikan mic HP** (biar tidak ada notifikasi masuk)
- **Set Do Not Disturb** di Windows
- **Tutup aplikasi lain** (biar CPU fokus OBS)
- **Praktik dulu** sebelum rekam final
- **Jangan lupa pause sebentar** antar scene, biar mudah edit

---

## 4. Edit Video — CapCut (Termudah) atau DaVinci Resolve

### 4.1. Pakai CapCut Desktop (Recommended untuk Pemula)

**Langkah 1: Import**

1. Buka CapCut → **New Project**
2. Drag file rekaman OBS ke timeline

**Langkah 2: Edit Dasar**

- **Potong** bagian yang tidak perlu (klik split)
- **Trim** awal/akhir
- **Speed up** bagian lambat (1.5x atau 2x)
- **Slow motion** bagian penting (0.5x)

**Langkah 3: Tambah Elemen**

| Elemen | Cara di CapCut |
|---|---|
| **Text** | Tab "Text" → pilih style → masukkan narasi |
| **Musik latar** | Tab "Audio" → "Music" → pilih "Indie" / "Vlog" |
| **Transisi** | Antar clip → pilih "Fade" atau "Slide" |
| **Sticker / Icon** | Tab "Stickers" → cari "batik", "Indonesia" |
| **Zoom in** | Klik clip → "Keyframe" → ubah scale 110% di akhir |
| **Highlight** | Tambah rectangle + opacity rendah di area penting |

**Langkah 4: Color Grading**

- Klik clip → tab "Adjustment"
- Naikkan **Saturation** sedikit (5-10) untuk warna lebih hidup
- **Brightness** sesuai kebutuhan (jangan over-expose)
- Tambah **Sharpen** sedikit (5-15)

### 4.2. Pakai DaVinci Resolve (Pro, Gratis)

**Untuk hasil lebih profesional**, DaVinci Resolve punya:
- Color grading industry-grade
- Audio mixing
- Effects & transitions lengkap

Workflow:
1. **Media** → import file OBS
2. **Cut** → trim & potong cepat
3. **Edit** → tambah text, audio, transisi
4. **Color** → koreksi warna & grading
5. **Fairlight** → mixing audio
6. **Deliver** → export final

---

## 5. Voice Over & Musik Latar

### 5.1. Voice Over (Opsional, Tapi Sangat Disarankan)

**Opsi A: Rekam Sendiri**

1. Buka **Audacity**
2. Pilih mic input → rekam
3. **Edit**:
   - Noise Reduction (Effect → Noise Reduction)
   - Compressor (meratakan volume)
   - Normalize (volume konsisten)
4. **Export** WAV atau MP3
5. Import ke timeline video

**Tips rekam suara bagus:**
- Ruangan **sepi** (matikan AC/kipas)
- Mic **dekat mulut** (± 15 cm)
- Bicara **natural**, tidak terlalu cepat/lambat
- **Script sudah dihafal** atau ada teleprompter

**Opsi B: Pakai AI Voice (Gratis / Murah)**

| Tool | Bahasa Indonesia? | Harga |
|---|---|---|
| **ElevenLabs** | ✅ Bagus | Free 10 menit/bulan |
| **Narakeet** | ✅ | Berbayar |
| **Google TTS** | ✅ Standar | Free |
| **NaturalReader** | ✅ | Free terbatas |

**Opsi C: Tanpa Voice Over**

Gunakan **text overlay** + musik latar. Cocok untuk video pendek (30 detik - 1 menit).

### 5.2. Musik Latar (Royalty-Free, GRATIS)

| Sumber | Link |
|---|---|
| **YouTube Audio Library** | <https://studio.youtube.com/channel/music> |
| **Pixabay Music** | <https://pixabay.com/music> |
| **Uppbeat Free** | <https://uppbeat.io/free> |
| **Mixkit** | <https://mixkit.co/free-stock-music> |
| **Free Music Archive** | <https://freemusicarchive.org> |

**Rekomendasi mood untuk video demo:**
- **Inspiratif / corporate**: cari "inspiring", "corporate"
- **Tradisional / budaya**: cari "gamelan", "indonesian", "ethnic"
- **Modern / tech**: cari "electronic", "ambient"
- **Hangat / welcoming**: cari "acoustic", "folk"

**Volume musik:** 20-30% dari total (jangan sampai cover voice over)

---

## 6. Export & Upload ke YouTube

### 6.1. Export Setting di CapCut / DaVinci

| Setting | YouTube 1080p | YouTube 4K |
|---|---|---|
| **Resolution** | 1920x1080 | 3840x2160 |
| **FPS** | 30 | 30 atau 60 |
| **Codec** | H.264 | H.264 / H.265 |
| **Bitrate** | 8-12 Mbps | 35-45 Mbps |
| **Format** | MP4 | MP4 |
| **Audio** | AAC 192 kbps | AAC 256 kbps |

### 6.2. Upload ke YouTube

1. Buka <https://studio.youtube.com> → **Create** → **Upload videos**
2. Drag file video
3. Isi metadata:

**Judul (contoh):**
```
Batik Re-Palette: AI Cultural Fusion Generator | Demo Aplikasi MBKM
```

**Deskripsi:**
```
Batik Re-Palette adalah aplikasi web berbasis AI (Stable Diffusion XL + LoRA)
yang menghasilkan pola batik fusion dari 2 budaya Indonesia berbeda.

🎨 Fitur:
- Generate motif batik fusion 2 daerah
- Narasi filosofi otomatis
- Simulasi pakaian (virtual try-on)
- 100% gratis, tanpa install

🔗 Coba sendiri:
https://huggingface.co/spaces/USER/batik-fusion-space

📚 Riset MBKM 2024 — [Nama Kampus]
👥 Tim: [Nama Anggota]
🏷️ #batik #AI #budaya #diffusion #MBKM
```

**Tags:**
```
batik, batik AI, batik fusion, stable diffusion, LoRA, budaya Indonesia,
MBKM, riset, AI generative, SDXL
```

**Thumbnail** (PENTING untuk klik!):
- Ukuran: 1280x720 px
- Pakai **Canva** → buat thumbnail dengan:
  - Background gelap dengan elemen batik
  - Teks besar: "AI Batik Fusion"
  - Subtitle: "2 Budaya dalam 1 Pola"
  - Logo / foto aplikasi
  - Wajah (opsional, meningkatkan CTR)

### 6.3. Publish Setting

- **Visibility**: Public / Unlisted (jika hanya untuk lomba)
- **License**: Standard YouTube License
- **Category**: Science & Technology / Education
- **Language**: Indonesian

---

## 7. Tips Profesional

### 7.1. Biar Tampilan Makin Keren

- **Cursor highlight**: gunakan plugin OBS atau setting manual agar cursor lebih jelas
- **Mouse smooth**: pakai Ease Cursor (CapCut plugin)
- **Zoom in** saat klik tombol penting → arahkan perhatian
- **Lower third**: tambah nama presenter / judul di pojok bawah
- **Before-After**: split screen perbandingan motif asli vs fusion
- **Animasi transisi**: jangan terlalu banyak, max 2-3 jenis

### 7.2. Biar Audio Jernih

- Rekam voice over di **ruangan tenang**
- Pakai **pop filter** (bisa DIY dari stocking + hanger)
- Tambah **soft music** sebagai latar
- **EQ**: turunkan bass 100Hz sedikit, naikkan treble 3-5kHz

### 7.3. Storytelling yang Kuat

- **Hook 5 detik pertama**: pertanyaan, fakta mengejutkan, atau visual menarik
- **Show, don't tell**: tampilkan UI, bukan cuma ceritakan
- **Highlight impact**: berapa budaya yang sudah dilestarikan, berapa user
- **CTA jelas**: "Coba sendiri di [link]"

### 7.4. Optimasi untuk Lomba

| Aspek | Tips |
|---|---|
| **Durasi** | 1-3 menit (maksimal 5 menit) |
| **Kualitas** | Minimal 1080p, audio jelas |
| **Storyline** | Problem → Solusi → Demo → Impact |
| **Originalitas** | Highlight keunikan fitur fusion + narasi |
| **Dampak** | Tunjukkan potensi untuk UMKM / edukasi |

---

## 8. Troubleshooting

### ❌ OBS Lag Saat Rekam
**Solusi:**
- Turunkan **Output Resolution** ke 1280x720 dulu
- Pakai **NVENC encoder** (jika GPU NVIDIA)
- Tutup aplikasi lain (Chrome, Discord, dll.)
- Update driver GPU

### ❌ Suara Voice Over Pecah / Noise
**Solusi:**
- Mic terlalu dekat → mundur 15-20 cm
- Mic terlalu kecil gain → naikkan gain, jangan volume clip
- Ada suara AC/kipas → matikan atau pindah ruangan
- Pakai Audacity → Noise Reduction

### ❌ Video Hasil Edit Terpotong di YouTube
**Solusi:**
- Pakai **MP4 H.264** (codec universal)
- Bitrate tidak lebih dari 50 Mbps untuk upload
- Durasi upload pertama butuh proses (bisa 1-4 jam untuk 4K)

### ❌ Musik Latar Terdengar Cover Voice Over
**Solusi:**
- Turunkan volume musik ke **-15 dB** saat ada voice
- Pakai **ducking** otomatis (CapCut Pro)
- Edit manual: split clip musik → turunkan volume di bagian voice over

### ❌ Browser Lemot Saat Rekam Live Demo
**Solusi:**
- Tutup tab lain
- Disable extension yang tidak perlu (ad blocker, dll.)
- Rekam di **CPU basic Space** (lebih ringan dari T4 untuk live)
- Pakai **Window Capture** bukan Display Capture (lebih ringan)

### ❌ Thumbnail Tidak Menarik
**Solusi:**
- Pakai **warna kontras** (background gelap + teks terang)
- **Maks 5 kata** di thumbnail
- Tambah **foto wajah** (kalau berani)
- Test A/B: buat 3 thumbnail, upload, lihat CTR terbaik

---

## 🎬 Contoh Script OBS untuk Reference

```python
# OBS Python script (Tools → Scripts → + → paste ini)
# Auto-start/stop recording dengan hotkey

import obspython as obs

def script_description():
    return """Auto record demo with hotkey."""

def script_load(settings):
    obs.obs_hotkey_register_frontend("start_record", "Start Recording")
    obs.obs_hotkey_register_frontend("stop_record", "Stop Recording")

def start_record(pressed):
    if pressed:
        obs.obs_frontend_recording_start()

def stop_record(pressed):
    if pressed:
        obs.obs_frontend_recording_stop()
```

---

## 🎉 Checklist Sebelum Upload

- [ ] Video berdurasi 1-3 menit
- [ ] Resolusi minimal 1080p
- [ ] Audio jernih (volume konsisten)
- [ ] Voice over natural (tidak terlalu cepat)
- [ ] Musik latar tidak cover voice over
- [ ] Teks tidak typo / bahasa konsisten
- [ ] Thumbnail menarik dengan judul jelas
- [ ] CTA + link Space ada di deskripsi
- [ ] Tags relevan (batik, AI, budaya, dll.)
- [ ] Upload sebagai Public / Unlisted

---

## 📌 Tools Rekomendasi Cepat

| Kebutuhan | Tool | Harga |
|---|---|---|
| Rekam layar | **OBS Studio** | Gratis |
| Edit video (pemula) | **CapCut Desktop** | Gratis |
| Edit video (pro) | **DaVinci Resolve** | Gratis |
| Voice over AI | **ElevenLabs** | Free 10 menit/bln |
| Musik latar | **Pixabay Music** | Gratis |
| Thumbnail | **Canva** | Gratis |
| Upload | **YouTube** | Gratis |

---

Semoga panduan ini membantu! Kalau ada step yang bingung atau perlu detail lebih lanjut (mis. tutorial OBS lebih detail, atau color grading di DaVinci), kasih tahu — nanti saya bantu. 🎬🎨