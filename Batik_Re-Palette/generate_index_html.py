# -*- coding: utf-8 -*-
"""
generate_index_html.py
======================
Membangun showcase/index.html sebagai galeri statis siap-demo untuk
aplikasi "SiButik: Silang Budaya Batik" - SDXL + LoRA Joint Training generator.

Tampilan: Gradio-style DARK + PASTEL palette (eye-friendly).

Layout (1 halaman, 3 bagian):
  1. Generator    : 2 dropdown budaya + prompt input
  2. Template     : Carousel fusion (compact, 1 per view, scroll/arrow)
  3. Terapkan     : Preview + tombol "Terapkan ke Baju"

Sumber data: fusion_descriptions.json (21 fusion hasil Joint LoRA SDXL).
Fitur: search client-side, tidak load model AI.

Output:
  showcase/
    index.html
    styles.css
    metadata.json
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
FUSION_JSON = SCRIPT_DIR / "fusion_descriptions.json"
OUTPUT_DIR = SCRIPT_DIR / "showcase"


def esc(text) -> str:
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def collect_unique_budaya(fusions) -> list:
    """Kumpulkan daftar budaya unik untuk isi dropdown."""
    budaya = set()
    for f in fusions:
        budaya.add(f.get("budaya_1", ""))
        budaya.add(f.get("budaya_2", ""))
    budaya.discard("")
    return sorted(budaya)


def build_search_blob(f: dict) -> str:
    """Teks yang dipakai untuk filter pencarian (lowercase)."""
    c1, c2 = f["ciri_daerah_1"], f["ciri_daerah_2"]
    parts = [
        f["budaya_1"], f["budaya_2"],
        f["judul"], f.get("subjudul", ""),
        f["trigger_1"], f["trigger_2"],
        f.get("filosofi_fusion", ""),
        f.get("penggunaan", ""),
        f.get("tema_prompt", ""),
        c1["nama"], c1.get("pulau", ""), c1.get("filosofi", ""),
        c1.get("elemen_utama", ""), c1.get("pola", ""),
        c2["nama"], c2.get("pulau", ""), c2.get("filosofi", ""),
        c2.get("elemen_utama", ""), c2.get("pola", ""),
    ] + c1.get("warna", []) + c1.get("motif", []) \
      + c2.get("warna", []) + c2.get("motif", [])
    return " ".join(parts).lower()


def render_compact_card(f: dict) -> str:
    """Render kartu fusion COMPACT untuk carousel (1 per view)."""
    fid = esc(f["id"])
    judul = esc(f["judul"])
    subjudul = esc(f.get("subjudul", ""))
    image = esc(f["image"])
    c1, c2 = f["ciri_daerah_1"], f["ciri_daerah_2"]

    return f"""
        <article class="carousel-item fusion-compact" id="card-{fid}" data-id="{fid}">
            <div class="compact-image">
                <img src="{image}" alt="{judul}" loading="lazy">
            </div>
            <div class="compact-body">
                <div class="compact-region">
                    <span class="region-tag region-1">{esc(f['budaya_1'])}</span>
                    <span class="cross">x</span>
                    <span class="region-tag region-2">{esc(f['budaya_2'])}</span>
                </div>
                <h3 class="compact-judul">{judul}</h3>
                <p class="compact-sub">{subjudul}</p>

                <div class="compact-triggers">
                    <code class="trigger-token">{esc(f['trigger_1'])}</code>
                    <span class="plus">+</span>
                    <code class="trigger-token">{esc(f['trigger_2'])}</code>
                </div>

                <details class="compact-detail">
                    <summary>Lihat Ciri Khas &amp; Filosofi</summary>
                    <div class="detail-grid">
                        <div class="detail-col">
                            <div class="detail-head">
                                <span class="detail-num">01</span>
                                <strong>{esc(c1['nama'])}</strong>
                                <span class="trigger-pill">{esc(c1.get('trigger',''))}</span>
                            </div>
                            <p class="filosofi"><em>{esc(c1.get('filosofi',''))}</em></p>
                            <p class="elemen">{esc(c1.get('elemen_utama',''))}</p>
                            <div class="chips">{''.join(f'<span class="chip chip-color">{esc(w)}</span>' for w in c1.get('warna',[]))}</div>
                            <div class="chips">{''.join(f'<span class="chip chip-motif">{esc(m)}</span>' for m in c1.get('motif',[]))}</div>
                        </div>
                        <div class="detail-col">
                            <div class="detail-head">
                                <span class="detail-num">02</span>
                                <strong>{esc(c2['nama'])}</strong>
                                <span class="trigger-pill">{esc(c2.get('trigger',''))}</span>
                            </div>
                            <p class="filosofi"><em>{esc(c2.get('filosofi',''))}</em></p>
                            <p class="elemen">{esc(c2.get('elemen_utama',''))}</p>
                            <div class="chips">{''.join(f'<span class="chip chip-color">{esc(w)}</span>' for w in c2.get('warna',[]))}</div>
                            <div class="chips">{''.join(f'<span class="chip chip-motif">{esc(m)}</span>' for m in c2.get('motif',[]))}</div>
                        </div>
                    </div>
                    <div class="compact-summary">
                        <div class="gradio-label">Filosofi Fusion</div>
                        <p>{esc(f.get('filosofi_fusion',''))}</p>
                        <div class="gradio-label" style="margin-top:8px">Cocok untuk</div>
                        <p>{esc(f.get('penggunaan',''))}</p>
                    </div>
                </details>

                <button type="button" class="btn-pick" data-id="{fid}">Pilih Template Ini</button>
            </div>
        </article>
"""


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SiButik: Silang Budaya Batik - Generator Cultural Fusion Batik Nusantara</title>
<link rel="stylesheet" href="styles.css">
</head>
<body>

<div class="gradio-container">

    <header class="gradio-header">
        <div class="gradio-header-inner">
            <div class="brand">
                <span class="brand-mark">S</span>
                <div>
                    <h1>SiButik</h1>
                    <p class="brand-sub">Silang Budaya Batik &mdash; Generator Cultural Fusion Batik Nusantara</p>
                </div>
            </div>
            <p class="meta">
                SDXL + LoRA Joint Training
            </p>
        </div>
    </header>

    <main class="gradio-main">

        <!-- ============================== SECTION 1: GENERATOR ============================== -->
        <section class="section section-config">
            <header class="section-head">
                <span class="section-num">1</span>
                <div>
                    <h2>Generator</h2>
                    <p class="section-sub">Pilih budaya yang akan digabungkan dan tulis prompt sesuai keinginan.</p>
                </div>
            </header>

            <div class="gradio-row two-col">
                <div class="gradio-column">
                    <label class="gradio-label" for="budaya1">Budaya 1 <span class="hint">(wajib)</span></label>
                    <select id="budaya1" class="gradio-select">
                        <option value="">&mdash; Pilih budaya pertama &mdash;</option>
                        {budaya_options}
                    </select>
                </div>
                <div class="gradio-column">
                    <label class="gradio-label" for="budaya2">Budaya 2 <span class="hint">(opsional &mdash; kosong = 1 budaya)</span></label>
                    <select id="budaya2" class="gradio-select">
                        <option value="">&mdash; Kosong / 1 budaya saja &mdash;</option>
                        {budaya_options}
                    </select>
                </div>
            </div>

            <div class="gradio-column">
                <label class="gradio-label" for="promptInput">Prompt <span class="hint">(opsional, untuk filter tambahan)</span></label>
                <textarea id="promptInput" class="gradio-textarea" rows="3"
                          placeholder="mis. batik perpaduan madura jawa timur, latar navy gelap dengan floral sprigs dan vines yang saling terkait..."></textarea>
            </div>
        </section>

        <!-- ============================== SECTION 2: TEMPLATE CAROUSEL ============================== -->
        <section class="section section-template">
            <header class="section-head">
                <span class="section-num">2</span>
                <div>
                    <h2>Template Hasil</h2>
                    <p class="section-sub">Scroll atau gunakan tombol untuk melihat template fusion. Klik "Pilih Template Ini" untuk dibawa ke langkah berikutnya.</p>
                </div>
            </header>

            <div class="carousel-status" id="carouselStatus">
                <span id="resultInfo">Menampilkan semua {total} template</span>
            </div>

            <div class="carousel-wrapper">
                <button type="button" class="carousel-nav prev" id="carouselPrev" aria-label="Sebelumnya">&lsaquo;</button>
                <div class="carousel" id="carousel">
                    {cards}
                </div>
                <button type="button" class="carousel-nav next" id="carouselNext" aria-label="Berikutnya">&rsaquo;</button>
            </div>

            <div class="carousel-dots" id="carouselDots"></div>
        </section>

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

    </main>

    <footer class="gradio-footer">
        <p><b>SiButik</b> &mdash; Silang Budaya Batik &mdash; Generator Cultural Fusion Batik Nusantara</p>
        <small>SDXL + LoRA Joint Training (kohya-ss) &mdash; demo statis, tanpa inference</small>
    </footer>

</div>

<script>
(function () {{
    // ====================== DATA ======================
    const fusions = {fusions_json};

    // ====================== FILTER LOGIC ======================
    const budaya1Sel = document.getElementById('budaya1');
    const budaya2Sel = document.getElementById('budaya2');
    const promptInput = document.getElementById('promptInput');
    const resultInfo = document.getElementById('resultInfo');

    function tokenize(s) {{
        return (s || '').toLowerCase()
            .replace(/[{{}}()'"`~!@#$%^&*+=:;,.<>/?\\|_-]/g, ' ')
            .split(/\\s+/)
            .filter(function (t) {{
                return t.length >= 2
                    && !/^(?:triggers|class_name|class|pattern|fabric|batik|style|textile|design|motif|color|colour|background|composition)$/i.test(t);
            }});
    }}

    function getFilteredAndScored() {{
        const b1 = budaya1Sel.value;
        const b2 = budaya2Sel.value;
        const promptTokens = tokenize(promptInput.value);

        const items = fusions.map(function (f) {{
            const blob = (f.search_blob || '');
            let score = 0;
            let matched = true;

            // Filter budaya 1
            if (b1) {{
                if (f.budaya_1 !== b1 && f.budaya_2 !== b1) matched = false;
                else score += 5;
            }}

            // Filter budaya 2 (kalau dipilih)
            if (b2) {{
                if (f.budaya_1 !== b2 && f.budaya_2 !== b2) matched = false;
                else score += 5;
            }}

            // Prompt keywords (OR scoring)
            promptTokens.forEach(function (t) {{
                if (blob.indexOf(t) !== -1) {{
                    score += 1;
                }} else {{
                    // token tidak match = penalty kecil (bukan deal-breaker)
                    score -= 0.5;
                }}
            }});

            return {{ fusion: f, score: score, matched: matched }};
        }})
        .filter(function (x) {{ return x.matched; }})
        .sort(function (a, b) {{ return b.score - a.score; }});

        return items.map(function (x) {{ return x.fusion; }});
    }}

    // ====================== CAROUSEL ======================
    const carousel = document.getElementById('carousel');
    const prevBtn = document.getElementById('carouselPrev');
    const nextBtn = document.getElementById('carouselNext');
    const dotsBox = document.getElementById('carouselDots');
    const cardsAll = Array.from(document.querySelectorAll('.carousel-item'));
    let currentIndex = 0;

    function getVisibleCards() {{
        return cardsAll.filter(function (c) {{
            return !c.classList.contains('is-hidden')
                && !c.classList.contains('is-filtered');
        }});
    }}

    function updateCarousel() {{
        const visible = getVisibleCards();

        // Hide cards yang ke-filter; sisakan yang visible
        cardsAll.forEach(function (c) {{
            const shouldShow = !c.classList.contains('is-filtered');
            c.classList.toggle('is-hidden', !shouldShow);
        }});

        // Update info
        if (visible.length === 0) {{
            resultInfo.textContent = 'Tidak ada template yang cocok dengan filter.';
            prevBtn.disabled = true;
            nextBtn.disabled = true;
        }} else {{
            resultInfo.textContent = 'Menampilkan ' + visible.length + ' template';
            prevBtn.disabled = false;
            nextBtn.disabled = false;
        }}

        // Update dots
        dotsBox.innerHTML = visible.map(function (_, i) {{
            return '<button type="button" class="dot" data-i="' + i + '" aria-label="Template ' + (i + 1) + '"></button>';
        }}).join('');
        Array.from(dotsBox.querySelectorAll('.dot')).forEach(function (d) {{
            d.addEventListener('click', function () {{
                scrollToIndex(parseInt(d.dataset.i, 10));
            }});
        }});

        currentIndex = 0;
        updateDotsHighlight();
    }}

    function scrollToIndex(i) {{
        const visible = getVisibleCards();
        if (i < 0) i = 0;
        if (i >= visible.length) i = visible.length - 1;
        currentIndex = i;
        if (visible[i]) {{
            visible[i].scrollIntoView({{ behavior: 'smooth', inline: 'start', block: 'nearest' }});
        }}
        updateDotsHighlight();
    }}

    function updateDotsHighlight() {{
        Array.from(dotsBox.querySelectorAll('.dot')).forEach(function (d, idx) {{
            d.classList.toggle('active', idx === currentIndex);
        }});
    }}

    prevBtn.addEventListener('click', function () {{ scrollToIndex(currentIndex - 1); }});
    nextBtn.addEventListener('click', function () {{ scrollToIndex(currentIndex + 1); }});

    // Horizontal scroll dengan mouse wheel
    carousel.addEventListener('wheel', function (e) {{
        // Hanya intercept vertical wheel (deltaY) dan ubah jadi horizontal scroll
        if (Math.abs(e.deltaY) > Math.abs(e.deltaX)) {{
            e.preventDefault();
            carousel.scrollLeft += e.deltaY;
        }}
    }}, {{ passive: false }});

    // Update currentIndex berdasarkan scroll position
    let scrollTimer = null;
    carousel.addEventListener('scroll', function () {{
        if (scrollTimer) clearTimeout(scrollTimer);
        scrollTimer = setTimeout(function () {{
            const visible = getVisibleCards();
            const carouselRect = carousel.getBoundingClientRect();
            let nearest = 0;
            let nearestDist = Infinity;
            visible.forEach(function (c, i) {{
                const r = c.getBoundingClientRect();
                const dist = Math.abs(r.left - carouselRect.left);
                if (dist < nearestDist) {{ nearestDist = dist; nearest = i; }}
            }});
            currentIndex = nearest;
            updateDotsHighlight();
        }}, 80);
    }});

    // Keyboard navigation saat carousel focus
    carousel.addEventListener('keydown', function (e) {{
        if (e.key === 'ArrowLeft') {{ e.preventDefault(); scrollToIndex(currentIndex - 1); }}
        else if (e.key === 'ArrowRight') {{ e.preventDefault(); scrollToIndex(currentIndex + 1); }}
    }});

    // ====================== FILTER EVENTS ======================
    function applyFilters() {{
        // Simpan data blob ke dataset kalau belum
        cardsAll.forEach(function (c) {{
            if (!c.dataset.search) {{
                // cari blob dari fusions
                const id = c.dataset.id;
                const f = fusions.find(function (x) {{ return x.id === id; }});
                if (f) c.dataset.search = f.search_blob;
            }}
        }});

        const b1 = budaya1Sel.value;
        const b2 = budaya2Sel.value;
        const promptTokens = tokenize(promptInput.value);

        cardsAll.forEach(function (card) {{
            const f = fusions.find(function (x) {{ return x.id === card.dataset.id; }});
            if (!f) return;
            let visible = true;
            if (b1 && f.budaya_1 !== b1 && f.budaya_2 !== b1) visible = false;
            if (b2 && f.budaya_1 !== b2 && f.budaya_2 !== b2) visible = false;
            // prompt: tampilkan kalau ada token match, atau kalau prompt kosong
            if (promptTokens.length > 0 && visible) {{
                const blob = f.search_blob || '';
                const anyMatch = promptTokens.some(function (t) {{ return blob.indexOf(t) !== -1; }});
                if (!anyMatch) visible = false;
            }}
            card.classList.toggle('is-filtered', !visible);
        }});

        updateCarousel();
    }}

    budaya1Sel.addEventListener('change', applyFilters);
    budaya2Sel.addEventListener('change', applyFilters);
    promptInput.addEventListener('input', applyFilters);

    // ====================== PICK & APPLY ======================
    const applyBtn = document.getElementById('applyBtn');
    const applyPlaceholder = document.getElementById('applyPlaceholder');
    const applyResult = document.getElementById('applyResult');
    const applyImage = document.getElementById('applyImage');
    const applyTitle = document.getElementById('applyTitle');
    const applyTriggers = document.getElementById('applyTriggers');
    const applyNote = document.getElementById('applyNote');
    let selectedFusion = null;

    document.querySelectorAll('.btn-pick').forEach(function (btn) {{
        btn.addEventListener('click', function () {{
            const id = btn.dataset.id;
            selectedFusion = fusions.find(function (f) {{ return f.id === id; }});
            if (!selectedFusion) return;

            // Highlight picked card
            cardsAll.forEach(function (c) {{ c.classList.remove('is-picked'); }});
            const card = document.getElementById('card-' + id);
            if (card) card.classList.add('is-picked');

            // Update apply section
            applyImage.src = selectedFusion.image;
            applyImage.alt = selectedFusion.judul;
            applyTitle.textContent = selectedFusion.judul;
            applyTriggers.textContent = selectedFusion.trigger_1 + ' + ' + selectedFusion.trigger_2;
            applyPlaceholder.hidden = true;
            applyResult.hidden = false;
            applyBtn.disabled = false;
            applyNote.innerHTML = '<b>Siap diterapkan.</b> Pada aplikasi Gradio interaktif, simulasi memakai segmentasi area pakaian (rembg u2net_cloth_seg) + Feathered Seams tiling.';

            // Smooth scroll ke section apply
            document.querySelector('.section-apply').scrollIntoView({{ behavior: 'smooth', block: 'start' }});
        }});
    }});

    applyBtn.addEventListener('click', function () {{
        if (!selectedFusion) return;
        applyBtn.classList.add('is-loading');
        applyBtn.disabled = true;
        const origHtml = applyBtn.innerHTML;
        applyBtn.innerHTML = 'Memproses...';
        setTimeout(function () {{
            applyBtn.classList.remove('is-loading');
            applyBtn.disabled = false;
            applyBtn.innerHTML = origHtml;
            applyNote.innerHTML = '<b>Simulasi selesai (demo).</b> Hasil akhir dapat dilihat lengkap di aplikasi Gradio interaktif (<code>app.py</code>).';
        }}, 900);
    }});

    // ====================== INIT ======================
    applyFilters();
}})();
</script>

</body>
</html>
"""


CSS = r"""/* SiButik - Silang Budaya Batik - Pastel dark theme */

:root {
    --bg: #1a1612;
    --surface: #221d18;
    --card: #2c2620;
    --elevated: #352e28;
    --deeper: #13100d;
    --border: #423b35;
    --border-subtle: #322c26;
    --text: #f5ead7;
    --text-soft: #d9cbb5;
    --text-mute: #9d8e7a;
    --text-faint: #6b5f52;
    --accent: #f4a261;
    --accent-bright: #ffd6a5;
    --accent-soft: rgba(244, 162, 97, 0.15);
    --accent-glow: rgba(244, 162, 97, 0.22);
    --region-1: #f4978e;
    --region-1-text: #4a2820;
    --region-2: #a8d8ea;
    --region-2-text: #1a3a4a;
    --sage-soft: rgba(168, 213, 178, 0.18);
    --sage-text: #b8e0c4;
    --sage-border: rgba(168, 213, 178, 0.3);
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html { scroll-behavior: smooth; }

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
    min-height: 100vh;
    color-scheme: dark;
}

.gradio-container {
    max-width: 1400px;
    margin: 0 auto;
    background: var(--bg);
}

/* ===================== HEADER ===================== */
.gradio-header {
    background:
        radial-gradient(ellipse at top left, rgba(244, 162, 97, 0.08), transparent 50%),
        radial-gradient(ellipse at bottom right, rgba(168, 213, 178, 0.05), transparent 50%),
        linear-gradient(135deg, var(--surface) 0%, var(--card) 50%, var(--surface) 100%);
    padding: 24px 32px;
    border-bottom: 1px solid var(--border);
}
.gradio-header-inner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 24px;
    flex-wrap: wrap;
}
.brand {
    display: flex;
    align-items: center;
    gap: 14px;
}
.brand-mark {
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, #ffd6a5 0%, #f4a261 100%);
    color: var(--deeper);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    font-weight: 800;
    font-family: ui-serif, Georgia, serif;
    box-shadow: 0 0 18px rgba(244, 162, 97, 0.25);
}
.brand h1 {
    font-size: 1.5rem;
    color: var(--text);
    margin: 0;
    line-height: 1.2;
    letter-spacing: -0.01em;
}
.brand-sub {
    font-size: 0.85rem;
    color: var(--accent-bright);
    margin: 2px 0 0;
    font-weight: 500;
}
.meta {
    font-size: 0.82rem;
    color: var(--text-mute);
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
}
.badge-no-model {
    background: var(--accent-soft);
    color: var(--accent-bright);
    padding: 3px 10px;
    border-radius: 999px;
    font-weight: 600;
    font-size: 0.75rem;
    border: 1px solid rgba(244, 162, 97, 0.3);
}

/* ===================== MAIN ===================== */
.gradio-main {
    padding: 24px 32px 60px;
}

/* ===================== SECTION ===================== */
.section {
    background: var(--card);
    border: 1px solid var(--border-subtle);
    border-radius: 14px;
    padding: 20px 24px 24px;
    margin-bottom: 22px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.25);
}
.section-head {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 16px;
}
.section-num {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    background: linear-gradient(135deg, #ffd6a5 0%, #f4a261 100%);
    color: var(--deeper);
    border-radius: 999px;
    font-size: 0.92rem;
    font-weight: 800;
    font-family: ui-monospace, "SF Mono", Menlo, monospace;
    box-shadow: 0 0 12px rgba(244, 162, 97, 0.3);
    flex-shrink: 0;
}
.section-head h2 {
    font-size: 1.15rem;
    color: var(--text);
    margin: 2px 0 2px;
    font-weight: 700;
}
.section-sub {
    font-size: 0.85rem;
    color: var(--text-mute);
    margin: 0;
    line-height: 1.5;
}

/* ===================== GRID & ROW ===================== */
.gradio-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
    margin-bottom: 14px;
}
.gradio-row.two-col { grid-template-columns: 1fr 1fr; gap: 14px; }
.gradio-column {
    display: flex;
    flex-direction: column;
    gap: 6px;
}
@media (max-width: 760px) {
    .gradio-row, .gradio-row.two-col { grid-template-columns: 1fr; }
}

/* ===================== FORM ===================== */
.gradio-label {
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--text-soft);
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 4px;
}
.hint {
    color: var(--text-faint);
    font-weight: 400;
    text-transform: none;
    letter-spacing: 0;
    font-size: 0.78rem;
}
.gradio-select, .gradio-textarea {
    background: var(--elevated);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px 12px;
    font-size: 0.95rem;
    color: var(--text);
    font-family: inherit;
    width: 100%;
    transition: border-color 180ms, box-shadow 180ms;
}
.gradio-select:focus, .gradio-textarea:focus {
    outline: none;
    border-color: var(--accent);
    box-shadow: 0 0 0 3px var(--accent-glow);
}
.gradio-select {
    appearance: none;
    -webkit-appearance: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='14' height='14' viewBox='0 0 24 24' fill='none' stroke='%23a8a29e' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 12px center;
    padding-right: 36px;
}
.gradio-select option {
    background: var(--card);
    color: var(--text);
}
.gradio-textarea {
    resize: vertical;
    min-height: 64px;
    line-height: 1.5;
}

/* ===================== CAROUSEL ===================== */
.carousel-status {
    font-size: 0.85rem;
    color: var(--text-mute);
    margin-bottom: 12px;
    font-weight: 500;
}

.carousel-wrapper {
    position: relative;
    display: flex;
    align-items: center;
    gap: 10px;
}

.carousel {
    display: flex;
    overflow-x: auto;
    scroll-snap-type: x mandatory;
    scroll-behavior: smooth;
    scrollbar-width: none;
    -webkit-overflow-scrolling: touch;
    flex: 1;
    border-radius: 10px;
    background: var(--elevated);
    border: 1px solid var(--border-subtle);
    padding: 4px;
}
.carousel::-webkit-scrollbar { display: none; }

.carousel-item {
    flex: 0 0 100%;
    scroll-snap-align: start;
    display: flex;
    flex-direction: row;
    gap: 18px;
    padding: 18px;
    background: var(--card);
    border-radius: 8px;
    border: 1px solid var(--border-subtle);
    transition: border-color 200ms, box-shadow 200ms, transform 200ms;
    min-height: 280px;
}
.carousel-item.is-hidden,
.carousel-item.is-filtered { display: none; }
.carousel-item.is-picked {
    border-color: var(--accent);
    box-shadow: 0 0 0 2px var(--accent-glow);
}

.compact-image {
    flex: 0 0 280px;
    background: var(--surface);
    border-radius: 6px;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
}
.compact-image img {
    width: 100%;
    height: 100%;
    max-height: 260px;
    object-fit: cover;
    display: block;
}

.compact-body {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 8px;
    min-width: 0;
}
.compact-region {
    display: flex;
    align-items: center;
    gap: 8px;
}
.region-tag {
    font-size: 0.8rem;
    font-weight: 600;
    padding: 4px 12px;
    border-radius: 999px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
}
.region-1 { background: var(--region-1); color: var(--region-1-text); }
.region-2 { background: var(--region-2); color: var(--region-2-text); }
.cross {
    font-size: 1rem;
    color: var(--text-mute);
    font-weight: 700;
    font-family: ui-serif, Georgia, serif;
}
.compact-judul {
    font-size: 1.2rem;
    color: var(--text);
    margin: 0;
    line-height: 1.25;
}
.compact-sub {
    font-size: 0.88rem;
    color: var(--text-mute);
    font-style: italic;
    margin: 0;
}
.compact-triggers {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-top: 4px;
}
.trigger-token {
    background: var(--surface);
    color: var(--accent-bright);
    padding: 3px 8px;
    border-radius: 5px;
    font-size: 0.78rem;
    font-family: ui-monospace, "SF Mono", Menlo, monospace;
    border: 1px solid var(--border);
}
.plus { color: var(--accent); font-weight: 700; }

.compact-detail {
    margin-top: 6px;
    background: var(--surface);
    border: 1px solid var(--border-subtle);
    border-radius: 6px;
    padding: 8px 12px;
}
.compact-detail summary {
    cursor: pointer;
    color: var(--accent-bright);
    font-size: 0.85rem;
    font-weight: 600;
    list-style: none;
    user-select: none;
}
.compact-detail summary::-webkit-details-marker { display: none; }
.compact-detail summary::before {
    content: '+ ';
    color: var(--accent);
    font-weight: 800;
}
.compact-detail[open] summary::before { content: '- '; }
.compact-detail[open] { padding: 12px; }

.detail-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-top: 12px;
}
.detail-col {
    background: var(--bg);
    border: 1px solid var(--border-subtle);
    border-radius: 6px;
    padding: 10px 12px;
}
.detail-head {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 6px;
}
.detail-num {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 22px;
    height: 22px;
    background: linear-gradient(135deg, #ffd6a5 0%, #f4a261 100%);
    color: var(--deeper);
    border-radius: 999px;
    font-size: 0.7rem;
    font-weight: 800;
    font-family: ui-monospace, "SF Mono", Menlo, monospace;
}
.detail-head strong {
    font-size: 0.9rem;
    color: var(--text);
    flex: 1;
}
.trigger-pill {
    background: var(--card);
    color: var(--accent-bright);
    padding: 2px 7px;
    border-radius: 999px;
    font-size: 0.66rem;
    font-family: ui-monospace, "SF Mono", Menlo, monospace;
    font-weight: 600;
    border: 1px solid var(--border);
}
.filosofi {
    color: var(--accent-bright);
    font-size: 0.84rem;
    margin-bottom: 4px;
    line-height: 1.4;
}
.elemen {
    color: var(--text-soft);
    font-size: 0.82rem;
    margin-bottom: 8px;
    line-height: 1.5;
}
.chips {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    margin-bottom: 6px;
}
.chip {
    padding: 2px 8px;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 500;
    line-height: 1.5;
}
.chip-color {
    background: rgba(244, 162, 97, 0.18);
    color: var(--accent-bright);
    border: 1px solid rgba(244, 162, 97, 0.3);
}
.chip-motif {
    background: var(--sage-soft);
    color: var(--sage-text);
    border: 1px solid var(--sage-border);
}

.compact-summary {
    margin-top: 12px;
    padding: 10px 12px;
    background: var(--bg);
    border: 1px solid rgba(244, 162, 97, 0.22);
    border-left: 3px solid var(--accent);
    border-radius: 6px;
}
.compact-summary .gradio-label {
    color: var(--accent);
    font-size: 0.74rem;
}
.compact-summary p {
    color: var(--text);
    font-size: 0.84rem;
    line-height: 1.5;
    margin-top: 2px;
}

.btn-pick {
    align-self: flex-start;
    margin-top: 6px;
    background: var(--accent-soft);
    color: var(--accent-bright);
    border: 1px solid rgba(244, 162, 97, 0.35);
    padding: 7px 16px;
    border-radius: 6px;
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 180ms;
    font-family: inherit;
}
.btn-pick:hover {
    background: var(--accent);
    color: var(--deeper);
    border-color: var(--accent);
}

/* Carousel nav */
.carousel-nav {
    background: var(--card);
    border: 1px solid var(--border);
    color: var(--text-soft);
    border-radius: 50%;
    width: 38px;
    height: 38px;
    font-size: 1.4rem;
    line-height: 1;
    cursor: pointer;
    transition: all 180ms;
    flex-shrink: 0;
    font-family: inherit;
    display: flex;
    align-items: center;
    justify-content: center;
}
.carousel-nav:hover:not(:disabled) {
    background: var(--accent);
    color: var(--deeper);
    border-color: var(--accent);
}
.carousel-nav:disabled {
    opacity: 0.3;
    cursor: not-allowed;
}

/* Dots */
.carousel-dots {
    display: flex;
    justify-content: center;
    gap: 6px;
    margin-top: 12px;
    flex-wrap: wrap;
}
.dot {
    background: var(--border);
    border: none;
    width: 8px;
    height: 8px;
    border-radius: 999px;
    cursor: pointer;
    padding: 0;
    transition: all 180ms;
}
.dot:hover { background: var(--text-mute); }
.dot.active {
    background: var(--accent);
    width: 22px;
}

/* ===================== APPLY SECTION ===================== */
.apply-panel {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 18px;
    align-items: stretch;
}
@media (max-width: 760px) {
    .apply-panel { grid-template-columns: 1fr; }
}

.apply-preview {
    background: var(--elevated);
    border: 1px solid var(--border-subtle);
    border-radius: 10px;
    padding: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 240px;
    overflow: hidden;
}

.apply-placeholder {
    text-align: center;
    color: var(--text-mute);
}
.apply-placeholder svg { color: var(--text-faint); margin-bottom: 8px; }
.apply-placeholder p {
    font-size: 0.95rem;
    color: var(--text-soft);
    margin: 4px 0;
}
.apply-placeholder small {
    font-size: 0.8rem;
    color: var(--text-faint);
}

.apply-result {
    position: relative;
    width: 100%;
    height: 100%;
}
.apply-result img {
    width: 100%;
    height: 100%;
    max-height: 320px;
    object-fit: cover;
    border-radius: 6px;
    display: block;
}
.apply-overlay {
    position: absolute;
    bottom: 10px;
    left: 10px;
    right: 10px;
    background: rgba(19, 16, 13, 0.78);
    backdrop-filter: blur(6px);
    color: var(--text);
    padding: 10px 14px;
    border-radius: 6px;
    border: 1px solid rgba(244, 162, 97, 0.3);
    display: flex;
    flex-direction: column;
    gap: 4px;
}
.apply-overlay strong {
    color: var(--accent-bright);
    font-size: 0.95rem;
}
.apply-overlay span {
    color: var(--text-mute);
    font-size: 0.78rem;
    font-family: ui-monospace, "SF Mono", Menlo, monospace;
}

.apply-action {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    gap: 14px;
}

.btn-apply {
    background: linear-gradient(135deg, #ffd6a5 0%, #f4a261 100%);
    color: var(--deeper);
    border: none;
    padding: 14px 20px;
    border-radius: 8px;
    font-size: 0.95rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 180ms;
    font-family: inherit;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    box-shadow: 0 4px 14px rgba(244, 162, 97, 0.25);
}
.btn-apply:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 6px 18px rgba(244, 162, 97, 0.35);
}
.btn-apply:disabled {
    opacity: 0.4;
    cursor: not-allowed;
    box-shadow: none;
}
.btn-apply.is-loading { animation: pulse 1.2s ease-in-out infinite; }
@keyframes pulse {
    0%, 100% { opacity: 0.6; }
    50% { opacity: 1; }
}

.apply-note {
    font-size: 0.82rem;
    color: var(--text-mute);
    line-height: 1.55;
    background: var(--surface);
    border: 1px solid var(--border-subtle);
    border-left: 3px solid var(--accent);
    padding: 10px 12px;
    border-radius: 6px;
}
.apply-note b { color: var(--accent-bright); }
.apply-note code {
    background: var(--elevated);
    color: var(--accent-bright);
    padding: 1px 5px;
    border-radius: 3px;
    font-family: ui-monospace, "SF Mono", Menlo, monospace;
    font-size: 0.86em;
    border: 1px solid var(--border-subtle);
}

/* ===================== FOOTER ===================== */
.gradio-footer {
    background: var(--surface);
    border-top: 1px solid var(--border);
    text-align: center;
    padding: 18px 32px;
    color: var(--text-soft);
}
.gradio-footer p {
    font-weight: 600;
    margin-bottom: 2px;
    color: var(--accent-bright);
    font-size: 0.92rem;
}
.gradio-footer small {
    color: var(--text-mute);
    font-size: 0.78rem;
}

/* ===================== RESPONSIVE ===================== */
@media (max-width: 760px) {
    .gradio-header, .gradio-main { padding-left: 16px; padding-right: 16px; }
    .brand h1 { font-size: 1.25rem; }
    .section { padding: 16px; }
    .carousel-item {
        flex-direction: column;
        padding: 14px;
        min-height: 0;
    }
    .compact-image {
        flex: 0 0 auto;
        max-height: 220px;
    }
    .detail-grid { grid-template-columns: 1fr; }
    .carousel-nav { width: 32px; height: 32px; font-size: 1.2rem; }
}
"""


def generate():
    """Bangun showcase/index.html + styles.css dari fusion_descriptions.json."""
    if not FUSION_JSON.exists():
        raise FileNotFoundError(f"{FUSION_JSON} tidak ditemukan.")

    data = json.loads(FUSION_JSON.read_text(encoding="utf-8"))
    fusions = data.get("fusions", [])
    if not fusions:
        raise ValueError("fusion_descriptions.json tidak berisi entri 'fusions'.")

    # Tidak ada exclude - semua 21+ fusion dari joint LoRA training ditampilkan
    fusions = fusions

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Inject search_blob & raw data untuk JS
    fusions_with_blob = []
    for f in fusions:
        ff = dict(f)
        ff["search_blob"] = build_search_blob(f)
        fusions_with_blob.append(ff)

    # Build dropdown options
    budaya_list = collect_unique_budaya(fusions)
    budaya_options = "\n".join(
        f'                        <option value="{esc(b)}">{esc(b)}</option>'
        for b in budaya_list
    )

    cards_html = "\n".join(render_compact_card(f) for f in fusions)

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    # Strip search_blob dari fusions yang di-render ke HTML (hanya perlu di JS)
    html = HTML_TEMPLATE.format(
        cards=cards_html,
        total=len(fusions),
        generated_at=generated_at,
        trigger="<nama_daerah>",
        budaya_options=budaya_options,
        fusions_json=json.dumps(fusions_with_blob, ensure_ascii=False),
    )

    (OUTPUT_DIR / "index.html").write_text(html, encoding="utf-8")
    (OUTPUT_DIR / "styles.css").write_text(CSS, encoding="utf-8")

    metadata = {
        "generated_at": generated_at,
        "total_pairs": len(fusions),
        "success": len(fusions),
        "failed": 0,
        "lora_source": "madura-madura_pola_kompleks-joint-lora-000001",
        "entries": [
            {
                "id": f["id"],
                "judul": f["judul"],
                "image": f["image"],
                "trigger_1": f["trigger_1"],
                "trigger_2": f["trigger_2"],
                "prompt": f"a {f['trigger_1']} {f['trigger_2']} batik pattern, fusion of {f['budaya_1']} and {f['budaya_2']}",
            }
            for f in fusions
        ],
    }
    (OUTPUT_DIR / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"[OK] SiButik showcase digenerate.")
    print(f"     - {OUTPUT_DIR / 'index.html'}")
    print(f"     - {OUTPUT_DIR / 'styles.css'}")
    print(f"     - {OUTPUT_DIR / 'metadata.json'}")
    print(f"     Total entri: {len(fusions)}")
    print(f"     Budaya unik: {len(budaya_list)}")


if __name__ == "__main__":
    generate()