# -*- coding: utf-8 -*-
"""Upload index.html baru (dengan section fitur baru) ke HF Static Space.
Juga hapus 4 gambar sintetis lama yang salah upload."""
import sys
from huggingface_hub import HfApi

TOKEN = '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'
SPACE_ID = 'rafli9/batik-fusion-showcase'

api = HfApi(token=TOKEN)

# 1. Hapus 4 gambar sintetis yang salah upload
images_to_delete = [
    'images/madura_jawa_barat.png',
    'images/madura_pola_kompleks_jawa_barat.png',
    'images/madura_jawa_tengah.png',
    'images/madura_yogyakarta.png',
]
for f in images_to_delete:
    try:
        api.delete_file(path_in_repo=f, repo_id=SPACE_ID, repo_type='space',
                        commit_message=f'Remove placeholder image, waiting for real LoRA output')
        print(f'[DEL] {f}', flush=True)
    except Exception as e:
        print(f'[SKIP] {f}: {e}', flush=True)

# 2. Upload index.html yang baru (dengan section fitur + resource HF)
try:
    api.upload_file(
        path_or_fileobj=r'd:\Riset MBKM\model results\Batik_Re-Palette\showcase\index.html',
        path_in_repo='index.html',
        repo_id=SPACE_ID,
        repo_type='space',
        commit_message='Update index.html: keep original placeholder layout + add Fitur Unggulan & Resource HF sections',
    )
    print('[OK] index.html uploaded', flush=True)
except Exception as e:
    print(f'[ERR upload index.html] {e}', flush=True)

print(f'[DONE] https://huggingface.co/spaces/{SPACE_ID}', flush=True)