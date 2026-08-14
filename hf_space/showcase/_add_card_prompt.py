#!/usr/bin/env python
"""Restructure carousel cards:
1. Kecilkan image (compact-image ~180px)
2. Tambahkan prompt di compact-body (di bawah judul)
Prompt dibangun dari FUSION_DESCRIPTIONS notebook.
"""
import re
from pathlib import Path

FILE = Path(r"d:\Riset MBKM\model results\Batik_Re-Palette\showcase\index.html")
txt = FILE.read_text(encoding="utf-8")

# Mapping: data-id -> (region_a, region_b)
# Catatan: "madura_klasik" di data-id dipetakan ke "madura" di FUSION_DESCRIPTIONS
CARDS_MAP = {
    "fusion_yogyakarta_madura_pola_sederhana": ("yogyakarta", "madura_pola_sederhana"),
    "fusion_yogyakarta_madura_pola_kompleks": ("yogyakarta", "madura_pola_kompleks"),
    "fusion_yogyakarta_madura_klasik": ("yogyakarta", "madura"),
    "fusion_yogyakarta_jawa_timur": ("yogyakarta", "jawa_timur"),
    "fusion_yogyakarta_jawa_tengah": ("yogyakarta", "jawa_tengah"),
    "fusion_yogyakarta_jawa_barat": ("yogyakarta", "jawa_barat"),
    "fusion_madura_pola_sederhana_madura_pola_kompleks": ("madura_pola_sederhana", "madura_pola_kompleks"),
    "fusion_madura_pola_sederhana_madura_klasik": ("madura_pola_sederhana", "madura"),
    "fusion_madura_pola_sederhana_jawa_timur": ("madura_pola_sederhana", "jawa_timur"),
    "fusion_madura_pola_sederhana_jawa_tengah": ("madura_pola_sederhana", "jawa_tengah"),
}

# FUSION_DESCRIPTIONS (copy dari notebook)
FUSION_DESCRIPTIONS = {
    ("yogyakarta", "madura_pola_sederhana"):
        "Rich red fabric overlaid with a uniform grid of cream circular medallions, interspersed with bold golden-yellow floral sprigs and flowing vines.",
    ("yogyakarta", "madura_pola_kompleks"):
        "Deep red and green fabric with a dense grid of cream circular medallions, layered beneath vibrant floral sprigs, swirling leaves, and butterflies.",
    ("yogyakarta", "madura"):
        "Dark navy fabric with a uniform grid of cream circular medallions, accented by stylized floral sprigs, birds, and scattered white dot clusters.",
    ("yogyakarta", "jawa_timur"):
        "Dark background densely patterned with cream and gold circular medallions, interwoven with stylized tropical birds, bamboo stalks, and warm floral sprigs.",
    ("yogyakarta", "jawa_tengah"):
        "Dark brown fabric combining a uniform grid of cream circular medallions with flowing abstract swirls and small geometric accents in gold and beige.",
    ("yogyakarta", "jawa_barat"):
        "Deep navy fabric where a dense grid of cream circular medallions meets flowing gold cloud-like swirls, blending geometric precision with soft wave-like motion.",
    ("madura_pola_sederhana", "madura_pola_kompleks"):
        "Rich red fabric dense with bold golden-yellow floral sprigs and blossoms, layered beneath vibrant swirling leaves and butterflies in teal and orange.",
    ("madura_pola_sederhana", "madura"):
        "Dark navy fabric scattered with bold golden-yellow floral sprigs and blossoms, accented by cream stylized birds and clusters of small white dots.",
    ("madura_pola_sederhana", "jawa_timur"):
        "Rich red fabric dense with golden-yellow floral sprigs and flowing vines, interwoven with stylized tropical birds and slender bamboo stalks.",
    ("madura_pola_sederhana", "jawa_tengah"):
        "Dark brown fabric blending bold golden-yellow floral sprigs and blossoms with flowing abstract swirls and small geometric accents in cream.",
    ("madura_pola_sederhana", "jawa_barat"):
        "Deep navy fabric with flowing gold cloud-like swirls intertwined with bold golden-yellow floral sprigs and blossoms in a dense, high-contrast layout.",
}

def build_prompt(a, b, desc):
    return f"a {a}batik {b}batik batik pattern, {desc}"

# Untuk setiap card di carousel, tambahkan <p class="card-prompt">PROMPT</p>
# Pattern: cari <h3 class="compact-judul">TITLE</h3> lalu tambahkan prompt setelahnya

def replace_card(match):
    card_html = match.group(0)
    # Cari data-id
    id_match = re.search(r'data-id="([^"]+)"', card_html)
    if not id_match:
        return card_html
    data_id = id_match.group(1)
    if data_id not in CARDS_MAP:
        return card_html
    a, b = CARDS_MAP[data_id]
    # Cari deskripsi
    desc = FUSION_DESCRIPTIONS.get((a, b))
    if not desc:
        return card_html
    prompt = build_prompt(a, b, desc)
    # Sisipkan prompt setelah compact-judul (sebelum penutup compact-body)
    prompt_html = f'\n                <p class="card-prompt">{prompt}</p>'
    # Cari </h3> lalu tambahkan prompt_html
    return card_html.replace('</h3>', '</h3>' + prompt_html, 1)

# Proses setiap <article class="carousel-item fusion-compact">...</article>
card_re = re.compile(
    r'<article class="carousel-item fusion-compact"[^>]*>.*?</article>',
    re.DOTALL,
)
txt = card_re.sub(replace_card, txt)

FILE.write_text(txt, encoding="utf-8")
print("Selesai. Panjang:", len(txt))