#!/usr/bin/env python
"""Perbaiki layout yang rusak:
1. Hapus orphan fusion-prompts yang masih di dalam carousel
2. Pindahkan prompts block ke dalam fusion-narrative-block (yang sekarang narasi saja)
3. Hasil akhir: narrative + prompts ada di luar carousel, sebelum carousel-dots
"""
import re
from pathlib import Path

FILE = Path(r"d:\Riset MBKM\model results\Batik_Re-Palette\showcase\index.html")
txt = FILE.read_text(encoding="utf-8")

# 1) Hapus orphan fusion-prompts di dalam carousel (plus extra closing </div>)
orphan_pattern = re.compile(
    r'<div class="fusion-prompts">.*?</div>\s*</div>\s*</div>\s*<button type="button" class="carousel-nav next"',
    re.DOTALL,
)
m = orphan_pattern.search(txt)
assert m, "Orphan prompts tidak ditemukan"
txt = txt[:m.start()] + '<button type="button" class="carousel-nav next"' + txt[m.end():]

# 2) Sekarang narrative-madura-jawa-barat ada di luar, tapi prompts-nya sudah terpisah
# Kita perlu copy prompts content dari tempat lama ke dalam narrative block
# Ambil content dari prompts list (cari setelah "Prompt:" di file saat ini)
prompts_re = re.compile(
    r'<ul class="prompt-list">(.*?)</ul>',
    re.DOTALL,
)
m2 = prompts_re.search(txt)
assert m2, "Daftar prompts <ul> tidak ditemukan"
prompts_list_inner = m2.group(1)

# Hapus prompts list yang terpisah itu (cari blok lengkap fusion-prompts yang orphan)
orphan_prompts_full = re.compile(
    r'<div class="fusion-prompts">.*?</div>\s*</div>\s*',
    re.DOTALL,
)
matches = list(orphan_prompts_full.finditer(txt))
print(f"Found {len(matches)} orphan prompts blocks to remove")
# Hapus yang terakhir (yang paling baru) - ini yang ada di luar narrative
# Sebenarnya kita sudah hapus 1 di step 1. Cari yang masih ada.
for match in reversed(matches):
    # Skip yang di dalam carousel (sudah dihapus di step 1)
    txt = txt[:match.start()] + txt[match.end():]

# 3) Sisipkan prompts ke dalam narrative block
narrative_block = re.compile(
    r'(<div class="fusion-narrative-block" id="narrative-madura-jawa-barat">.*?)(</div>\s*</div>)',
    re.DOTALL,
)
m3 = narrative_block.search(txt)
assert m3, "Narrative block tidak ditemukan"

prompts_section = f'''
            <div class="fusion-prompts">
                <h3 class="prompts-title">Prompt:</h3>
                <ul class="prompt-list">{prompts_list_inner}</ul>
            </div>
'''

# Sisipkan tepat sebelum </div>\s*</div> penutup fusion-narrative-block
txt = txt[:m3.start(2)] + prompts_section + "        " + txt[m3.start(2):]

FILE.write_text(txt, encoding="utf-8")
print("Selesai. Panjang:", len(txt))