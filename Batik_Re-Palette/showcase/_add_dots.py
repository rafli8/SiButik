#!/usr/bin/env python
"""Add carousel-dots inside section-template (right after fusion-narrative-block, before </section>)
"""
import re
from pathlib import Path

FILE = Path(r"d:\Riset MBKM\model results\Batik_Re-Palette\showcase\index.html")
txt = FILE.read_text(encoding="utf-8")

# Cari pattern: </div> penutup fusion-narrative-block, diikuti </section>
# Insert carousel-dots di antara keduanya
pattern = re.compile(
    r'(</div>\s*\n\s*</div>\s*\n\s*</section>)',
)
m = pattern.search(txt)
if m:
    # Sisipkan carousel-dots SEBELUM </section>
    insert = '\n\n            <div class="carousel-dots" id="carouselDots"></div>\n        </section>'
    # Replace m.group(1) dengan insert
    txt = txt[:m.start()] + insert + txt[m.end():]
    print("Carousel-dots ditambahkan ke section-template")
else:
    print("Pattern tidak ditemukan, mencoba alternatif")
    # Cari </section> yang diikuti dengan section-apply atau main
    alt = re.compile(r'(</section>)(\s*\n\s*<section class="section section-apply">)')
    m2 = alt.search(txt)
    if m2:
        # Cari </div></div> sebelum m2 untuk dapat lokasi narrative end
        # Cari </div>\s*</div>\s*\n\s*</section> yang muncul pertama
        dots_re = re.compile(r'(</div>\s*</div>)\s*\n(\s*</section>)')
        m3 = dots_re.search(txt[:m2.start()])
        if m3:
            insert = '\n\n            <div class="carousel-dots" id="carouselDots"></div>'
            txt = txt[:m3.end(1)] + insert + txt[m3.end(1):]
            print("Carousel-dots ditambahkan (alt)")

FILE.write_text(txt, encoding="utf-8")
print("Panjang:", len(txt))