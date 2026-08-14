# -*- coding: utf-8 -*-
"""Upload index.html + styles.css baru (mirip Gradio Blocks) ke HF Static Space."""
from huggingface_hub import HfApi

TOKEN = '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'
SPACE_ID = 'rafli9/batik-fusion-showcase'

api = HfApi(token=TOKEN)

# Upload index.html yang baru (layout Gradio Blocks)
try:
    api.upload_file(
        path_or_fileobj=r'd:\Riset MBKM\model results\Batik_Re-Palette\showcase\index.html',
        path_in_repo='index.html',
        repo_id=SPACE_ID,
        repo_type='space',
        commit_message='Replace showcase with Gradio Blocks layout (3 tabs as docs)',
    )
    print('[OK] index.html uploaded', flush=True)
except Exception as e:
    print(f'[ERR upload index.html] {e}', flush=True)

# Upload styles.css yang baru (style Gradio)
try:
    api.upload_file(
        path_or_fileobj=r'd:\Riset MBKM\model results\Batik_Re-Palette\showcase\styles.css',
        path_in_repo='styles.css',
        repo_id=SPACE_ID,
        repo_type='space',
        commit_message='Update styles.css: Gradio Blocks theme (tabs, inputs, sliders, color pickers)',
    )
    print('[OK] styles.css uploaded', flush=True)
except Exception as e:
    print(f'[ERR upload styles.css] {e}', flush=True)

print(f'[DONE] https://huggingface.co/spaces/{SPACE_ID}', flush=True)