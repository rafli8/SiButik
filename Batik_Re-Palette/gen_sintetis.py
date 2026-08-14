# -*- coding: utf-8 -*-
"""Generate 4 gambar fusion sintetis ke showcase/images/."""
import sys
import traceback
sys.path.insert(0, r'd:\Riset MBKM\model results\Batik_Re-Palette')

from lora_generator import _generate_sintetis
from pathlib import Path

IMAGES_DIR = Path(r'd:\Riset MBKM\model results\Batik_Re-Palette\showcase\images')
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

pasangan = [
    ('madura', 'jawa_barat'),
    ('madura_pola_kompleks', 'jawa_barat'),
    ('madura', 'jawa_tengah'),
    ('madura', 'yogyakarta'),
]

for idx, (d1, d2) in enumerate(pasangan, 1):
    try:
        prompt = f'a {d1}batik {d2}batik batik pattern, fusion of {d1} and {d2}'
        img = _generate_sintetis(prompt, ukuran=512)
        img_path = IMAGES_DIR / f'{d1}_{d2}.png'
        img.save(img_path)
        print(f'[{idx}/4] OK: {img_path.name} ({img_path.stat().st_size // 1024} KB)', flush=True)
    except Exception as e:
        print(f'[{idx}/4] GAGAL: {e}', flush=True)
        traceback.print_exc()

print('Selesai!', flush=True)