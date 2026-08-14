# -*- coding: utf-8 -*-
"""
generate_showcase.py
====================
Script untuk PRE-GENERATE gambar fusion batik dari semua kombinasi
pasangan daerah, sehingga bisa ditampilkan sebagai showcase STATIS
(tanpa GPU) di Hugging Face Static Space / GitHub Pages.

Cara kerja:
  1. Untuk setiap pasangan (daerah_1, daerah_2) dari BUDAYA_DB:
     - Generate gambar fusion pakai SDXL + LoRA joint-training
     - Generate narasi markdown penjelasan fusion
     - Simpan gambar ke folder `showcase/images/`
     - Simpan narasi ke `showcase/descriptions/<pasangan>.md`
     - Update `showcase/index.html` (gallery)

Output:
  showcase/
  ├── index.html              # Gallery HTML siap upload
  ├── styles.css              # Styling
  ├── images/                 # Gambar fusion (PNG)
  │   ├── madura_jawa_barat.png
  │   ├── madura_bali.png
  │   └── ...
  └── descriptions/           # Markdown penjelasan per fusion
      ├── madura_jawa_barat.md
      └── ...

Setelah selesai:
  - Upload folder `showcase/` ke Hugging Face Static Space (GRATIS)
  - Atau ke GitHub Pages / Netlify / Vercel (semua gratis)

Cara pakai:
  python generate_showcase.py
"""

from __future__ import annotations

import os
import sys
import json
import itertools
from pathlib import Path
from datetime import datetime
from typing import List, Tuple

# Tambah parent dir ke sys.path agar bisa import modul Batik_Re-Palette
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from fusion_engine import (
    buat_template_fusion, template_ke_markdown, BUDAYA_DB,
)
from lora_generator import generate_batik_dengan_lora, bersihkan_pipeline

OUTPUT_DIR = SCRIPT_DIR / "showcase"
IMAGES_DIR = OUTPUT_DIR / "images"
DESCRIPTIONS_DIR = OUTPUT_DIR / "descriptions"


def nama_file_aman(daerah_1: str, daerah_2: str) -> str:
    """Buat nama file aman dari 2 nama daerah."""
    return f"{daerah_1}_{daerah_2}".replace("/", "-").replace(" ", "_")


def generate_semua(
    pasangan: List[Tuple[str, str]] = None,
    lora_path: str = None,
    hf_repo_id: str = None,
    hf_filename: str = None,
    lora_scale: float = 0.85,
    steps: int = 25,
    seed: int = 42,
    hanya_dengan_lora: bool = False,
):
    """
    Generate fusion untuk semua pasangan (default: 13 daerah = 78 pasangan).

    Args:
        pasangan: list of (daerah_1, daerah_2). Default None = semua kombinasi.
        lora_path / hf_repo_id / hf_filename: sumber LoRA (lihat lora_generator.py)
        hanya_dengan_lora: kalau True, skip pasangan yang tidak ada LoRA-nya
                          (saat ini LoRA hanya dilatih untuk madura + jawa_barat)
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    DESCRIPTIONS_DIR.mkdir(parents=True, exist_ok=True)

    keys = list(BUDAYA_DB.keys())
    if pasangan is None:
        if hanya_dengan_lora:
            # Untuk demo lomba, fokus pada pasangan yang ada LoRA-nya
            pasangan = [
                ("madura", "jawa_barat"),
                ("madura_pola_kompleks", "jawa_barat"),
                ("madura", "jawa_tengah"),
                ("madura", "yogyakarta"),
            ]
        else:
            # Semua kombinasi (78 pasangan)
            pasangan = list(itertools.combinations(keys, 2))

    total = len(pasangan)
    print(f"[showcase] Akan generate {total} pasang fusion ...")
    print(f"[showcase] LoRA source: {lora_path or hf_repo_id or 'fallback sintetis'}")
    print(f"[showcase] Output dir : {OUTPUT_DIR}")
    print()

    gallery_entries = []
    sukses = 0
    gagal = 0

    for idx, (d1, d2) in enumerate(pasangan, 1):
        nama = nama_file_aman(d1, d2)
        print(f"[{idx}/{total}] Fusion: {d1} x {d2} ...")

        try:
            t = buat_template_fusion(
                nama_1=d1,
                prompt_1="",
                nama_2=d2,
                prompt_2="",
                tema="harmoni budaya nusantara",
                lora_path=lora_path,
                hf_repo_id=hf_repo_id,
                hf_filename=hf_filename,
                lora_scale=lora_scale,
                steps=steps,
                seed=seed,
            )

            # Simpan gambar
            img_path = IMAGES_DIR / f"{nama}.png"
            t.gambar.save(img_path)

            # Simpan narasi markdown
            md_path = DESCRIPTIONS_DIR / f"{nama}.md"
            md_path.write_text(template_ke_markdown(t), encoding="utf-8")

            # Kumpulkan entry untuk gallery
            gallery_entries.append({
                "id": nama,
                "daerah_1": t.asal_daerah_1,
                "daerah_2": t.asal_daerah_2,
                "judul": t.judul,
                "image": f"images/{nama}.png",
                "description": f"descriptions/{nama}.md",
                "trigger_1": t.trigger_1,
                "trigger_2": t.trigger_2,
                "prompt": t.prompt_gambar,
            })

            sukses += 1
            print(f"   [OK] Tersimpan: {img_path.name}")

        except Exception as e:
            gagal += 1
            print(f"   [GAGAL] {e}")

    # Simpan metadata gallery
    metadata = {
        "generated_at": datetime.now().isoformat(),
        "total_pairs": total,
        "success": sukses,
        "failed": gagal,
        "lora_source": lora_path or hf_repo_id or "fallback sintetis",
        "entries": gallery_entries,
    }
    (OUTPUT_DIR / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print()
    print(f"[showcase] Selesai! {sukses}/{total} berhasil, {gagal} gagal.")
    print(f"[showcase] Metadata: {OUTPUT_DIR / 'metadata.json'}")
    print(f"[showcase] Langkah selanjutnya: jalankan generate_index_html.py untuk buat gallery")

    # Bersihkan VRAM
    bersihkan_pipeline()
    return metadata


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Pre-generate gambar fusion batik untuk showcase statis."
    )
    parser.add_argument("--lora-path", help="Path lokal ke file .safetensors")
    parser.add_argument("--hf-repo-id", help="HF repo ID untuk download LoRA")
    parser.add_argument("--hf-filename", help="Nama file .safetensors di HF")
    parser.add_argument("--lora-scale", type=float, default=0.85)
    parser.add_argument("--steps", type=int, default=25)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--all", action="store_true",
                        help="Generate SEMUA pasangan (78). Default: hanya yang ada LoRA-nya (4)")
    parser.add_argument("--pasangan", nargs="+",
                        help="Pasangan custom, mis. --pasangan madura jawa_barat madura bali")

    args = parser.parse_args()

    if args.pasangan:
        pasangan_custom = []
        for i in range(0, len(args.pasangan), 2):
            if i + 1 < len(args.pasangan):
                pasangan_custom.append((args.pasangan[i], args.pasangan[i + 1]))
        pasangan_arg = pasangan_custom
    elif args.all:
        pasangan_arg = None  # akan di-resolve ke semua kombinasi
    else:
        pasangan_arg = None  # default: hanya_dengan_lora=True (4 pasangan)

    generate_semua(
        pasangan=pasangan_arg,
        lora_path=args.lora_path,
        hf_repo_id=args.hf_repo_id,
        hf_filename=args.hf_filename,
        lora_scale=args.lora_scale,
        steps=args.steps,
        seed=args.seed,
        hanya_dengan_lora=not args.all,
    )
