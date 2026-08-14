#!/usr/bin/env python
"""Final cleanup: hapus duplicate section-apply yang masih nested
"""
import re
from pathlib import Path

FILE = Path(r"d:\Riset MBKM\model results\Batik_Re-Palette\showcase\index.html")
txt = FILE.read_text(encoding="utf-8")

# Hapus section-apply nested (yang ada di line 278)
# Pattern: </div> tepat diikuti section-apply, sampai closing </section>
nested_re = re.compile(
    r'</div>\s*<section class="section section-apply">[\s\S]*?</section>',
    re.DOTALL,
)
matches = list(nested_re.finditer(txt))
print(f"Found {len(matches)} nested section-apply blocks")
# Hapus yang DUPLICATE (bukan yang baru ditambahkan dengan benar)
# Asumsi: yang pertama adalah nested (line ~278), yang kedua adalah yang baru (line ~329)
# Kita hapus yang pertama (duplicate)
for i, m in enumerate(reversed(matches)):
    if i == len(matches) - 1:
        # Skip the LAST one (newly added correct one)
        continue
    txt = txt[:m.start()] + txt[m.end():]
    print(f"Hapus nested section-apply #{i+1}")

# Tapi kita perlu menjaga konsistensi: kalau ada 2 section-apply, hapus yang pertama
# Mari cek hasilnya
remaining = nested_re.findall(txt)
print(f"Sisa: {len(remaining)} section-apply blocks")

FILE.write_text(txt, encoding="utf-8")
print("Panjang:", len(txt))