# -*- coding: utf-8 -*-
"""Generate index.html dengan path gambar fusion yang sebenarnya."""
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, r'd:\Riset MBKM\model results\Batik_Re-Palette')
from fusion_engine import buat_template_fusion, template_ke_markdown

OUTPUT_DIR = Path(r'd:\Riset MBKM\model results\Batik_Re-Palette\showcase')
IMAGES_DIR = OUTPUT_DIR / 'images'
DESCRIPTIONS_DIR = OUTPUT_DIR / 'descriptions'

pasangan = [
    ('madura', 'jawa_barat'),
    ('madura_pola_kompleks', 'jawa_barat'),
    ('madura', 'jawa_tengah'),
    ('madura', 'yogyakarta'),
]

cards_html = []
descriptions_md = []

for d1, d2 in pasangan:
    t = buat_template_fusion(d1, '', d2, '', tema='harmoni budaya nusantara', steps=10, seed=42)
    img_file = f'{d1}_{d2}.png'
    desc_file = f'{d1}_{d2}.md'

    card = f'''
            <div class="card">
                <img class="card-image" src="images/{img_file}" alt="Fusion {d1} x {d2}" loading="lazy">
                <div class="card-body">
                    <h3>{t.judul}</h3>
                    <p class="triggers">
                        <span class="trigger">{t.trigger_1}</span>
                        <span class="plus">+</span>
                        <span class="trigger">{t.trigger_2}</span>
                    </p>
                    <p class="desc">{t.deskripsi_singkat}</p>
                    <details>
                        <summary>Lihat narasi lengkap</summary>
                        <div class="markdown-body">
                            <pre>{template_ke_markdown(t)}</pre>
                        </div>
                    </details>
                </div>
            </div>'''
    cards_html.append(card)
    md_content = template_ke_markdown(t)
    (DESCRIPTIONS_DIR / desc_file).write_text(md_content, encoding='utf-8')

tanggal = datetime.now().strftime('%Y-%m-%d')
html = f'''<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Batik Fusion Showcase - Cultural Fusion 2 Budaya</title>
<link rel="stylesheet" href="styles.css">
</head>
<body>
<header>
    <h1>Batik Fusion Showcase</h1>
    <p class="subtitle">Cultural Fusion 2 Budaya dengan SDXL + LoRA Joint Training</p>
    <p class="meta">
        Dibuat pada: {tanggal} | Total: {len(pasangan)} pasang fusion | Riset MBKM
    </p>
</header>

<main>
    <section class="info-box">
        <h2>Tentang Showcase Ini</h2>
        <p>
            Showcase ini menampilkan hasil <b>Cultural Fusion Batik</b> dari dua
            daerah Nusantara yang berbeda, di-generate menggunakan
            <b>Stable Diffusion XL + LoRA Joint Training</b>.
        </p>
        <p>
            Setiap gambar dihasilkan dengan menyertakan <b>trigger token</b>
            dari kedua daerah (mis. <code>madurabatik jawa_baratbatik</code>),
            sehingga model menggabungkan motif, warna, dan pola khas masing-masing
            daerah menjadi satu kain batik fusion yang utuh.
        </p>
        <p><b>Komponen teknis:</b></p>
        <ul>
            <li>Base model: <code>stabilityai/stable-diffusion-xl-base-1.0</code></li>
            <li>VAE: <code>madebyollin/sdxl-vae-fp16-fix</code></li>
            <li>LoRA: joint training (kohya-ss), network_dim=32, network_alpha=16</li>
            <li>Trigger format: <code>{ '{' }region{ '}' }batik</code> untuk tiap daerah</li>
        </ul>
        <p>
            Untuk generate fusion baru (custom prompt, custom pasangan,
            simulasi jadi pakaian), gunakan <b>app.py</b> (perlu GPU).
        </p>
    </section>

    <section class="gallery">
        <h2>Galeri Hasil Fusion</h2>
        <p class="section-sub">{len(pasangan)} pasangan utama — dijalankan dengan LoRA Joint Training madura + jawa_barat</p>
        <div class="grid">{''.join(cards_html)}
        </div>
    </section>

    <section class="info-box">
        <h2>Tentang Aplikasi</h2>
        <p>
            <b>Batik Re-Palette</b> adalah aplikasi AI (Stable Diffusion XL + LoRA)
            untuk menggabungkan motif batik dari 2 daerah Nusantara berbeda,
            menghasilkan pola fusion yang harmonis secara visual dan filosofis.
        </p>
        <ul>
            <li><b>Generate fusion</b> dari kombinasi 2 budaya</li>
            <li><b>Narasi otomatis</b> tentang warna, motif, dan filosofi yang diambil dari tiap daerah</li>
            <li><b>Simulasi pakaian</b> (virtual try-on)</li>
            <li><b>LoRA fleksibel</b> — bisa diganti tanpa ubah kode</li>
        </ul>
        <p>
            Untuk generate fusion baru secara online, buka
            <a href="https://huggingface.co/spaces/rafli9/batik-fusion-space" target="_blank">web app demo</a>
            (perlu GPU) atau gunakan <code>app.py</code> di lokal.
        </p>
    </section>
</main>

<footer>
    <p>
        <b>Batik Re-Palette</b> - Hasil Riset MBKM<br>
        <small>Dibuat dengan SDXL + LoRA Joint Training (kohya-ss) - oleh Afrizal Rafli</small>
    </p>
</footer>
</body>
</html>
'''

(OUTPUT_DIR / 'index.html').write_text(html, encoding='utf-8')
print(f'[OK] index.html updated with {len(pasangan)} cards')

# Simpan metadata
metadata = {
    'generated_at': datetime.now().isoformat(),
    'total_pairs': len(pasangan),
    'entries': [{'id': f'{d1}_{d2}', 'image': f'images/{d1}_{d2}.png'} for d1, d2 in pasangan]
}
(OUTPUT_DIR / 'metadata.json').write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding='utf-8')
print(f'[OK] metadata.json saved')