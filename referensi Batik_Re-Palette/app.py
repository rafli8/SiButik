import gradio as gr
from PIL import Image
import numpy as np
import cv2
from scipy.spatial import distance_matrix as cdist
from scipy.optimize import linear_sum_assignment

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

def bangun_antarmuka():
    css = """
    .judul-utama { text-align: center; padding: 20px 0 10px; }
    .judul-utama h1 { font-size: 2rem; color: #5D4037; }
    .judul-utama p  { color: #795548; font-size: 0.95rem; }
    .label-seksi { font-weight: 700; color: #4E342E; margin-top: 12px; }
    footer { display: none !important; }
    """

    with gr.Blocks(title="Aplikasi Pewarnaan Batik") as aplikasi:

        gr.HTML("""
        <div class="judul-utama">
            <h1>Aplikasi Pewarnaan Ulang Batik</h1>
            <p>Ubah palet warna batik secara otomatis atau manual, buat tampilan kain, dan simulasikan pakaian batik.</p>
        </div>
        """)

        with gr.Tabs():

            # TAB 1 — DARI GAMBAR REFERENSI
            with gr.Tab("Dari Gambar Referensi"):

                gr.Markdown("### Masukkan Gambar")
                with gr.Row():
                    masukan_batik_a  = gr.Image(label="Gambar Batik Asli", type="pil")
                    masukan_referensi = gr.Image(label="Gambar Referensi Warna", type="pil")

                tombol_proses_a = gr.Button("Proses Pencocokan Warna", variant="primary", size="lg")

                gr.Markdown("### Hasil Pewarnaan Ulang")
                hasil_warna_a = gr.Image(label="Batik Hasil Pewarnaan Ulang")
                tombol_proses_a.click(
                    fn=proses_dari_referensi,
                    inputs=[masukan_batik_a, masukan_referensi],
                    outputs=[hasil_warna_a]
                )

                gr.Markdown("### Tampilan Kain Penuh")
                with gr.Row():
                    kolom_a = gr.Number(label="Jumlah Kolom", value=KOLOM_KAIN_DEFAULT, precision=0, minimum=1, maximum=20)
                    baris_a = gr.Number(label="Jumlah Baris",  value=BARIS_KAIN_DEFAULT,  precision=0, minimum=1, maximum=20)
                tombol_kain_a = gr.Button("Buat Tampilan Kain")
                hasil_kain_a  = gr.Image(label="Simulasi Kain Batik Penuh")
                tombol_kain_a.click(
                    fn=_buat_kain,
                    inputs=[hasil_warna_a, kolom_a, baris_a],
                    outputs=[hasil_kain_a]
                )

                gr.Markdown("### Simulasi Pakaian")
                gr.Markdown("Upload foto orang berbaju untuk melihat tampilan batik dikenakan.")
                with gr.Row():
                    foto_orang_a = gr.Image(label="Foto Orang Berbaju", type="pil")
                    with gr.Column():
                        ketebalan_a = gr.Slider(
                            label="Intensitas Motif Batik",
                            minimum=0.3, maximum=1.0, value=1.0, step=0.05
                        )
                        ukuran_a = gr.Slider(
                            label="Ukuran Motif Batik (kecil ↔ besar)",
                            minimum=0.1, maximum=1.5, value=1.0, step=0.05
                        )
                        tombol_tryon_a = gr.Button("Tampilkan di Pakaian", variant="primary")
                with gr.Row():
                    hasil_tryon_a = gr.Image(label="Hasil Simulasi Pakaian Batik")
                status_tryon_a = gr.Textbox(label="Status", interactive=False)
                tombol_tryon_a.click(
                    fn=tempel_batik_ke_baju,
                    inputs=[foto_orang_a, hasil_warna_a, ketebalan_a, ukuran_a],
                    outputs=[hasil_tryon_a, status_tryon_a]
                )

            # TAB 2 — PILIH WARNA MANUAL DINAMIS
            with gr.Tab("Pilih Warna Manual"):
                MAX_WARNA = 12

                gr.Markdown("### Unggah Gambar Batik")
                masukan_batik_b = gr.Image(label="Gambar Batik Asli", type="pil")

                gr.Markdown("### Ekstrak Warna Dominan")
                tombol_ekstrak = gr.Button("Ekstrak Warna Dominan", variant="secondary")
                strip_warna    = gr.Image(label="Warna Terdeteksi", height=70)

                # State: jumlah warna aktif
                state_n = gr.State(0)

                # Buat semua komponen pra-buat
                MAX_WARNA = 12
                cols     = []
                pickers  = []
                btn_dels = []
                with gr.Row():
                    for i in range(MAX_WARNA):
                        with gr.Column(min_width=90, visible=False) as col:
                            p = gr.ColorPicker(value="#ffffff", label=f"Warna {i+1}")
                            b = gr.Button("✕ Hapus", size="sm")
                        cols.append(col)
                        pickers.append(p)
                        btn_dels.append(b)

                with gr.Row():
                    btn_tambah = gr.Button("➕ Tambah Warna", size="sm", variant="secondary")

                # Helper: buat list update visibilitas col + nilai picker
                def _slot_updates(vals, n):
                    """Return list gr.update untuk cols (12) + pickers (12)."""
                    col_upd = [gr.update(visible=(i < n)) for i in range(MAX_WARNA)]
                    pic_upd = [gr.update(value=vals[i]) for i in range(MAX_WARNA)]
                    return col_upd + pic_upd

                def fn_ekstrak(batik_pil):
                    strip, hex_list = ekstrak_warna_dinamis(batik_pil)
                    n = len(hex_list)
                    padded = hex_list + ["#ffffff"] * (MAX_WARNA - n)
                    return [strip, n] + _slot_updates(padded, n)

                def fn_tambah(n, *cur_vals):
                    aktif = list(cur_vals[:n]) + ["#ffffff"]
                    new_n = min(len(aktif), MAX_WARNA)
                    padded = aktif[:new_n] + ["#ffffff"] * (MAX_WARNA - new_n)
                    return [new_n] + _slot_updates(padded, new_n)

                # Event: Ekstrak
                tombol_ekstrak.click(
                    fn=fn_ekstrak,
                    inputs=[masukan_batik_b],
                    outputs=[strip_warna, state_n] + cols + pickers,
                )

                # Event: Tambah warna
                btn_tambah.click(
                    fn=fn_tambah,
                    inputs=[state_n] + pickers,
                    outputs=[state_n] + cols + pickers,
                )

                # Event: Hapus per slot
                for i in range(MAX_WARNA):
                    def make_del_fn(slot):
                        def fn(n, *vals):
                            lst = list(vals[:n])
                            if slot < len(lst):
                                lst.pop(slot)
                            new_n = len(lst)
                            padded = lst + ["#ffffff"] * (MAX_WARNA - new_n)
                            return [new_n] + _slot_updates(padded, new_n)
                        return fn
                    btn_dels[i].click(
                        fn=make_del_fn(i),
                        inputs=[state_n] + pickers,
                        outputs=[state_n] + cols + pickers,
                    )


                gr.Markdown("### Terapkan Palet ke Gambar")


                def fn_terapkan(batik_pil, n, *vals):
                    hex_list = list(vals[:n])
                    return terapkan_warna_dinamis(batik_pil, hex_list)

                tombol_terapkan = gr.Button("Terapkan Palet", variant="primary", size="lg")
                hasil_warna_b   = gr.Image(label="Batik Hasil Pewarnaan Ulang")
                tombol_terapkan.click(
                    fn=fn_terapkan,
                    inputs=[masukan_batik_b, state_n] + pickers,
                    outputs=[hasil_warna_b],
                )

                gr.Markdown("### Tampilan Kain")
                with gr.Row():
                    kolom_b = gr.Number(label="Jumlah Kolom", value=KOLOM_KAIN_DEFAULT, precision=0, minimum=1, maximum=20)
                    baris_b = gr.Number(label="Jumlah Baris",  value=BARIS_KAIN_DEFAULT,  precision=0, minimum=1, maximum=20)
                tombol_kain_b = gr.Button("Buat Tampilan Kain")
                hasil_kain_b  = gr.Image(label="Simulasi Kain Batik Penuh")
                tombol_kain_b.click(
                    fn=_buat_kain,
                    inputs=[hasil_warna_b, kolom_b, baris_b],
                    outputs=[hasil_kain_b]
                )

                gr.Markdown("### Simulasi Pakaian")
                gr.Markdown("Upload foto orang berbaju untuk melihat tampilan batik dikenakan.")
                with gr.Row():
                    foto_orang_b = gr.Image(label="📷 Foto Orang Berbaju", type="pil")
                    with gr.Column():
                        ketebalan_b = gr.Slider(
                            label="Intensitas Motif Batik",
                            minimum=0.3, maximum=1.0, value=1.0, step=0.05
                        )
                        ukuran_b = gr.Slider(
                            label="Ukuran Motif Batik",
                            minimum=0.1, maximum=1.5, value=1.0, step=0.05
                        )
                        tombol_tryon_b = gr.Button("Tampilkan di Pakaian", variant="primary")
                with gr.Row():
                    hasil_tryon_b = gr.Image(label="Hasil Simulasi Pakaian Batik")
                status_tryon_b = gr.Textbox(label="Status", interactive=False)
                tombol_tryon_b.click(
                    fn=tempel_batik_ke_baju,
                    inputs=[foto_orang_b, hasil_warna_b, ketebalan_b, ukuran_b],
                    outputs=[hasil_tryon_b, status_tryon_b]
                )


    return aplikasi


demo = bangun_antarmuka()

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0")
