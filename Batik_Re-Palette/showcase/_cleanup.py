#!/usr/bin/env python
"""Cleanup:
1. Pindahkan blok narasi+prompt dari dalam carousel ke luar (setelah carousel-wrapper)
2. Hapus entry JS fusions yang punya id 'madura — pola sederhana__jawa barat'
3. Update counter dari 11 ke 10
"""

import re
from pathlib import Path

FILE = Path(r"d:\Riset MBKM\model results\Batik_Re-Palette\showcase\index.html")
txt = FILE.read_text(encoding="utf-8")

# 1) Potong blok narasi dari dalam carousel
narrative_re = re.compile(
    r'<div class="fusion-narrative-block" id="narrative-madura-jawa-barat">.*?</div>\s*',
    re.DOTALL,
)
m = narrative_re.search(txt)
assert m, "Blok narasi tidak ditemukan"
narrative_block = m.group(0)
txt = txt[:m.start()] + txt[m.end():]

# 2) Sisipkan setelah </div> penutup carousel dan sebelum carousel-nav next
# Yaitu setelah baris `</div>` (penutup <div class="carousel">)
# Cari pola: </div>\n                <button type="button" class="carousel-nav next"
sisah_re = re.compile(
    r'(</div>\s*\n\s*<button type="button" class="carousel-nav next")',
)
m2 = sisah_re.search(txt)
assert m2, "Penutup carousel tidak ditemukan"
# Sisipkan narrative block SEBELUM tag <button> next (jadi EXIT carousel dulu)
txt = txt[:m2.start()] + narrative_block + "\n" + txt[m2.start():]

# 3) Update counter
txt = txt.replace(
    '<span id="resultInfo">Menampilkan 11 template</span>',
    '<span id="resultInfo">Menampilkan 10 template</span>',
)

# 4) Hapus entry JS fusions yg id-nya madura_pola_sederhana__jawa_barat (dg em-dash & spasi)
# Format: "id": "madura — pola sederhana__jawa barat"
js_re = re.compile(
    r'\{\s*"id":\s*"madura — pola sederhana__jawa barat"[^}]*\}\s*\}',
    re.DOTALL,
)
# Coba cari entry lengkap
# Cari dari "id": "madura — pola sederhana__jawa barat" sampai kurung tutup bersarang
m3 = re.search(r'"id":\s*"madura — pola sederhana__jawa barat"', txt)
assert m3, "Entry JS id madura-pola-sederhana-jawa-barat tidak ditemukan"
# Cari kurung buka { sebelum dan kurung tutup } setelah
open_idx = txt.rfind('{', 0, m3.start())
# Cari koma/bracket setelah untuk tentukan akhir
# Cari balanced } setelahnya
depth = 0
end_idx = None
for i in range(open_idx, len(txt)):
    if txt[i] == '{':
        depth += 1
    elif txt[i] == '}':
        depth -= 1
        if depth == 0:
            end_idx = i + 1
            break
assert end_idx, "Tidak bisa menemukan akhir object"
# Hapus object + koma setelahnya
slice_to_remove = txt[open_idx:end_idx]
# Skip trailing comma
remove_end = end_idx
if end_idx < len(txt) and txt[end_idx] == ',':
    remove_end += 1
# Skip leading whitespace
remove_start = open_idx
while remove_start > 0 and txt[remove_start - 1] in ' \t\n':
    remove_start -= 1
txt = txt[:remove_start] + txt[remove_end:]

FILE.write_text(txt, encoding="utf-8")
print("Selesai. Panjang:", len(txt))