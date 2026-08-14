#!/usr/bin/env python
"""Update narrative block:
1. Isi narasi madura x jawa_barat (deskripsi ciri khas madura + jawa_barat dari notebook)
2. Hapus 'prompt-pair' (tag madura x jawa_barat) dari tiap prompt item
"""
import re
from pathlib import Path

FILE = Path(r"d:\Riset MBKM\model results\Batik_Re-Palette\showcase\index.html")
txt = FILE.read_text(encoding="utf-8")

# 1) Ganti isi narasi placeholder dengan narasi asli
old_narrative = '<p class="narrative-body"><!-- TODO: narasi madura x jawabarat, akan diisi di prompt berikutnya --></p>'
new_narrative = """<p class="narrative-body">Perpaduan <strong>Madura × Jawa Barat</strong> menggabungkan dua karakter batik yang kontras namun saling melengkapi. Dari <strong>Madura</strong>, hadir motif floral stilasi (stylized floral sprigs) dalam nuansa krem dan merah di atas dasar biru tua, disertai taburan titik-titik putih kecil (isen-isen) yang rapat — ciri khas yang memberi kesan ketegasan dan keuletan. Dari <strong>Jawa Barat</strong>, kontur mega mendung (awan bergulung) mengalir bagai ombak dengan ritme bergelombang yang lembut, di atas warna biru tua dan aksen emas keemasan. Hasil fusion-nya: kain navy Madura menjadi kanvas gelap tempat gulungan mega mendung keemasan Jawa Barat mengalir, sementara taburan titik-titik putih halus Madura mengisi sela-sela. Perpaduan ini memunculkan kesan yang kuat sekaligus anggun — struktur titik Madura menopang keanggunan mega mendung khas Jawa Barat.</p>"""
assert old_narrative in txt, "Placeholder narasi tidak ditemukan"
txt = txt.replace(old_narrative, new_narrative)

# 2) Hapus prompt-pair (tag madura x jawa_barat) dari prompt-item
# Pattern: <div class="prompt-pair">...</div>
# Replace dengan string kosong (hapus div saja)
txt = re.sub(
    r'\s*<div class="prompt-pair"><span class="region-tag region-1">[^<]+</span> <span class="cross">x</span> <span class="region-tag region-2">[^<]+</span></div>',
    '',
    txt
)

# 3) Update CSS .prompt-pair margin (kalau dihapus, hilangkan margin-bottom-nya)
# Tapi kita tetap adjust CSS supaya .prompt-text jadi full tanpa pair di atas
# Kita tambah .prompt-pair gap sederhana - atau biarkan default

FILE.write_text(txt, encoding="utf-8")
print("Selesai. Panjang:", len(txt))