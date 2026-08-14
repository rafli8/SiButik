#!/usr/bin/env python
"""Sederhanakan Section 2 (Template) sesuai instruksi user:
1. Heading: hanya "Template" (hapus "Hasil" + subtitle)
2. Setiap card (1-11): hanya judul (hapus deskripsi, triggers, details, chips, summary, button)
3. Hapus card 12-21 (sisakan sampai Madura-Pola Sederhana × Jawa Barat)
4. Update teks resultInfo
5. Update array fusions di JS
"""

import re
from pathlib import Path

FILE = Path(r"d:\Riset MBKM\model results\Batik_Re-Palette\showcase\index.html")
txt = FILE.read_text(encoding="utf-8")
orig_len = len(txt)

# 1) Heading section 2: ganti 'Template Hasil' + subtitle jadi cuma 'Template'
old_heading = (
    '                <div>\n'
    '                    <h2>Template Hasil</h2>\n'
    '                    <p class="section-sub">Scroll atau gunakan tombol untuk melihat template fusion. Klik "Pilih Template Ini" untuk dibawa ke langkah berikutnya.</p>\n'
    '                </div>\n'
)
new_heading = (
    '                <div>\n'
    '                    <h2>Template</h2>\n'
    '                </div>\n'
)
assert old_heading in txt, "Heading section 2 tidak ditemukan (sudah pernah diedit?)"
txt = txt.replace(old_heading, new_heading)

# 2) Update resultInfo
txt = txt.replace(
    '<span id="resultInfo">Menampilkan semua 21 template</span>',
    '<span id="resultInfo">Menampilkan 11 template</span>',
)

# 3) Cari dan proses semua <article class="carousel-item fusion-compact"> ... </article>
article_pattern = re.compile(
    r"<article class=\"carousel-item fusion-compact\"[^>]*>.*?</article>\s*",
    re.DOTALL,
)
articles = article_pattern.findall(txt)
print(f"Ditemukan {len(articles)} article blocks")

# 4) Tentukan card mana yang disimpan (1-11) dan dihapus (12-21)
# Urutan card dari pembacaan sebelumnya
KEPT_INDICES = list(range(0, 11))  # card 1-11 (index 0-10)
REMOVED_INDICES = list(range(11, len(articles)))  # card 12-21 (index 11-20)

# 5) Untuk setiap card yang disimpan, ambil hanya img src, alt, judul, region tags
def simplify_card(article_html: str) -> str:
    # Ambil image src
    img_match = re.search(r'<img src="([^"]+)" alt="([^"]+)"', article_html)
    img_src = img_match.group(1) if img_match else ""
    img_alt = img_match.group(2) if img_match else ""
    # Ambil judul
    title_match = re.search(r'<h3 class="compact-judul">(.*?)</h3>', article_html)
    title = title_match.group(1) if title_match else ""
    # Ambil region-1 dan region-2 (kalau ada)
    r1_match = re.search(r'<span class="region-tag region-1">([^<]+)</span>', article_html)
    r2_match = re.search(r'<span class="region-tag region-2">([^<]+)</span>', article_html)
    r1 = r1_match.group(1) if r1_match else ""
    r2 = r2_match.group(1) if r2_match else ""

    # Buat ID unik dari judul untuk data-id (sederhana)
    slug = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")

    # Struktur minimal card
    new_card = f'''<article class="carousel-item fusion-compact" id="card-{slug}" data-id="{slug}">
            <div class="compact-image">
                <img src="{img_src}" alt="{img_alt}" loading="lazy">
            </div>
            <div class="compact-body">
                <div class="compact-region">
                    <span class="region-tag region-1">{r1}</span>
                    <span class="cross">x</span>
                    <span class="region-tag region-2">{r2}</span>
                </div>
                <h3 class="compact-judul">{title}</h3>
            </div>
        </article>


'''
    return new_card

# Bangun teks baru: gabungkan ulang articles
new_articles_text = ""
for i, art in enumerate(articles):
    if i in KEPT_INDICES:
        new_articles_text += simplify_card(art)
    # yang lain dihapus (skip)
    # juga tidak ada separator blank line di antara card yang disimpan

# Replace semua articles dengan teks baru
# Karena regex findall mengembalikan list, kita pakai finditer + position untuk replace
def replace_articles(text: str) -> str:
    pieces = []
    last_end = 0
    for m in article_pattern.finditer(text):
        pieces.append(text[last_end:m.start()])
        last_end = m.end()
    pieces.append(text[last_end:])

    # Rekonstruksi: pieces[0] + articles baru (yang sudah disederhanakan/dihapus) + pieces[1..]
    # articles[i] correspond to between pieces[i] and pieces[i+1]
    new_parts = [pieces[0]]
    for i in range(len(articles)):
        if i in KEPT_INDICES:
            new_parts.append(simplify_card(articles[i]))
        # else: skip (deleted)
        new_parts.append(pieces[i + 1])
    return "".join(new_parts)

txt = replace_articles(txt)

# 6) Update JS fusions array: pertahankan hanya 11 entri pertama
# Cari 'const fusions = [' dan hitung entri level-1 di array
m = re.search(r"const fusions = (\[.*?\]);", txt, re.DOTALL)
assert m, "Array fusions tidak ditemukan"
fusions_js = m.group(1)
# Parse top-level objects (seimbang kurung)
def parse_top_level_objs(s: str):
    """Mengambil list of top-level {...} objects dalam JSON array s."""
    objs = []
    depth = 0
    start = None
    in_str = False
    esc = False
    for i, ch in enumerate(s):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start is not None:
                objs.append(s[start:i + 1])
                start = None
    return objs

objs = parse_top_level_objs(fusions_js)
print(f"Ditemukan {len(objs)} entri di JS fusions array")
kept_objs = objs[:11]
new_fusions_js = "[" + ",".join(kept_objs) + "]"
txt = txt[:m.start(1)] + new_fusions_js + txt[m.end(1):]

# Simpan
FILE.write_text(txt, encoding="utf-8")
new_len = len(txt)
print(f"Selesai. Ukuran: {orig_len} -> {new_len} byte (diff {new_len - orig_len:+d})")
print(f"Article kept: {len(KEPT_INDICES)}, removed: {len(REMOVED_INDICES)}")
print(f"JS fusions kept: {len(kept_objs)}, removed: {len(objs) - len(kept_objs)}")