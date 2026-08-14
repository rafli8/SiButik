#!/usr/bin/env python
"""Perbaiki struktur section 2 dan section 3 yang rusak:
1. Tambah carousel-dots di akhir section-template (sebelum </section>)
2. Tambah section-apply lengkap dengan header & apply-panel (sebelum apply-action)
"""
import re
from pathlib import Path

FILE = Path(r"d:\Riset MBKM\model results\Batik_Re-Palette\showcase\index.html")
txt = FILE.read_text(encoding="utf-8")

# 1) Insert carousel-dots sebelum </section> penutup section-template
# Cari section-template section: patternnya section yg punya carouselDots sebelumnya,
# tapi karena dots hilang, kita cari </section> yang diikuti dengan apply-action
section_end_re = re.compile(
    r'(        </div>\s*\n\s*</section>\s*\n\s*<div class="apply-action">)',
    re.DOTALL,
)
m = section_end_re.search(txt)
if m:
    # Sisipkan carousel-dots SEBELUM </section>
    new_content = '\n            <div class="carousel-dots" id="carouselDots"></div>\n' + m.group(1)
    txt = txt[:m.start()] + new_content + txt[m.end():]
    print("Carousel-dots ditambahkan")
else:
    print("Pattern section-end tidak ditemukan, coba alternatif")
    # Cari </section> yang diikuti dengan class apply-action (skip narrative block)
    alt_re = re.compile(
        r'(</div>\s*\n\s*</section>)(\s*\n\s*<div class="apply-action">)',
    )
    m2 = alt_re.search(txt)
    if m2:
        txt = txt[:m2.end(1)] + '\n\n            <div class="carousel-dots" id="carouselDots"></div>\n        ' + txt[m2.end(1):]
        print("Carousel-dots ditambahkan (alt)")

# 2) Sisipkan section-apply lengkap sebelum <div class="apply-action">
apply_section_header = '''        <section class="section section-apply">
            <header class="section-head">
                <span class="section-num">3</span>
                <div>
                    <h2>Terapkan ke Baju</h2>
                    <p class="section-sub">Template yang dipilih akan diterapkan ke pola pakaian menggunakan segmentasi area pakaian (rembg u2net_cloth_seg).</p>
                </div>
            </header>
            <div class="apply-panel">
                <div class="apply-preview" id="applyPreview">
                    <div class="apply-placeholder" id="applyPlaceholder">
                        <svg viewBox="0 0 24 24" width="42" height="42" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                            <path d="M20.38 3.46L16 2a4 4 0 0 1-8 0L3.62 3.46a2 2 0 0 0-1.34 2.23l.58 3.47a1 1 0 0 0 .99.84H6v10c0 1.1.9 2 2 2h8a2 2 0 0 0 2-2V10h2.15a1 1 0 0 0 .99-.84l.58-3.47a2 2 0 0 0-1.34-2.23z"/>
                        </svg>
                        <p>Belum ada template dipilih</p>
                        <small>Pilih template di atas untuk diterapkan ke baju</small>
                    </div>
                    <div class="apply-result" id="applyResult" hidden>
                        <img id="applyImage" src="" alt="Template fusion">
                        <div class="apply-overlay">
                            <strong id="applyTitle"></strong>
                            <span id="applyTriggers"></span>
                        </div>
                    </div>
                </div>
'''
apply_re = re.compile(r'(\s*<div class="apply-action">)')
m3 = apply_re.search(txt)
if m3:
    txt = txt[:m3.start()] + apply_section_header + txt[m3.start():]
    print("Apply section header ditambahkan")

# 3) Tutup apply-panel dan section-apply setelah apply-action
# Cari </div> terakhir dari apply-action
apply_close_re = re.compile(
    r'(<p class="apply-note" id="applyNote">[\s\S]*?</p>\s*)\n(\s*</div>\s*)\n(\s*</main>)',
)
m4 = apply_close_re.search(txt)
if m4:
    # Tambahkan closing tags
    extra_close = '\n            </div>\n        </section>\n'
    txt = txt[:m3.end()] + txt[m3.end():m4.start()] + m4.group(1) + extra_close + m4.group(3) + txt[m4.end():]
    # Tapi di sini m3.end() adalah posisi sebelum <div class="apply-action">
    # Mari saya kerjakan ulang lebih hati-hati
    pass

# Cara lebih sederhana: cari </p> dari apply-note, lalu tambahkan closing
note_end_re = re.compile(
    r'(<p class="apply-note" id="applyNote">[\s\S]*?</p>)',
)
m5 = note_end_re.search(txt)
if m5:
    closing = '\n            </div>\n        </section>\n'
    # Cek apakah sudah ada closing
    if 'section-apply' not in txt[m5.end():m5.end()+500]:
        txt = txt[:m5.end()] + closing + txt[m5.end():]
        print("Apply section closing ditambahkan")

FILE.write_text(txt, encoding="utf-8")
print("Selesai. Panjang:", len(txt))