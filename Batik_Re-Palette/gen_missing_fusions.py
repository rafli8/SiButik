"""Generate gambar sintetis untuk 2 fusion yang belum punya gambar."""
import sys
sys.path.insert(0, r'd:\Riset MBKM\model results\Batik_Re-Palette')
from lora_generator import _generate_sintetis
from pathlib import Path

OUT = Path(r'd:\Riset MBKM\model results\Batik_Re-Palette\showcase\images')
OUT.mkdir(parents=True, exist_ok=True)

pasangan = [
    ('madura_jawa_tengah', 'a madurabatik jawa_tengahbatik batik pattern, fusion of madura and jawa_tengah, parang and kawung motifs'),
    ('solo', 'a jawa_tengahbatik jawa_tengahbatik batik pattern, solo parang kawung truntum batik, keagungan jawa'),
]

for name, prompt in pasangan:
    print(f'Generating {name}...', flush=True)
    img = _generate_sintetis(prompt, ukuran=512)
    out = OUT / f'{name}.png'
    img.save(out)
    print(f'  [OK] {out.name} ({out.stat().st_size // 1024} KB)', flush=True)

print('\n=== HASIL ===', flush=True)
for f in sorted(OUT.iterdir()):
    print(f'  {f.name}: {f.stat().st_size:,} bytes', flush=True)