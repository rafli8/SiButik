#!/usr/bin/env python
"""Restructure narrative block: kiri = gambar, kanan = narasi + prompts.
Layout mirip card compact-image | compact-body yang dipakai di carousel.
"""
import re
from pathlib import Path

FILE = Path(r"d:\Riset MBKM\model results\Batik_Re-Palette\showcase\index.html")
txt = FILE.read_text(encoding="utf-8")

# 1) Replace blok narrative-block lama dengan struktur baru (image | info)
old_block = re.compile(
    r'<div class="fusion-narrative-block" id="narrative-madura-jawa-barat">.*?</div>\s*</div>\s*</div>\s*',
    re.DOTALL,
)
m = old_block.search(txt)
assert m, "Blok narrative-block lama tidak ditemukan"

new_block = '''<div class="fusion-narrative-block" id="narrative-madura-jawa-barat">
            <div class="fusion-image">
                <img src="images/fusion_madura_pola_sederhana_jawa_barat.png" alt="Fusion Madura × Jawa Barat" loading="lazy">
            </div>
            <div class="fusion-info">
                <div class="fusion-region">
                    <span class="region-tag region-1">Madura</span>
                    <span class="cross">x</span>
                    <span class="region-tag region-2">Jawa Barat</span>
                </div>
                <h3 class="fusion-judul">Fusion Madura × Jawa Barat</h3>
                <div class="fusion-narrative">
                    <h3 class="narrative-title">Narasi</h3>
                    <p class="narrative-body"><!-- TODO: narasi madura x jawabarat, akan diisi di prompt berikutnya --></p>
                </div>
                <div class="fusion-prompts">
                    <h3 class="prompts-title">Prompt:</h3>
                    <ul class="prompt-list">
                        <li class="prompt-item">
                            <div class="prompt-pair"><span class="region-tag region-1">madura</span> <span class="cross">x</span> <span class="region-tag region-2">jawa_barat</span></div>
                            <code class="prompt-text">a madurabatik jawa_baratbatik batik pattern, Dark navy blue fabric, dense flowing gold cloud-like swirls, scattered blue floral sprigs, white dot clusters.</code>
                        </li>
                        <li class="prompt-item">
                            <div class="prompt-pair"><span class="region-tag region-1">madura_pola_sederhana</span> <span class="cross">x</span> <span class="region-tag region-2">jawa_barat</span></div>
                            <code class="prompt-text">a madura_pola_sederhanabatik jawa_baratbatik batik pattern, Deep navy fabric with flowing gold cloud-like swirls intertwined with bold golden-yellow floral sprigs and blossoms in a dense, high-contrast layout.</code>
                        </li>
                        <li class="prompt-item">
                            <div class="prompt-pair"><span class="region-tag region-1">madura_pola_kompleks</span> <span class="cross">x</span> <span class="region-tag region-2">jawa_barat</span></div>
                            <code class="prompt-text">a madura_pola_kompleksbatik jawa_baratbatik batik pattern, Deep blue fabric where flowing gold cloud-like swirls intertwine with vibrant floral sprigs, swirling leaves, and butterflies in red and teal.</code>
                        </li>
                    </ul>
                </div>
            </div>
        </div>

'''
txt = txt[:m.start()] + new_block + txt[m.end():]

FILE.write_text(txt, encoding="utf-8")
print("Selesai. Panjang:", len(txt))