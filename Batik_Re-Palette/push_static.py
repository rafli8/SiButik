# -*- coding: utf-8 -*-
"""Upload folder showcase ke HF Static Space."""
import sys
from huggingface_hub import HfApi

TOKEN = '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'
SPACE_ID = 'rafli9/batik-fusion-showcase'
FOLDER = r'd:\Riset MBKM\model results\Batik_Re-Palette\showcase'

api = HfApi(token=TOKEN)

# 1. Buat static space
try:
    api.create_repo(
        repo_id=SPACE_ID,
        repo_type='space',
        space_sdk='static',
        exist_ok=True,
    )
    print(f'[OK] Static Space siap: https://huggingface.co/spaces/{SPACE_ID}', flush=True)
except Exception as e:
    print(f'[ERR create_repo] {e}', flush=True)
    sys.exit(1)

# 2. Upload folder showcase (index.html, styles.css, images/, descriptions/)
try:
    api.upload_folder(
        folder_path=FOLDER,
        repo_id=SPACE_ID,
        repo_type='space',
        commit_message='Deploy Batik Re-Palette static showcase (4 fusion images)',
    )
    print(f'[OK] Folder showcase berhasil di-upload!', flush=True)
    print(f'[DONE] Showcase live di: https://huggingface.co/spaces/{SPACE_ID}', flush=True)
except Exception as e:
    print(f'[ERR upload_folder] {e}', flush=True)
    sys.exit(1)