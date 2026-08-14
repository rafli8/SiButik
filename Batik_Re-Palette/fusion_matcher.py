# -*- coding: utf-8 -*-
"""
fusion_matcher.py
=================
Smart matcher untuk mencocokkan prompt user dengan database fusion.
- Kalau cocok: pakai gambar & deskripsi yang sudah ada (no model load)
- Kalau tidak cocok: fallback ke generator model (SDXL + LoRA)
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, Optional, Tuple


FUSION_DB_PATH = Path(__file__).resolve().parent / "fusion_descriptions.json"


def _load_fusion_db() -> Dict:
    """Load database fusion dari JSON."""
    if not FUSION_DB_PATH.exists():
        return {"fusions": []}
    with open(FUSION_DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _normalize_name(name: str) -> str:
    """Normalisasi nama daerah: lowercase, underscore, no spaces."""
    if not name:
        return ""
    n = name.lower().strip()
    alias = {
        "madura": "madura",
        "madura_pola_kompleks": "madura_pola_kompleks",
        "madura_pola_sederhana": "madura_pola_sederhana",
        "jawa barat": "jawa_barat",
        "jawa_barat": "jawa_barat",
        "sunda": "jawa_barat",
        "jawa tengah": "jawa_tengah",
        "jawa_tengah": "jawa_tengah",
        "jawa timur": "jawa_timur",
        "jawa_timur": "jawa_timur",
        "jogja": "yogyakarta",
        "yogyakarta": "yogyakarta",
        "yogya": "yogyakarta",
        "solo": "jawa_tengah",
        "surakarta": "jawa_tengah",
        "bali": "bali",
        "dayak": "kalimantan",
        "kalimantan": "kalimantan",
        "borneo": "kalimantan",
        "bugis": "sulawesi",
        "makassar": "sulawesi",
        "sulawesi": "sulawesi",
        "papua": "papua",
        "minang": "sumatera",
        "minangkabau": "sumatera",
        "batak": "sumatera",
        "sumatera": "sumatera",
        "ntt": "nusa_tenggara",
        "ntb": "nusa_tenggara",
        "nusa tenggara": "nusa_tenggara",
        "nusa_tenggara": "nusa_tenggara",
        "flores": "nusa_tenggara",
        "jawa": "jawa_tengah",
    }
    n = n.replace("-", "_").replace(" ", "_")
    return alias.get(n, n)


def _parse_prompt(prompt: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract budaya_1 & budaya_2 dari prompt.
    Cari pola: 'a {trigger1} {trigger2} batik pattern, ...'
    """
    if not prompt:
        return None, None

    # Cari token batik (e.g., madurabatik, jawa_baratbatik)
    triggers = re.findall(r"\b([a-z_]+)batik\b", prompt.lower())
    if len(triggers) >= 2:
        return _normalize_name(triggers[0].replace("batik", "")), _normalize_name(triggers[1].replace("batik", ""))

    # Fallback: cari nama daerah langsung
    known_regions = [
        "madura_pola_kompleks", "madura_pola_sederhana", "madura",
        "jawa_barat", "jawa_tengah", "jawa_timur", "yogyakarta",
        "bali", "kalimantan", "sulawesi", "papua",
        "sumatera", "nusa_tenggara", "solo",
    ]
    found = []
    for region in sorted(known_regions, key=len, reverse=True):
        if region in prompt.lower() and region not in found:
            found.append(region)
        if len(found) >= 2:
            break
    if len(found) >= 2:
        return _normalize_name(found[0]), _normalize_name(found[1])
    if len(found) == 1:
        return _normalize_name(found[0]), None
    return None, None


def _build_fusion_id(budaya_1: str, budaya_2: str, db: Dict) -> Optional[Dict]:
    """Cari fusion di database yang cocok dengan budaya_1 & budaya_2."""
    if not budaya_1 or not budaya_2:
        return None
    b1, b2 = _normalize_name(budaya_1), _normalize_name(budaya_2)

    for f in db.get("fusions", []):
        fb1 = _normalize_name(f["budaya_1"])
        fb2 = _normalize_name(f["budaya_2"])

        # Exact match
        if (fb1 == b1 and fb2 == b2) or (fb1 == b2 and fb2 == b1):
            return f

        # Special case: Solo Heritage selalu solo
        if f["id"] == "solo" and (b1 == "solo" or b2 == "solo"):
            return f
        if f["id"] == "solo" and (b1 == "jawa_tengah" or b2 == "jawa_tengah"):
            # Solo Heritage mengandung jawa_tengah
            return f

        # Partial match: nama daerah parsed adalah substring dari nama di DB
        # e.g. "jawa_barat" adalah bagian dari "jawa_barat_(awan_emas)"
        if ((b1 in fb1 or fb1 in b1) and (b2 in fb2 or fb2 in b2)) or \
           ((b1 in fb2 or fb2 in b1) and (b2 in fb1 or fb1 in b2)):
            return f

    return None


def cari_fusion_dari_prompt(
    prompt: str = "",
    budaya_1: str = "",
    budaya_2: str = "",
) -> Tuple[Optional[Dict], float, str]:
    """
    Cari fusion yang cocok. Returns:
        (fusion_dict or None, confidence_score, mode)
        - mode: "matched" kalau ada, "not_found" kalau tidak
    """
    db = _load_fusion_db()
    if not db.get("fusions"):
        return None, 0.0, "not_found"

    # 1. User kasih nama daerah eksplisit
    if budaya_1 and budaya_2:
        f = _build_fusion_id(budaya_1, budaya_2, db)
        if f:
            return f, 1.0, "matched"
        return None, 0.0, "not_found"

    # 2. Parse prompt
    if prompt:
        b1, b2 = _parse_prompt(prompt)
        if b1 and b2:
            f = _build_fusion_id(b1, b2, db)
            if f:
                return f, 1.0, "matched"
            # Kalau 2 daerah tapi tidak ada di DB, return not_found
            return None, 0.0, "not_found"
        elif b1 or b2:
            # Partial match: hanya 1 daerah yg kedeteksi
            # Cari fusion yang mengandung daerah tsb
            target = b1 or b2
            candidates = []
            for f in db.get("fusions", []):
                fb1 = _normalize_name(f["budaya_1"])
                fb2 = _normalize_name(f["budaya_2"])
                if fb1 == target or fb2 == target:
                    candidates.append(f)
            # Kalau ada beberapa, pilih yang beda-beda jenisnya
            # (e.g. madura_jawa_barat_emas beda dari madura_jawa_barat_biru)
            # Default: kembalikan yg pertama
            if candidates:
                # Kalau ada multiple madura_*, ambil yg punya jawa_tengah (default)
                if len(candidates) > 1:
                    for c in candidates:
                        fb2 = _normalize_name(c["budaya_2"])
                        if fb2 not in ("jawa_barat",):
                            return c, 0.6, "matched"
                return candidates[0], 0.6, "matched"
            return None, 0.0, "not_found"

    return None, 0.0, "not_found"


def fusion_ke_markdown(fusion: Dict) -> str:
    """Convert fusion dict ke markdown (untuk app.py)."""
    if not fusion:
        return "_(Fusion tidak ditemukan)_"

    md = f"""### {fusion['judul']}

_{fusion['subjudul']}_

---

#### [Daerah 1] Yang Diambil dari **{fusion['ciri_daerah_1']['nama']}** (trigger: `{fusion['trigger_1']}`)
- **Palet warna:** {', '.join(fusion['ciri_daerah_1']['warna'])}
- **Motif utama:** {', '.join(fusion['ciri_daerah_1']['motif'])}
- **Pola:** {fusion['ciri_daerah_1']['pola']}
- **Filosofi:** {fusion['ciri_daerah_1']['filosofi']}
- **Elemen diambil:** {fusion['ciri_daerah_1']['elemen_utama']}

#### [Daerah 2] Yang Diambil dari **{fusion['ciri_daerah_2']['nama']}** (trigger: `{fusion['trigger_2']}`)
- **Palet warna:** {', '.join(fusion['ciri_daerah_2']['warna'])}
- **Motif utama:** {', '.join(fusion['ciri_daerah_2']['motif'])}
- **Pola:** {fusion['ciri_daerah_2']['pola']}
- **Filosofi:** {fusion['ciri_daerah_2']['filosofi']}
- **Elemen diambil:** {fusion['ciri_daerah_2']['elemen_utama']}

#### [Filosofi] Filosofi Fusion
{fusion['filosofi_fusion']}

#### [Pakai] Cocok Digunakan Untuk
{fusion['penggunaan']}
"""
    return md


def render_card_html(fusion: Dict, image_base_url: str = "") -> str:
    """Render fusion sebagai card HTML (gambar kiri, deskripsi kanan)."""
    if not fusion:
        return "<p>_(Fusion tidak ditemukan)_</p>"

    img_url = fusion['image']
    if image_base_url and img_url.startswith('images/'):
        img_url = image_base_url.rstrip('/') + '/' + img_url

    return f"""
    <div class="fusion-card">
        <div class="fusion-card-image">
            <img src="{img_url}" alt="{fusion['judul']}" loading="lazy">
        </div>
        <div class="fusion-card-body">
            <h3 class="fusion-title">{fusion['judul']}</h3>
            <p class="fusion-subtitle"><em>{fusion['subjudul']}</em></p>
            <div class="fusion-meta">
                <span class="meta-tag">{fusion['budaya_1']}</span>
                <span class="meta-plus">×</span>
                <span class="meta-tag">{fusion['budaya_2']}</span>
            </div>
            <div class="fusion-section">
                <h4>📍 Yang Diambil dari {fusion['ciri_daerah_1']['nama']}</h4>
                <p><strong>Warna:</strong> {', '.join(fusion['ciri_daerah_1']['warna'])}</p>
                <p><strong>Motif:</strong> {', '.join(fusion['ciri_daerah_1']['motif'])}</p>
                <p><strong>Filosofi:</strong> {fusion['ciri_daerah_1']['filosofi']}</p>
                <p class="elemen">{fusion['ciri_daerah_1']['elemen_utama']}</p>
            </div>
            <div class="fusion-section">
                <h4>📍 Yang Diambil dari {fusion['ciri_daerah_2']['nama']}</h4>
                <p><strong>Warna:</strong> {', '.join(fusion['ciri_daerah_2']['warna'])}</p>
                <p><strong>Motif:</strong> {', '.join(fusion['ciri_daerah_2']['motif'])}</p>
                <p><strong>Filosofi:</strong> {fusion['ciri_daerah_2']['filosofi']}</p>
                <p class="elemen">{fusion['ciri_daerah_2']['elemen_utama']}</p>
            </div>
            <div class="fusion-section highlight">
                <h4>🎨 Filosofi Fusion</h4>
                <p>{fusion['filosofi_fusion']}</p>
            </div>
            <div class="fusion-section">
                <h4>👔 Cocok Untuk</h4>
                <p>{fusion['penggunaan']}</p>
            </div>
        </div>
    </div>
    """


if __name__ == "__main__":
    tests = [
        ("a madurabatik jawa_timurbatik pattern, ...", "madura", "jawa_timur"),
        ("a madurabatik jawa_baratbatik fusion, emas", "", ""),
        ("a madura jawa_barat pattern biru putih", "", ""),
        ("fusion Madura dengan Jawa Tengah", "", ""),
        ("", "madura", "jawa_barat"),
        ("", "Solo", ""),
        ("random prompt nothing related", "", ""),
    ]
    for prompt, b1, b2 in tests:
        f, conf, mode = cari_fusion_dari_prompt(prompt, b1, b2)
        if f:
            print(f"  prompt='{prompt[:40]}...' -> {f['id']} (conf={conf})")
        else:
            print(f"  prompt='{prompt[:40]}...' -> NOT FOUND")