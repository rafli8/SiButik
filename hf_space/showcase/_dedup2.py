#!/usr/bin/env python
"""Hapus nested section-apply, keep yang terakhir (yang baru ditambahkan benar)
"""
import re
from pathlib import Path

FILE = Path(r"d:\Riset MBKM\model results\Batik_Re-Palette\showcase\index.html")
txt = FILE.read_text(encoding="utf-8")

nested_re = re.compile(
    r'</div>\s*<section class="section section-apply">[\s\S]*?</section>',
    re.DOTALL,
)
matches = list(nested_re.finditer(txt))
print(f"Found {len(matches)} nested section-apply blocks")

# Hapus semua KECUALI yang terakhir (yang baru ditambahkan dengan benar)
for m in matches[:-1]:
    txt = txt[:m.start()] + txt[m.end():]
    print(f"Hapus nested section-apply di index {m.start()}")

# Sekarang juga cek apakah masih ada duplicate apply-action, apply-preview
# Cek duplicate apply-action (di section-template yang seharusnya tidak ada)
# Cari pattern apply-action di dalam section-template
# Cari: position </section> setelah section-template ke apply-action pertama
section_t_re = re.compile(r'<section class="section section-template">(.*?)</section>', re.DOTALL)
sm = section_t_re.search(txt)
if sm:
    section_t_content = sm.group(1)
    # Hitung apply-action di section-template
    inner_apply_actions = section_t_content.count('apply-action')
    inner_apply_previews = section_t_content.count('apply-preview')
    print(f"Inside section-template: apply-action={inner_apply_actions}, apply-preview={inner_apply_previews}")
    if inner_apply_actions > 0 or inner_apply_previews > 0:
        # Hapus bagian apply dari section-template
        # Cari apply-panel yang ada di dalam section-template
        # Asumsi: apply-panel, apply-preview, apply-action, apply-note adalah struktur nested yg harus hilang
        # Hapus dari <div class="apply-panel"> sampai </section> yang menutup apply-action
        # Hmm, mungkin lebih mudah: cari "        <div class=\"apply-panel\">" dan hapus dari sana sampai "</section>" pertama setelah-nya
        panel_re = re.compile(r'        <div class="apply-panel">[\s\S]*?</section>')
        pm = panel_re.search(section_t_content)
        if pm:
            # Build new section_template without apply panel
            new_section_t = section_t_content[:pm.start()] + section_t_content[pm.end():]
            # Hapus extra </div> jika ada
            # Original section-t dengan apply-panel dihapus, replaced dengan section-t closing
            # Actually, let me reconstruct: replace section_template full match
            new_section_t_full = '<section class="section section-template">' + new_section_t + '</section>'
            txt = txt.replace(sm.group(0), new_section_t_full)
            print("Apply-panel nested dihapus dari section-template")

FILE.write_text(txt, encoding="utf-8")
print("Panjang:", len(txt))