#!/usr/bin/env python
"""Replace card 'Madura — Pola Sederhana × Jawa Barat' (madura x jawabarat)
in Section 2 with:
  - narrative placeholder (akan diisi user di prompt berikutnya)
  - 'Prompt:' section berisi 3 fusion prompt madura + jawa_barat
Update JS fusions array juga (remove entry yang dihapus).
"""

import re
from pathlib import Path

FILE = Path(r"d:\Riset MBKM\model results\Batik_Re-Palette\showcase\index.html")
txt = FILE.read_text(encoding="utf-8")
orig_len = len(txt)

# 3 fusion prompts madura + jawa_barat
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

# 1) Cari card madura-pola-sederhana x jawa_barat (card ke-11 di section 2)
# Ciri unik: data-id="fusion_madura_pola_sederhana_jawa_barat"
target_re = re.compile(
    r'<article class="carousel-item fusion-compact" id="card-fusion_madura_pola_sederhana_jawa_barat"[^>]*>.*?</article>\s*',
    re.DOTALL,
)
m = target_re.search(txt)
assert m, "Card madura_pola_sederhana × jawa_barat tidak ditemukan"

# Bangun blok pengganti: narasi placeholder + section prompt
prompt_items = []
for a, b, desc in PROMPTS:
    prompt_items.append(
        f'                    <li class="prompt-item">\n'
        f'                        <div class="prompt-pair"><span class="region-tag region-1">{a}</span> <span class="cross">x</span> <span class="region-tag region-2">{b}</span></div>\n'
        f'                        <code class="prompt-text">{build_full_prompt(a, b, desc)}</code>\n'
        f'                    </li>'
    )
prompts_html = "\n".join(prompt_items)

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

txt = txt[:m.start()] + new_block + txt[m.end():]

# 2) Update JS fusions: hapus entry madura_pola_sederhana__jawa_barat
# Cari const fusions = [...] di JS
m2 = re.search(r"const fusions = (\[.*?\]);", txt, re.DOTALL)
assert m2, "Array fusions tidak ditemukan"
fusions_js = m2.group(1)

# Parse top-level objects
def parse_top_level_objs(s):
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
print(f"Sebelum: {len(objs)} entries di JS fusions")
kept = [o for o in objs if '"madura_pola_sederhana__jawa_barat"' not in o]
print(f"Sesudah: {len(kept)} entries")
new_fusions_js = "[" + ",".join(kept) + "]"
txt = txt[:m2.start(1)] + new_fusions_js + txt[m2.end(1):]

FILE.write_text(txt, encoding="utf-8")
print(f"Ukuran: {orig_len} -> {len(txt)} byte (diff {len(txt) - orig_len:+d})")