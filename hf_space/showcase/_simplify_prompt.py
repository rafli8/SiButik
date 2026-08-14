#!/usr/bin/env python
"""Sederhanakan blok narasi madura x jawabarat:
1. Ganti image src ke fusion_madura_jawa_barat.png (sesuai judul 'Madura x Jawa Barat')
2. Hapus 3 prompts, ganti dengan 1 prompt (madura x jawa_barat)
3. Rapikan struktur fusion-info
"""
import re
from pathlib import Path

FILE = Path(r"d:\Riset MBKM\model results\Batik_Re-Palette\showcase\index.html")
txt = FILE.read_text(encoding="utf-8")

# 1) Ganti image src
txt = txt.replace(
    '<img src="images/fusion_madura_pola_sederhana_jawa_barat.png" alt="Fusion Madura × Jawa Barat"',
    '<img src="images/fusion_madura_jawa_barat.png" alt="Fusion Madura × Jawa Barat"',
)

# 2) Replace blok prompt (3 item) jadi 1 item madura x jawa_barat
old_prompts = '''<ul class="prompt-list">
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
                    </ul>'''
new_prompt = '''<ul class="prompt-list">
                        <li class="prompt-item">
                            <div class="prompt-pair"><span class="region-tag region-1">madura</span> <span class="cross">x</span> <span class="region-tag region-2">jawa_barat</span></div>
                            <code class="prompt-text">a madurabatik jawa_baratbatik batik pattern, Dark navy blue fabric, dense flowing gold cloud-like swirls, scattered blue floral sprigs, white dot clusters.</code>
                        </li>
                    </ul>'''
assert old_prompts in txt, "Prompt block tidak ditemukan"
txt = txt.replace(old_prompts, new_prompt)

FILE.write_text(txt, encoding="utf-8")
print("Selesai. Panjang:", len(txt))