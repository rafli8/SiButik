# -*- coding: utf-8 -*-
"""
app.py - Aplikasi Pewarnaan Ulang Batik
Tab:
  1. Dari Gambar Referensi
  2. Pilih Warna Manual Dinamis
  3. Cultural Fusion (2 Budaya) -> fitur baru
"""

import gradio as gr
from PIL import Image
import numpy as np
import cv2
import json
from scipy.spatial import distance_matrix as cdist
from scipy.optimize import linear_sum_assignment
from pathlib import Path

try:
    from rembg import remove as rembg_remove
    from rembg import new_session
    REMBG_TERSEDIA = True
except ImportError:
    REMBG_TERSEDIA = False

_session_kain = None

def get_session_kain():
    global _session_kain
    if _session_kain is None and REMBG_TERSEDIA:
        _session_kain = new_session("u2net_cloth_seg")
    return _session_kain



# parameter default
UKURAN_KERJA = 512
JUMLAH_WARNA_REFERENSI = 256
KOLOM_KAIN_DEFAULT = 4
BARIS_KAIN_DEFAULT = 6


# state sesi
_gambar_batik = None


# fungsi inti

def _ke_rgb(gambar_pil, ukuran=UKURAN_KERJA):
    return np.array(gambar_pil.convert("RGB").resize((ukuran, ukuran), Image.LANCZOS))


def _kuantisasi(rgb, n):
    """Kuantisasi gambar ke N warna dominan."""
    pil = Image.fromarray(rgb)
    q   = pil.convert("P", palette=Image.ADAPTIVE, colors=n)
    palet = np.array(q.getpalette()[:3 * n], dtype=np.float32).reshape(n, 3)
    indeks = np.array(q, dtype=np.int32)
    return indeks, palet


def _terapkan_palet(indeks, palet_baru):
    """Terapkan palet warna baru ke gambar terindeks."""
    T, L = indeks.shape
    hasil = np.zeros((T, L, 3), dtype=np.uint8)
    for i, warna in enumerate(palet_baru):
        hasil[indeks == i] = np.clip(warna, 0, 255).astype(np.uint8)
    return hasil


def _cocokkan_warna_lab(palet_sumber, palet_target):
    """Cocokkan warna secara optimal di ruang warna LAB"""
    def ke_lab(p):
        u8  = np.clip(p, 0, 255).astype(np.uint8).reshape(1, -1, 3)
        return cv2.cvtColor(u8, cv2.COLOR_RGB2Lab).reshape(-1, 3).astype(np.float32)
    jarak = cdist(ke_lab(palet_sumber), ke_lab(palet_target))
    baris, kolom = linear_sum_assignment(jarak)
    palet_baru = np.zeros_like(palet_sumber)
    for b, k in zip(baris, kolom):
        palet_baru[b] = palet_target[k]
    return palet_baru


def _buat_strip_warna(palet, lebar_kotak=50, tinggi=55):
    """Buat gambar strip kotak-kotak warna dari palet."""
    n = len(palet)
    gambar = np.zeros((tinggi, n * lebar_kotak, 3), dtype=np.uint8)
    for i, warna in enumerate(palet):
        gambar[:, i*lebar_kotak:(i+1)*lebar_kotak] = np.clip(warna, 0, 255).astype(np.uint8)
    return Image.fromarray(gambar)


def _hex_ke_rgb(kode_hex):
    h = kode_hex.strip().lstrip("#")
    return [int(h[i:i+2], 16) for i in (0, 2, 4)]


def _buat_ubin_natural(arr_rgb, target_T, target_L):
    """
    Membuat ubin tekstur (tiling) dengan teknik Feathered Seams (alpha blending) + Half-Drop.
    arr_rgb: numpy array [H, W, 3] gambar batik 1 tile
    target_T, target_L: ukuran akhir kanvas yang dibutuhkan
    """
    tB, lB = arr_rgb.shape[:2]
    
    # Overlap 15% untuk gradasi peleburan halus pada tiap sambungan
    overlap_x = int(lB * 0.15)
    overlap_y = int(tB * 0.15)
    
    step_x = lB - overlap_x
    step_y = tB - overlap_y
    
    if step_x <= 0 or step_y <= 0:
        return np.zeros((target_T, target_L, 3), dtype=np.uint8)
        
    kolom = (target_L // step_x) + 3
    baris = (target_T // step_y) + 3
    
    # KANVAS LEBIH LEBAR: Tambah pad_kiri untuk mencegah kotak hitam di tepi kiri saat digeser
    pad_kiri = step_x 
    
    canvas_w = int(lB + (kolom - 1) * step_x + step_x * 0.5) + pad_kiri
    canvas_h = int(tB + (baris - 1) * step_y)
    
    canvas = np.zeros((canvas_h, canvas_w, 3), dtype=np.float32)
    weight_map = np.zeros((canvas_h, canvas_w, 3), dtype=np.float32)
    
    # Mask gradient 1D (feathering/transparansi pada tepi)
    grad_x = np.ones(lB, dtype=np.float32)
    if overlap_x > 0:
        grad_x[:overlap_x] = np.linspace(0, 1, overlap_x)
        grad_x[-overlap_x:] = np.linspace(1, 0, overlap_x)
        
    grad_y = np.ones(tB, dtype=np.float32)
    if overlap_y > 0:
        grad_y[:overlap_y] = np.linspace(0, 1, overlap_y)
        grad_y[-overlap_y:] = np.linspace(1, 0, overlap_y)
        
    mask_2d = np.outer(grad_y, grad_x)
    mask_3d = np.dstack([mask_2d]*3)
    arr_float = arr_rgb.astype(np.float32)
    
    for b in range(baris):
        # Mulai k dari -1 untuk menutupi ruang kosong akibat offset ke kanan
        for k in range(-1, kolom):
            # Pola Half-Drop : geser baris ganjil ke kanan sejauh 50%
            offset_x = int(step_x * 0.5) if (b % 2 == 1) else 0
            
            x_start = k * step_x + offset_x + pad_kiri
            y_start = b * step_y
            x_end = x_start + lB
            y_end = y_start + tB
            
            if x_start >= 0 and x_end <= canvas_w and y_start >= 0 and y_end <= canvas_h:
                canvas[y_start:y_end, x_start:x_end] += arr_float * mask_3d
                weight_map[y_start:y_end, x_start:x_end] += mask_3d
                
    weight_map[weight_map == 0] = 1.0
    canvas = canvas / weight_map
    
    # Potong area transparan di tepi luar dan potong offset ekstra di kiri
    crop_y1 = overlap_y
    crop_x1 = overlap_x + pad_kiri
    
    hasil = np.clip(canvas[crop_y1:crop_y1+target_T, crop_x1:crop_x1+target_L], 0, 255).astype(np.uint8)
    
    if hasil.shape[0] < target_T or hasil.shape[1] < target_L:
        pad_t = max(0, target_T - hasil.shape[0])
        pad_l = max(0, target_L - hasil.shape[1])
        hasil = np.pad(hasil, ((0, pad_t), (0, pad_l), (0, 0)), mode='reflect')
        
    return hasil


def _buat_kain(gambar, kolom, baris):
    """Ubin gambar dengan teknik Feathered Seams + Half-Drop"""
    if gambar is None:
        return None
    arr  = gambar if isinstance(gambar, np.ndarray) else np.array(gambar.convert("RGB"))
    kolom = max(1, int(kolom))
    baris = max(1, int(baris))
    
    tB, lB = arr.shape[:2]
    step_x = lB - int(lB * 0.15)
    step_y = tB - int(tB * 0.15)
    
    target_L = step_x * kolom
    target_T = step_y * baris
    
    hasil = _buat_ubin_natural(arr, target_T, target_L)
    return Image.fromarray(hasil)


# deteksi area pakaian

def _segmentasi_baju_atas(pil_img):
    """
    Gunakan rembg (u2net_cloth_seg) untuk memisahkan area pakaian atas.
    Model menghasilkan output RGBA berukuran 3x tinggi gambar input
    (3 segmen vertikal: Upper, Lower, Full ditumpuk).
    Return: masker alpha uint8 [H,W] sama dengan ukuran pil_img.
    """
    H_asli = pil_img.height
    W_asli = pil_img.width

    session = get_session_kain()
    if session is not None:
        hasil_rgba = rembg_remove(pil_img, session=session)
    else:
        hasil_rgba = rembg_remove(pil_img)

    alpha_full = np.array(hasil_rgba)[:, :, 3]
    H_out = alpha_full.shape[0]

    # u2net_cloth_seg menumpuk 3 segmen secara vertikal:
    # [0        .. H_asli-1] = Upper body
    # [H_asli   .. 2*H_asli-1] = Lower body
    # [2*H_asli .. 3*H_asli-1] = Full body
    # Kita ambil gabungan Upper + Full body dan buang Lower
    if H_out >= 2 * H_asli:
        alpha_upper = alpha_full[:H_asli, :]
        if H_out >= 3 * H_asli:
            alpha_full_body = alpha_full[2*H_asli:3*H_asli, :]
            # Gabungkan: pakai Upper, tapi juga tambahkan Full body untuk gamis/jubah
            alpha = np.maximum(alpha_upper, alpha_full_body)
        else:
            alpha = alpha_upper
    else:
        alpha = alpha_full

    # Resize ke ukuran foto asli jika masih beda
    if alpha.shape != (H_asli, W_asli):
        alpha = cv2.resize(alpha, (W_asli, H_asli), interpolation=cv2.INTER_LINEAR)

    _, biner = cv2.threshold(alpha, 10, 255, cv2.THRESH_BINARY)
    kernel   = np.ones((5, 5), np.uint8)
    biner    = cv2.morphologyEx(biner, cv2.MORPH_CLOSE, kernel, iterations=2)

    # Hapus komponen kecil yang bukan pakaian atas (misal celana yang ikut terdeteksi)
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(biner, connectivity=8)
    masker_final = np.zeros_like(biner)
    for label_id in range(1, num_labels):
        y_top = stats[label_id, cv2.CC_STAT_TOP]
        area  = stats[label_id, cv2.CC_STAT_AREA]
        if area > (H_asli * W_asli * 0.005) and y_top < (H_asli * 0.65):
            masker_final[labels == label_id] = 255

    return masker_final



def tempel_batik_ke_baju(foto_orang, gambar_batik, intensitas, ukuran_motif=0.4):
    """
    Tempelkan motif batik ke area pakaian menggunakan Displacement Mapping.
    
    1. Masking: rembg + filter kulit
    2. Ekstrak Shading: Konversi baju ke grayscale, blur bilateral
    3. Tiling & Skala: Ubin motif batik
    4. Warping: Bengkokkan ubin mengikuti lekukan/gradien shading baju
    5. Blending: Kalikan motif yang sudah bengkok dengan shading baju
    """
    if foto_orang is None or gambar_batik is None:
        return None, "(Error) Upload foto orang dan gambar batik terlebih dahulu."

    def ke_numpy_rgb(img):
        if isinstance(img, np.ndarray):
            return img[:, :, :3].astype(np.uint8) if img.ndim == 3 else img
        return np.array(img.convert("RGB"))

    # Pastikan foto dalam PIL untuk rembg
    if isinstance(foto_orang, np.ndarray):
        foto_pil = Image.fromarray(foto_orang[:, :, :3].astype(np.uint8))
    else:
        foto_pil = foto_orang.convert("RGB")

    orang_rgb = np.array(foto_pil)
    T, L      = orang_rgb.shape[:2]
    orang_bgr = cv2.cvtColor(orang_rgb, cv2.COLOR_RGB2BGR)

    # 1. Masking Area Pakaian 
    if REMBG_TERSEDIA:
        masker_baju_keras = _segmentasi_baju_atas(foto_pil)
        # Pastikan masker memiliki ukuran yang sama dengan foto asli
        if masker_baju_keras.shape[:2] != (T, L):
            masker_baju_keras = cv2.resize(masker_baju_keras, (L, T), interpolation=cv2.INTER_NEAREST)
    else:
        masker_baju_keras = np.ones((T, L), dtype=np.uint8) * 255

    # Menutup lubang kecil di dalam baju
    kernel_close = np.ones((9, 9), np.uint8)
    masker_baju_keras = cv2.morphologyEx(masker_baju_keras, cv2.MORPH_CLOSE, kernel_close, iterations=2)
    
    # Sedikit melebarkan (dilate) masker agar batik menyentuh batas luar tepi baju
    kernel_dilate = np.ones((3, 3), np.uint8)
    masker_baju_keras = cv2.dilate(masker_baju_keras, kernel_dilate, iterations=1)
    
    # Menghaluskan tepi (anti-aliasing ringan)
    masker_baju_halus = cv2.GaussianBlur(masker_baju_keras, (5, 5), 0).astype(np.float32) / 255.0


    # 2. Ekstrak Shading (Pencahayaan & Lipatan)
    gray_u8 = cv2.cvtColor(orang_bgr, cv2.COLOR_BGR2GRAY)
    # Gunakan Gaussian Blur kuat untuk menghapus semua noise/tekstur asli baju, 
    gray_smooth = cv2.GaussianBlur(gray_u8, (21, 21), 0)
    gray_float = gray_smooth.astype(np.float32) / 255.0

    mask_bool = masker_baju_keras > 0
    if not np.any(mask_bool):
        return foto_orang, "(Error) Tidak ada area pakaian yang terdeteksi."

    # Normalisasi kecerahan agar baju gelap tidak membuat motif jadi hitam
    median_val = np.median(gray_float[mask_bool])
    median_val = max(median_val, 0.05)
    # Normalisasikan supaya rata-rata kecerahan baju menjadi 0.85 (cerah alami)
    shading = (gray_float / median_val) * 0.85
    # Clip rentang bayangan gelap (0.1) hingga terang (1.4)
    shading = np.clip(shading, 0.1, 1.4)

    # 3. Skala & Ubin Batik
    batik_rgb = ke_numpy_rgb(gambar_batik)
    coords = np.where(masker_baju_keras > 0)
    lebar_baju = int(coords[1].max() - coords[1].min())
    target_w = max(150, int(lebar_baju * float(ukuran_motif)))
    target_h = max(150, int(batik_rgb.shape[0] * target_w / max(batik_rgb.shape[1], 1)))
    batik_scaled = cv2.resize(batik_rgb, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4)

    tB, lB = batik_scaled.shape[:2]
    # Menyusun ubin batik secara menyatu/alami menggunakan Feathered Half-Drop
    batik_ubin = _buat_ubin_natural(batik_scaled, T, L)

    # 4. Warping (Displacement Mapping)
    # Menggunakan metode Intensity Displacement
    gray_for_displace = cv2.GaussianBlur(gray_u8, (21, 21), 0).astype(np.float32) / 255.0
    
    # 0.5 adalah nilai netral (tidak bergeser)
    displacement = (gray_for_displace - 0.5) * 35.0
    
    h, w = T, L
    X, Y = np.meshgrid(np.arange(w), np.arange(h))
    
    # Geser sumbu X dan Y berdasarkan lipatan bayangan kain
    map_x = (X + displacement).astype(np.float32)
    map_y = (Y + displacement).astype(np.float32)
    
    batik_warped = cv2.remap(batik_ubin, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

    # 5. Blending (Multiply Shading)
    # Kalikan motif batik dengan shading baju asli
    batik_shaded = np.clip(batik_warped.astype(np.float32) * shading[..., None], 0, 255)

    # 6. Tempelkan ke foto asli
    alpha = masker_baju_halus[..., None] * float(intensitas)
    hasil = orang_rgb.astype(np.float32) * (1.0 - alpha) + batik_shaded * alpha
    hasil_final = np.clip(hasil, 0, 255).astype(np.uint8)

    return Image.fromarray(hasil_final), "Selesai! Foto menggunakan hasil batik dengan warna yang telah di sesuaikan"



# Fungsi Tab 1: Dari Referensi

def proses_dari_referensi(batik_pil, referensi_pil):
    global _gambar_batik
    if batik_pil is None or referensi_pil is None:
        return None
    _gambar_batik = _ke_rgb(batik_pil)
    referensi_rgb = _ke_rgb(referensi_pil)
    indeks, palet_sumber = _kuantisasi(_gambar_batik, JUMLAH_WARNA_REFERENSI)
    _, palet_target      = _kuantisasi(referensi_rgb,  JUMLAH_WARNA_REFERENSI)
    palet_cocok = _cocokkan_warna_lab(palet_sumber, palet_target)
    return Image.fromarray(_terapkan_palet(indeks, palet_cocok))


# Fungsi Tab 2: Pilih 6 Warna Manual

def ekstrak_warna_dinamis(batik_pil):
    """Ekstrak warna dominan secara otomatis (standar 6 warna)."""
    global _gambar_batik
    jumlah_warna = 6
    if batik_pil is None:
        return None, ["#ffffff"] * jumlah_warna
    _gambar_batik = _ke_rgb(batik_pil)
    _, palet = _kuantisasi(_gambar_batik, jumlah_warna)
    strip = _buat_strip_warna(palet)
    kode_hex = [
        "#{:02x}{:02x}{:02x}".format(*np.clip(c, 0, 255).astype(int))
        for c in palet
    ]
    return strip, kode_hex


def terapkan_warna_dinamis(batik_pil, daftar_hex):
    """Terapkan palet kustom menggunakan pemetaan jarak terdekat di ruang LAB."""
    global _gambar_batik
    if batik_pil is None or not daftar_hex:
        return None
        
    _gambar_batik = _ke_rgb(batik_pil)
    
    palet_rgb = []
    for h in daftar_hex:
        try:
            palet_rgb.append(_hex_ke_rgb(h))
        except Exception:
            pass
            
    if not palet_rgb:
        return Image.fromarray(_gambar_batik)
        
    palet_rgb = np.array(palet_rgb, dtype=np.uint8)
    
    img_lab = cv2.cvtColor(_gambar_batik, cv2.COLOR_RGB2LAB).astype(np.float32)
    palet_lab = cv2.cvtColor(palet_rgb.reshape(1, -1, 3), cv2.COLOR_RGB2LAB).reshape(-1, 3).astype(np.float32)
    
    flat_img = img_lab.reshape(-1, 3)
    jarak = cdist(flat_img, palet_lab)
    
    idx_terdekat = np.argmin(jarak, axis=1)
    hasil_flat = palet_rgb[idx_terdekat]
    hasil = hasil_flat.reshape(_gambar_batik.shape[0], _gambar_batik.shape[1], 3).astype(np.uint8)
    
    return Image.fromarray(hasil)


# Antarmuka Pengguna

from fusion_engine import (
    buat_template_fusion, template_ke_markdown, BUDAYA_DB, ALL_REGIONS_TRAINING,
)

# Showcase: loader untuk metadata.json + gambar fusion pra-generate
SHOWCASE_DIR = Path(__file__).resolve().parent / "showcase"
SHOWCASE_META = SHOWCASE_DIR / "metadata.json"

def _muat_showcase():
    """Load metadata showcase (gambar fusion + prompt/trigger)."""
    if not SHOWCASE_META.exists():
        return [], []
    try:
        with open(SHOWCASE_META, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return [], []
    entries = data.get("entries", [])
    items = []      # untuk gr.Gallery: list (image_path, caption)
    payload = []    # list parallel berisi dict metadata asli
    for e in entries:
        rel_img = e.get("image", "")
        img_path = (SHOWCASE_DIR / rel_img).resolve()
        if not img_path.exists():
            continue
        caption = e.get("judul", "Fusion")
        items.append((str(img_path), caption))
        payload.append({
            "judul":    e.get("judul", ""),
            "trigger_1": e.get("trigger_1", ""),
            "trigger_2": e.get("trigger_2", ""),
            "prompt":   e.get("prompt", ""),
            "image":    str(img_path),
            "id":       e.get("id", ""),
        })
    return items, payload

_SHOWCASE_ITEMS, _SHOWCASE_PAYLOAD = _muat_showcase()

# --- Loader narasi filosofi dari fusion_descriptions.json (di-indeks per nama file)
_FUSION_DESC_PATH = Path(__file__).resolve().parent / "fusion_descriptions.json"
_FUSION_DESC_BY_IMAGE: dict = {}


def _muat_fusion_descriptions():
    """Bangun peta narasi filosofi (filosofi_fusion) per nama file gambar."""
    global _FUSION_DESC_BY_IMAGE
    _FUSION_DESC_BY_IMAGE = {}
    if not _FUSION_DESC_PATH.exists():
        return
    try:
        with open(_FUSION_DESC_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        for e in data.get("fusions", []):
            img = e.get("image", "")
            if img:
                _FUSION_DESC_BY_IMAGE[Path(img).name] = e
    except Exception:
        pass


_muat_fusion_descriptions()


def _pilih_template_dari_showcase(idx):
    """Muat template ke-`idx` dari showcase: gambar + narasi + prompt."""
    if idx is None or not _SHOWCASE_PAYLOAD:
        return None, "*Belum ada template fusion yang dipilih.*", None
    try:
        i = int(idx)
    except Exception:
        return None, "*Index template tidak valid.*", None
    if i < 0 or i >= len(_SHOWCASE_PAYLOAD):
        return None, "*Index template di luar jangkauan.*", None
    p = _SHOWCASE_PAYLOAD[i]
    img_path = Path(p["image"])
    img = Image.open(img_path).convert("RGB") if img_path.exists() else None
    fname = img_path.name
    desc = _FUSION_DESC_BY_IMAGE.get(fname, {})
    judul    = p.get("judul", "")
    trigger1 = p.get("trigger_1", "")
    trigger2 = p.get("trigger_2", "")
    prompt   = p.get("prompt", "")
    narrative = desc.get("filosofi_fusion") or "*Narasi belum tersedia untuk template ini.*"
    md = (
        f"### {judul}\n\n"
        f"**Trigger token:** `{trigger1}` + `{trigger2}`\n\n"
        f"**Narasi filosofi fusion:**\n\n{narrative}\n\n"
        f"**Prompt SDXL:**\n```\n{prompt}\n```"
    )
    return img, md, img


def bangun_antarmuka():
    css = """
    .judul-utama { text-align: center; padding: 20px 0 10px; }
    .judul-utama h1 { font-size: 2rem; color: #5D4037; }
    .judul-utama p  { color: #795548; font-size: 0.95rem; }
    .label-seksi { font-weight: 700; color: #4E342E; margin-top: 12px; }
    .fusion-card {
        background: linear-gradient(135deg, #fff7ed 0%, #fef3c7 100%);
        border: 1px solid #fbbf24;
        border-radius: 14px;
        padding: 14px;
    }
    .fusion-card h3 { color: #92400e; margin-top: 0; }
    .corner-cloth {
        background: #1f2937;
        color: #fff;
        border-radius: 14px;
        padding: 12px;
        border: 2px dashed #fbbf24;
    }
    .showcase-section {
        background: linear-gradient(135deg, #221d18 0%, #2c2620 100%);
        border: 1px solid #423b35;
        border-radius: 14px;
        padding: 14px 16px;
        margin-bottom: 14px;
    }
    .showcase-section h3 { color: #ffd6a5 !important; margin-top: 0 !important; }
    .showcase-section p  { color: #d9cbb5; }
    .showcase-badge {
        background: rgba(244,162,97,0.15);
        color: #ffd6a5;
        padding: 2px 10px;
        border-radius: 999px;
        font-size: 0.78rem;
        border: 1px solid rgba(244,162,97,0.3);
    }
    footer { display: none !important; }
    """

    with gr.Blocks(title="SiButik: Silang Budaya Batik") as aplikasi:

        gr.HTML("""
        <div class="judul-utama">
            <h1>SiButik: Silang Budaya Batik Nusantara</h1>
            <p>Generator <b>Cultural Fusion Batik</b> — gabungkan dua tradisi batik daerah menjadi satu kain fusion menggunakan SDXL + LoRA Joint Training.</p>
        </div>
        """)

        # ---------- SECTION: SHOWCASE TEMPLATE PICKER ----------
        with gr.Group(elem_classes="showcase-section"):
            gr.Markdown("### 🎨 Pilih dari Showcase Template")
            gr.Markdown(
                f"<span class='showcase-badge'>{len(_SHOWCASE_PAYLOAD)} template fusion siap-pakai</span> "
                "&nbsp;Klik salah satu kartu di gallery untuk memuatnya ke panel tengah. "
                "Narasi filosofi + prompt SDXL akan otomatis tampil."
            )
            showcase_gallery = gr.Gallery(
                value=_SHOWCASE_ITEMS,
                columns=5,
                rows=2,
                height=240,
                object_fit="cover",
                show_label=False,
                allow_preview=True,
            )
            showcase_info = gr.Markdown(value="*Belum ada template dipilih.*")

        # ---------- SECTION: INTRO FUSION ----------
            gr.Markdown(
                "### Fusion Dua Budaya Menjadi Satu Kain Batik\n"
                "Pilih atau ketik dua daerah budaya, tambahkan deskripsi spesifik, "
                "lalu aplikasi akan menggabungkan keduanya menjadi **template fusion** "
                "(gambar + narasi). Hasil fusion kemudian bisa disimulasikan sebagai "
                "pakaian di pojok kanan."
            )

            # Daftar pilihan budaya dari knowledge base
            pilihan_budaya = list(BUDAYA_DB.keys()) + ["(Lainnya / ketik sendiri)"]

            with gr.Row():
                # ---------- KOLOM KIRI: INPUT 2 BUDAYA + TEMA ----------
                with gr.Column(scale=2, elem_classes="fusion-card"):
                    gr.Markdown("#### Masukkan Dua Budaya")
                    with gr.Row():
                        dropdown_1 = gr.Dropdown(
                            choices=pilihan_budaya,
                            value="madura",
                            label="Budaya 1 (pilihan cepat)",
                        )
                        nama_1 = gr.Textbox(
                            label="Atau ketik nama Budaya 1",
                            placeholder="mis. Madura, Jawa, Batak, dll.",
                        )
                    prompt_1 = gr.Textbox(
                        label="Prompt tambahan Budaya 1",
                        placeholder="mis. warna merah tua, motif mata rantai, tegas",
                        lines=2,
                    )

                    with gr.Row():
                        dropdown_2 = gr.Dropdown(
                            choices=pilihan_budaya,
                            value="jawa_tengah",
                            label="Budaya 2 (pilihan cepat)",
                        )
                        nama_2 = gr.Textbox(
                            label="Atau ketik nama Budaya 2",
                            placeholder="mis. Jawa, Bali, Dayak, dll.",
                        )
                    prompt_2 = gr.Textbox(
                        label="Prompt tambahan Budaya 2",
                        placeholder="mis. warna coklat soga, motif parang, lembut",
                        lines=2,
                    )

                    tema_fusion = gr.Textbox(
                        label="Tema Fusion (opsional)",
                        placeholder="mis. harmoni budaya, pernikahan, festival nusantara",
                        value="harmoni budaya nusantara",
                    )

                    with gr.Row():
                        lora_scale_slider = gr.Slider(
                            label="Kekuatan LoRA (0 =abaikan, 1=full)",
                            minimum=0.0, maximum=1.5, value=0.85, step=0.05,
                        )
                        steps_slider = gr.Slider(
                            label="Langkah Inferensi",
                            minimum=10, maximum=50, value=25, step=1,
                        )
                        seed_input = gr.Number(
                            label="Seed (-1 = acak)",
                            value=-1, precision=0,
                        )

                    # (LoRA otomatis di-load dari folder lokal, lihat _cari_lora_lokal di lora_generator.py)
                    gr.Markdown(
                        "<small>ℹ️ LoRA otomatis di-load dari folder lokal. "
                        "Taruh file <code>.safetensors</code> di folder <code>lora-cache/</code> "
                        "atau root project.</small>"
                    )

                    tombol_fusi = gr.Button(
                        "[FUSION] Buat Template Fusion",
                        variant="primary",
                        size="lg",
                    )

                # ---------- KOLOM TENGAH: TEMPLATE FUSION ----------
                with gr.Column(scale=3):
                    gr.Markdown("#### Template Hasil Fusion")
                    template_gambar = gr.Image(
                        label="Gambar Fusion Batik (hasil LoRA)",
                        height=380,
                    )
                    template_markdown = gr.Markdown(
                        value="*Belum ada template fusion. Isi dua budaya di sebelah kiri lalu klik **Buat Template Fusion**.*"
                    )
                    template_state = gr.State()

                # ---------- KOLOM KANAN: SIMULASI JADI BAJU ----------
                with gr.Column(scale=2, elem_classes="corner-cloth"):
                    gr.Markdown("#### Buat Jadi Pakaian (Pojok Kanan)")
                    gr.Markdown(
                        "Hasil fusion di tengah akan diterapkan ke foto orang berbaju "
                        "di sebelah kanan layar."
                    )
                    foto_orang_f = gr.Image(
                        label="[FOTO] Foto Orang Berbaju",
                        type="pil",
                        height=260,
                    )
                    with gr.Row():
                        intensitas_f = gr.Slider(
                            label="Intensitas",
                            minimum=0.3, maximum=1.0, value=1.0, step=0.05,
                        )
                        ukuran_motif_f = gr.Slider(
                            label="Ukuran Motif",
                            minimum=0.1, maximum=1.5, value=1.0, step=0.05,
                        )
                    tombol_pakai_f = gr.Button(
                        "[PAKAI] Kenakan ke Pakaian",
                        variant="primary",
                    )
                    hasil_pakai_f = gr.Image(
                        label="Hasil Simulasi Fusion di Pakaian",
                        height=320,
                    )
                    status_pakai_f = gr.Textbox(
                        label="Status", interactive=False
                    )

            # --------- Event handler: sinkronkan dropdown -> textbox ---------
            def _sinkron_dropdown(pilihan, teks):
                # Jika user memilih dari dropdown, otomatis isi textbox
                if pilihan and pilihan != "(Lainnya / ketik sendiri)":
                    return pilihan
                return teks or ""

            dropdown_1.change(
                fn=_sinkron_dropdown,
                inputs=[dropdown_1, nama_1],
                outputs=[nama_1],
            )
            dropdown_2.change(
                fn=_sinkron_dropdown,
                inputs=[dropdown_2, nama_2],
                outputs=[nama_2],
            )

            # --------- Event handler: buat template fusion ---------
            def _proses_fusi(n1, p1, n2, p2, tema, lora_scale, steps, seed):
                nama_1_eff = (n1 or "").strip() or "Madura"
                nama_2_eff = (n2 or "").strip() or "Jawa"

                # === SMART MATCHER: cek apakah ada di database fusion ===
                from fusion_matcher import cari_fusion_dari_prompt, fusion_ke_markdown
                full_prompt = (p1 or "") + " " + (p2 or "") + " " + (tema or "")
                fusion, confidence, mode = cari_fusion_dari_prompt(
                    prompt=full_prompt,
                    budaya_1=nama_1_eff,
                    budaya_2=nama_2_eff,
                )

                if mode == "matched" and fusion:
                    # Pakai data dari database (no model load!)
                    md = fusion_ke_markdown(fusion)
                    # Try load image lokal untuk preview
                    try:
                        img_path = Path(__file__).parent / "showcase" / "images" / Path(fusion['image']).name
                        if not img_path.exists():
                            # Try image URL fallback
                            img_path = None
                            img = None
                        else:
                            from PIL import Image
                            img = Image.open(img_path)
                    except Exception:
                        img = None
                    if img is None:
                        # Placeholder dengan info matched
                        md = f"✅ **MATCHED dari database** (confidence: {confidence})\n\n" + md
                    else:
                        md = f"✅ **MATCHED dari database** (confidence: {confidence})\n\n" + md
                    return img, md, img

                # === FALLBACK: generate pakai model ===
                try:
                    t = buat_template_fusion(
                        nama_1=nama_1_eff,
                        prompt_1=p1 or "",
                        nama_2=nama_2_eff,
                        prompt_2=p2 or "",
                        tema=tema or "",
                        # LoRA otomatis di-load dari folder lokal oleh lora_generator
                        lora_scale=float(lora_scale),
                        steps=int(steps),
                        seed=int(seed) if seed is not None else -1,
                    )
                    md = template_ke_markdown(t)
                    return t.gambar, md, t.gambar
                except Exception as e:
                    return None, f"[ERROR] Terjadi error saat membuat template fusion: {e}", None

            tombol_fusi.click(
                fn=_proses_fusi,
                inputs=[
                    nama_1, prompt_1, nama_2, prompt_2,
                    tema_fusion, lora_scale_slider, steps_slider, seed_input,
                ],
                outputs=[template_gambar, template_markdown, template_state],
            )

            # --------- Event handler: simulasikan ke pakaian ---------
            def _pakai_ke_baju(foto, gambar_fusi, intensitas, ukuran):
                if gambar_fusi is None:
                    return None, "[ERROR] Belum ada gambar fusion. Buat template dulu di sebelah kiri."
                return tempel_batik_ke_baju(
                    foto_orang=foto,
                    gambar_batik=gambar_fusi,
                    intensitas=intensitas,
                    ukuran_motif=ukuran,
                )

            tombol_pakai_f.click(
                fn=_pakai_ke_baju,
                inputs=[foto_orang_f, template_state, intensitas_f, ukuran_motif_f],
                outputs=[hasil_pakai_f, status_pakai_f],
            )

            # --------- Event handler: klik kartu di showcase gallery ---------
            def _on_showcase_select(evt: gr.SelectData):
                idx = getattr(evt, "index", None)
                img, md, state = _pilih_template_dari_showcase(idx)
                if idx is None or img is None:
                    info = "*Belum ada template dipilih.*"
                else:
                    judul = _SHOWCASE_PAYLOAD[idx].get("judul", f"Template #{idx}")
                    info = f"✅ **Template #{idx} dipilih:** {judul}"
                return img, md, state, info

            showcase_gallery.select(
                fn=_on_showcase_select,
                inputs=[],
                outputs=[template_gambar, template_markdown, template_state, showcase_info],
            )


    return aplikasi


demo = bangun_antarmuka()

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0")
