#!/usr/bin/env python
"""Rebuild bersih bagian rusak di section 2:
1. Hapus orphan prompts yang masih di dalam carousel + extra closing divs
2. Hapus orphan narrative block
3. Sisipkan blok narrative + prompts yang rapi sebelum carousel-dots
"""
import re
from pathlib import Path

FILE = Path(r"d:\Riset MBKM\model results\Batik_Re-Palette\showcase\index.html")
txt = FILE.read_text(encoding="utf-8")

# 1) Hapus orphan prompts di dalam carousel: mulai dari <div class="fusion-prompts">
# sampai sebelum <button type="button" class="carousel-nav next"
broken_pattern = re.compile(
    r'<div class="fusion-prompts">.*?</ul>\s*</div>\s*</div>\s*</div>\s*<button type="button" class="carousel-nav next"',
    re.DOTALL,
)
m = broken_pattern.search(txt)
assert m, "Broken orphan block tidak ditemukan"
# Replace dengan <button next saja
txt = txt[:m.start()] + '<button type="button" class="carousel-nav next"' + txt[m.end():]

# 2) Hapus orphan narrative block: dari <div class="fusion-narrative-block">...</div></div>
# Pattern: <div class="fusion-narrative-block"...>...</div>\n\n        </div>
narrative_orphan = re.compile(
    r'<div class="fusion-narrative-block" id="narrative-madura-jawa-barat">.*?</div>\s*</div>\s*',
    re.DOTALL,
)
m2 = narrative_orphan.search(txt)
assert m2, "Orphan narrative block tidak ditemukan"
txt = txt[:m2.start()] + txt[m2.end():]

# 3) Ambil prompts list inner content dari teks yang baru (cari dari awal - prompts sudah dihapus dari orphan)
# Prompts sudah hilang, jadi kita perlu reconstruct dari informasi FUSION_DESCRIPTIONS notebook
PROMPTS = [
    ("madura", "jawa_barat",
     "Dark navy blue fabric, dense flowing gold cloud-like swirls, scattered blue floral sprigs, white dot clusters."),
    ("madura_pola_sederhana", "jawa_barat",
     "Deep navy fabric with flowing gold cloud-like swirls intertwined with bold golden-yellow floral sprigs and blossoms in a dense, high-contrast layout."),
    ("madura_pola_kompleks", "jawa_barat",
     "Deep blue fabric where flowing gold cloud-like swirls intertwine with vibrant floral sprigs, swirling leaves, and butterflies in red and teal."),
]

def build_full_prompt(a, b, desc):
    return f"a {a}batik {b}batik batik pattern, {desc}"

prompt_items = []
for a, b, desc in PROMPTS:
    prompt_items.append(
        f'                    <li class="prompt-item">\n'
        f'                        <div class="prompt-pair"><span class="region-tag region-1">{a}</span> <span class="cross">x</span> <span class="region-tag region-2">{b}</span></div>\n'
        f'                        <code class="prompt-text">{build_full_prompt(a, b, desc)}</code>\n'
        f'                    </li>'
    )
prompts_html = "\n".join(prompt_items)

# 4) Bangun blok narrative+prompts yang bersih dan sisipkan sebelum <div class="carousel-dots"
new_block = f'''<div class="fusion-narrative-block" id="narrative-madura-jawa-barat">
            <div class="fusion-narrative">
                <h3 class="narrative-title">Narasi</h3>
                <p class="narrative-body"><!-- TODO: narasi madura x jawabarat, akan diisi di prompt berikutnya --></p>
            </div>
            <div class="fusion-prompts">
                <h3 class="prompts-title">Prompt:</h3>
                <ul class="prompt-list">
{prompts_html}
                </ul>
            </div>
        </div>

'''

dots_re = re.compile(r'(<div class="carousel-dots" id="carouselDots"></div>)')
m3 = dots_re.search(txt)
assert m3, "carousel-dots tidak ditemukan"
txt = txt[:m3.start(1)] + new_block + "            " + txt[m3.start(1):]

FILE.write_text(txt, encoding="utf-8")
print("Selesai. Panjang:", len(txt))