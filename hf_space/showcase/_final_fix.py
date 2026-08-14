#!/usr/bin/env python
"""Perbaiki struktur section 2 dan section 3 dari awal:
- Tutup section-template dengan benar (carousel-dots di dalamnya)
- Buka section-apply setelah section-template (bukan nested)
"""
import re
from pathlib import Path

FILE = Path(r"d:\Riset MBKM\model results\Batik_Re-Palette\showcase\index.html")
txt = FILE.read_text(encoding="utf-8")

# Hapus misplaced section-apply (yang ada di dalam section-template)
# Pattern: mulai dari "<section class="section section-apply">" sampai "</section>" tepat setelah apply-action
# Hapus misplaced carousel-dots (yang ada di luar section-template)
# Lalu kita perlu: section-template close + carousel-dots + section-apply

# 1) Hapus misplaced section-apply dan carousel-dots dari posisi salah
# Cari pola: "        </div>\n        <section class="section section-apply">" (nested)
nested_re = re.compile(
    r'(        </div>\s*\n\s*)<section class="section section-apply">[\s\S]*?</section>',
    re.DOTALL,
)
m = nested_re.search(txt)
if m:
    # Simpan section-apply content untuk dipakai nanti
    section_apply_content = m.group(0).split('<section class="section section-apply">', 1)[1].rsplit('</section>', 1)[0]
    txt = txt[:m.start()] + m.group(1) + txt[m.end():]
    print(f"Nested section-apply dihapus, panjang saved: {len(section_apply_content)}")
else:
    print("Nested section-apply tidak ditemukan")
    section_apply_content = None

# 2) Hapus misplaced carousel-dots (yang ada setelah </section>)
dots_re = re.compile(
    r'(        </section>\s*\n\s*)<div class="carousel-dots" id="carouselDots"></div>',
    re.DOTALL,
)
m2 = dots_re.search(txt)
if m2:
    txt = txt[:m2.start()] + m2.group(1) + txt[m2.end():]
    print("Misplaced carousel-dots dihapus")

# 3) Sekarang struktur section-template masih perlu ditutup + carousel-dots ditambahkan + section-apply ditambahkan
# Cari penutup section-template: </section> diikuti </main>
end_re = re.compile(
    r'(\s*</section>)(\s*\n\s*</main>)',
)
m3 = end_re.search(txt)
if m3:
    section_template_close = m3.group(1)
    main_open = m3.group(2)
    # Section-apply baru
    section_apply_new = '''

        <!-- ============================== SECTION 3: TERAPKAN KE BAJU ============================== -->
        <section class="section section-apply">
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
                <div class="apply-action">
                    <button type="button" class="btn-apply" id="applyBtn" disabled>
                        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                            <path d="M20 6L9 17l-5-5"/>
                        </svg>
                        Terapkan ke Baju
                    </button>
                    <p class="apply-note" id="applyNote">
                        Fitur ini akan aktif setelah template dipilih.
                        Pada aplikasi Gradio interaktif, simulasi memakai segmentasi area
                        pakaian (rembg u2net_cloth_seg) + Feathered Seams tiling.
                    </p>
                </div>
            </div>
        </section>
'''
    # Insert carousel-dots + section-apply SEBELUM </main>
    insert = '\n\n            <div class="carousel-dots" id="carouselDots"></div>\n        ' + section_template_close + section_apply_new + main_open
    txt = txt[:m3.start()] + insert + txt[m3.end():]
    print("Section-template ditutup + carousel-dots ditambah + section-apply ditambahkan")

FILE.write_text(txt, encoding="utf-8")
print("Selesai. Panjang:", len(txt))