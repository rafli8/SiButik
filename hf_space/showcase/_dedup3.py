#!/usr/bin/env python
"""Hapus nested section-apply (yang ada di dalam section-template)
Regex hanya akan match yang nested, bukan yang baru (yang dipisahkan comment).
"""
import re
from pathlib import Path

FILE = Path(r"d:\Riset MBKM\model results\Batik_Re-Palette\showcase\index.html")
txt = FILE.read_text(encoding="utf-8")

# Hapus semua matches dari regex (semua yang nested)
nested_re = re.compile(
    r'</div>\s*<section class="section section-apply">[\s\S]*?</section>',
    re.DOTALL,
)
matches = list(nested_re.finditer(txt))
print(f"Found {len(matches)} nested section-apply blocks")

for m in reversed(matches):
    txt = txt[:m.start()] + txt[m.end():]
    print(f"Hapus di index {m.start()}")

# Sekarang cek apakah masih ada apply-preview/apply-action di dalam section-template
# Cek duplicate carousel-dots juga
print("Checking for residual apply-* inside section-template:")
section_t_re = re.compile(r'<section class="section section-template">(.*?)</section>', re.DOTALL)
sm = section_t_re.search(txt)
if sm:
    st_content = sm.group(1)
    print(f"  apply-action: {st_content.count('apply-action')}")
    print(f"  apply-preview: {st_content.count('apply-preview')}")
    print(f"  apply-panel: {st_content.count('apply-panel')}")
    print(f"  carousel-dots: {st_content.count('carousel-dots')}")

# Hapus '        </div>\n        ' atau '        </div>        ' yang extra jika ada
# Cek apakah ada extra </div> setelah carousel-dots
# Cari 'carousel-dots' diikuti '</div>' atau '</section>'
dots_after_re = re.compile(r'(<div class="carousel-dots"[^>]*></div>)\s*(</section>)')
da = dots_after_re.search(txt)
if da:
    print(f"Found carousel-dots followed by </section> at {da.start()}")

FILE.write_text(txt, encoding="utf-8")
print("Panjang:", len(txt))