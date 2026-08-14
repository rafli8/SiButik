# -*- coding: utf-8 -*-
"""
fusion_engine.py
================
Mesin untuk menggabungkan 2 budaya (tradisi/daerah) menjadi sebuah
template fusion batik, lengkap dengan penjelasan naratif.

KEY MATCH dengan dataset training (lihat `captioning (1).ipynb` &
`training2daerah (1).ipynb`):
  - Trigger token = "{region}batik"  -> mis. "madurabatik", "jawa_baratbatik"
  - Class word    = "batik"
  - Caption format: "{trigger} batik, {deskripsi visual}"
  - Untuk fusion 2 daerah -> sertakan KEDUA trigger di prompt.

Setiap key di BUDAYA_DB adalah **persis nama folder dataset** (sesuai yang
ditemukan oleh notebook captioning). User cukup ketik nama daerah (mis.
"Madura" atau "jawa_barat") dan otomatis dicocokkan ke key dataset yang
sesuai.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional

from PIL import Image

from lora_generator import generate_batik_dengan_lora


# -------------------------------------------------------------------
# Basis pengetahuan budaya.
# KEY = nama folder dataset (lowercase, underscore).
# -------------------------------------------------------------------
BUDAYA_DB: Dict[str, Dict] = {
    "madura": {
        "nama_lengkap": "Madura",
        "pulau": "Pulau Madura, Jawa Timur",
        "warna_khas": ["merah tua", "kuning emas", "navy gelap", "krem"],
        "motif_khas": ["floral sprigs", "birds", "mata rantai", "bintang"],
        "filosofi": "Ketegasan, keberanian, dan kemandirian.",
        "pola_umum": "repeating dense floral and figurative motifs",
        "penggunaan": "pakaian adat dan kain pernikahan",
    },
    "madura_pola_kompleks": {
        "nama_lengkap": "Madura (Pola Kompleks)",
        "pulau": "Pulau Madura, Jawa Timur",
        "warna_khas": ["navy gelap", "krem", "merah tua", "putih"],
        "motif_khas": ["layered floral medallions", "birds", "small dots"],
        "filosofi": "Keberanian dan kemewahan motif berlapis.",
        "pola_umum": "very dense and layered repeating pattern",
        "penggunaan": "kain pernikahan dan acara adat",
    },
    "madura_pola_sederhana": {
        "nama_lengkap": "Madura (Pola Sederhana)",
        "pulau": "Pulau Madura, Jawa Timur",
        "warna_khas": ["navy", "putih", "merah"],
        "motif_khas": ["simple repeating flowers", "minimal birds"],
        "filosofi": "Kesederhanaan yang tetap berani.",
        "pola_umum": "simple, repetitive motif with breathing space",
        "penggunaan": "kain sehari-hari dan pakaian casual",
    },
    "jawa_barat": {
        "nama_lengkap": "Jawa Barat (Sunda)",
        "pulau": "Pulau Jawa bagian barat",
        "warna_khas": ["navy dalam", "emas", "putih"],
        "motif_khas": ["cloud-like swirls", "gunung", "kujang"],
        "filosofi": "Keharmonisan dengan alam dan leluhur.",
        "pola_umum": "flowing continuous cloud-like swirls",
        "penggunaan": "kain seragam dan pakaian resmi",
    },
    "jawa_tengah": {
        "nama_lengkap": "Jawa Tengah",
        "pulau": "Pulau Jawa bagian tengah",
        "warna_khas": ["coklat soga", "putih", "biru indigo"],
        "motif_khas": ["parang", "kawung", "truntum"],
        "filosofi": "Keharmonisan, kesabaran, keseimbangan hidup.",
        "pola_umum": "halus, simetris, penuh gradasi",
        "penggunaan": "baju formal, selendang, kain sehari-hari",
    },
    "jawa_timur": {
        "nama_lengkap": "Jawa Timur",
        "pulau": "Pulau Jawa bagian timur",
        "warna_khas": ["coklat tua", "kuning", "merah"],
        "motif_khas": ["pradah", "modang", "bledak"],
        "filosofi": "Semangat juang dan keteguhan.",
        "pola_umum": "bold geometris dengan aksen cerah",
        "penggunaan": "kain acara dan pakaian pernikahan",
    },
    "yogyakarta": {
        "nama_lengkap": "Yogyakarta",
        "pulau": "Pulau Jawa (DIY)",
        "warna_khas": ["coklat soga", "putih", "emas"],
        "motif_khas": ["parang", "kawung", "truntum", "tambal"],
        "filosofi": "Keagungan keraton dan kearifan adiluhung.",
        "pola_umum": "halus, sangat simetris, penuh makna",
        "penggunaan": "kain kerajaan dan pakaian resmi",
    },
    "bali": {
        "nama_lengkap": "Bali",
        "pulau": "Pulau Bali",
        "warna_khas": ["merah", "emas", "hitam"],
        "motif_khas": ["pita", "ceplok", "pucuk", "wayang"],
        "filosofi": "Spiritualitas Hindu dan keberanian artistik.",
        "pola_umum": "ramai, penuh warna, dinamis",
        "penggunaan": "kain ritual dan pakaian tari",
    },
    "kalimantan": {
        "nama_lengkap": "Kalimantan (Dayak)",
        "pulau": "Pulau Kalimantan",
        "warna_khas": ["merah", "hitam", "kuning", "putih"],
        "motif_khas": ["burung enggang", "sulur", "kalung manik"],
        "filosofi": "Kehidupan hutan dan pelindung roh.",
        "pola_umum": "organik, sulur-suluran, penuh cerita",
        "penggunaan": "kain tradisional dan aksesoris adat",
    },
    "sulawesi": {
        "nama_lengkap": "Sulawesi (Bugis-Makassar)",
        "pulau": "Pulau Sulawesi",
        "warna_khas": ["merah tua", "emas", "hitam"],
        "motif_khas": ["phinisi", "rumah adat", "bunga teratai"],
        "filosofi": "Maritim dan jiwa pelaut.",
        "pola_umum": "megah, simbol kelautan",
        "penggunaan": "kain pernikahan dan pakaian resmi",
    },
    "papua": {
        "nama_lengkap": "Papua",
        "pulau": "Pulau Papua",
        "warna_khas": ["coklat", "merah", "kuning"],
        "motif_khas": ["cendrawasih", "asmat", "rumah honai"],
        "filosofi": "Alam, leluhur, kehidupan komunitas.",
        "pola_umum": "naturalistik, figuratif",
        "penggunaan": "noken, pakaian tari, aksesoris adat",
    },
    "sumatera": {
        "nama_lengkap": "Sumatera (Minangkabau/Batak)",
        "pulau": "Pulau Sumatera",
        "warna_khas": ["merah", "hitam", "putih", "emas"],
        "motif_khas": ["rumah gadang", "ulos", "songket"],
        "filosofi": "Kekerabatan dan keagungan adat.",
        "pola_umum": "tegas dengan aksen emas",
        "penggunaan": "ulos, songket, pakaian adat",
    },
    "nusa_tenggara": {
        "nama_lengkap": "Nusa Tenggara (NTT/NTB)",
        "pulau": "Kepulauan Nusa Tenggara",
        "warna_khas": ["biru indigo", "coklat", "putih"],
        "motif_khas": ["tenun ikat", "kuda", "ayam"],
        "filosofi": "Kesederhanaan dan kerja keras.",
        "pola_umum": "ikat dan pola etnis yang khas",
        "penggunaan": "tenun harian dan acara adat",
    },
}


# Daftar key dataset yang dipakai di notebook training (untuk referensi)
ALL_REGIONS_TRAINING: List[str] = [
    "madura_pola_kompleks",
    "madura_pola_sederhana",
    "jawa_barat",
    "jawa_tengah",
    "jawa_timur",
    "madura",
    "yogyakarta",
]


@dataclass
class TemplateFusion:
    judul: str
    deskripsi_singkat: str
    asal_daerah_1: str
    asal_daerah_2: str
    key_dataset_1: str
    key_dataset_2: str
    trigger_1: str
    trigger_2: str
    elemen_daerah_1: List[str]
    elemen_daerah_2: List[str]
    filosofi_fusion: str
    penggunaan_cocok: str
    prompt_gambar: str
    gambar: Optional[Image.Image] = None
    catatan_tambahan: str = ""


# Alias input user -> key BUDAYA_DB
_ALIAS: Dict[str, str] = {
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
    "solo": "jawa_tengah",
}


def _normalisasi_key(nama: str) -> Optional[str]:
    if not nama:
        return None
    s = nama.lower().strip().replace("-", "_").replace(" ", "_")
    if s in BUDAYA_DB:
        return s
    if s in _ALIAS:
        return _ALIAS[s]
    for k in BUDAYA_DB.keys():
        if k in s or s in k:
            return k
    return None


def _info_budaya(key: Optional[str]) -> Tuple[str, Dict]:
    if key and key in BUDAYA_DB:
        return key, BUDAYA_DB[key]
    fallback_key = key or "custom"
    return fallback_key, {
        "nama_lengkap": fallback_key.replace("_", " ").title(),
        "pulau": "wilayah lokal",
        "warna_khas": ["hangat", "alami"],
        "motif_khas": ["motif khas daerah"],
        "filosofi": "kearifan lokal",
        "pola_umum": "khas daerah",
        "penggunaan": "pakaian adat dan kain tradisional",
    }


def trigger_dari_key(key: Optional[str]) -> Optional[str]:
    if not key:
        return None
    return f"{key}batik"


def bangun_prompt_fusion(nama_1: str, prompt_1: str,
                         nama_2: str, prompt_2: str,
                         tema: str = ""):
    """Return: (prompt, key1, key2, info1, info2, trigger1, trigger2)."""
    key1 = _normalisasi_key(nama_1) or nama_1.lower().strip()
    key2 = _normalisasi_key(nama_2) or nama_2.lower().strip()

    _, info1 = _info_budaya(key1)
    _, info2 = _info_budaya(key2)

    tr1 = trigger_dari_key(key1) or f"{key1}batik"
    tr2 = trigger_dari_key(key2) or f"{key2}batik"

    tema_str = (tema or "harmoni budaya nusantara").strip()
    extras = []
    if prompt_1 and prompt_1.strip():
        extras.append(prompt_1.strip())
    if prompt_2 and prompt_2.strip():
        extras.append(prompt_2.strip())
    extra_str = ", " + ", ".join(extras) if extras else ""

    prompt_gambar = (
        f"a {tr1} {tr2} batik pattern, "
        f"fusion of {info1['nama_lengkap']} and {info2['nama_lengkap']} culture, "
        f"{tema_str}, "
        f"{info1['motif_khas'][0]} combined with {info2['motif_khas'][0]}, "
        f"intricate detail, symmetrical composition, "
        f"traditional indonesian textile art{extra_str}"
    )
    return prompt_gambar, key1, key2, info1, info2, tr1, tr2


def buat_template_fusion(
    nama_1: str, prompt_1: str,
    nama_2: str, prompt_2: str,
    tema: str = "",
    lora_path: Optional[str] = None,
    hf_repo_id: Optional[str] = None,
    hf_filename: Optional[str] = None,
    lora_scale: float = 0.85,
    steps: int = 30,
    guidance: float = 7.0,
    seed: int = -1,
    base_model: str = "stabilityai/stable-diffusion-xl-base-1.0",
) -> TemplateFusion:
    (prompt_gambar, key1, key2, info1, info2, tr1, tr2) = bangun_prompt_fusion(
        nama_1, prompt_1, nama_2, prompt_2, tema
    )

    gambar = generate_batik_dengan_lora(
        prompt=prompt_gambar,
        lora_path=lora_path,
        hf_repo_id=hf_repo_id,
        hf_filename=hf_filename,
        lora_scale=lora_scale,
        num_steps=steps,
        guidance=guidance,
        seed=seed,
        base_model=base_model,
    )

    el_1 = [
        f"trigger token: {tr1}",
        f"palet warna: {', '.join(info1['warna_khas'][:3])}",
        f"motif: {info1['motif_khas'][0]}",
        f"pola: {info1['pola_umum']}",
    ]
    el_2 = [
        f"trigger token: {tr2}",
        f"palet warna: {', '.join(info2['warna_khas'][:3])}",
        f"motif: {info2['motif_khas'][0]}",
        f"pola: {info2['pola_umum']}",
    ]

    judul = f"Fusion {info1['nama_lengkap']} x {info2['nama_lengkap']}"
    deskripsi = (
        f"Sebuah kanvas baru yang menyatukan dua kekayaan budaya: "
        f"{info1['nama_lengkap']} dari {info1['pulau']} dan "
        f"{info2['nama_lengkap']} dari {info2['pulau']}."
    )
    filosofi = (
        f"Fusion ini memadukan '{info1['filosofi']}' dari {info1['nama_lengkap']} "
        f"dengan '{info2['filosofi']}' dari {info2['nama_lengkap']}, "
        f"menghasilkan kain yang merepresentasikan pertemuan dua jiwa nusantara."
    )
    penggunaan = (
        f"Cocok untuk {info1['penggunaan'].split(',')[0]} "
        f"sekaligus {info2['penggunaan'].split(',')[0]}."
    )
    catatan = f"Tema yang diangkat: {tema.strip()}." if tema.strip() else ""

    return TemplateFusion(
        judul=judul,
        deskripsi_singkat=deskripsi,
        asal_daerah_1=info1["nama_lengkap"],
        asal_daerah_2=info2["nama_lengkap"],
        key_dataset_1=key1,
        key_dataset_2=key2,
        trigger_1=tr1,
        trigger_2=tr2,
        elemen_daerah_1=el_1,
        elemen_daerah_2=el_2,
        filosofi_fusion=filosofi,
        penggunaan_cocok=penggunaan,
        prompt_gambar=prompt_gambar,
        gambar=gambar,
        catatan_tambahan=catatan,
    )


def template_ke_markdown(t: TemplateFusion) -> str:
    el1_md = "\n".join(f"- {x}" for x in t.elemen_daerah_1)
    el2_md = "\n".join(f"- {x}" for x in t.elemen_daerah_2)

    md = f"""### {t.judul}

{t.deskripsi_singkat}

---

#### [Daerah 1] Yang Diambil dari **{t.asal_daerah_1}** (key: `{t.key_dataset_1}`)
{el1_md}

#### [Daerah 2] Yang Diambil dari **{t.asal_daerah_2}** (key: `{t.key_dataset_2}`)
{el2_md}

#### [Filosofi] Filosofi Fusion
{t.filosofi_fusion}

#### [Pakai] Cocok Digunakan Untuk
{t.penggunaan_cocok}

#### [Prompt] Prompt yang Dikirim ke SDXL + LoRA
```
{t.prompt_gambar}
```

#### [Trigger] Trigger Tokens
- Daerah 1: `{t.trigger_1}`
- Daerah 2: `{t.trigger_2}`
"""
    if t.catatan_tambahan:
        md += f"\n*{t.catatan_tambahan}*\n"
    return md
