# -*- coding: utf-8 -*-
"""Verifikasi deploy ke HF Space."""
from huggingface_hub import HfApi

TOKEN = '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'
SPACE_ID = 'rafli9/batik-fusion-showcase'
LORA_ID = 'rafli9/batik-joint-lora'

api = HfApi(token=TOKEN)

# 1. Verifikasi Space
print('=== STATIC SPACE ===', flush=True)
try:
    files = api.list_repo_files(SPACE_ID, repo_type='space')
    print(f'Space: https://huggingface.co/spaces/{SPACE_ID}', flush=True)
    print(f'Files ({len(files)}):', flush=True)
    for f in files:
        print(f'  - {f}', flush=True)
except Exception as e:
    print(f'ERR: {e}', flush=True)

print('', flush=True)

# 2. Verifikasi LoRA
print('=== LORA MODEL HUB ===', flush=True)
try:
    files = api.list_repo_files(LORA_ID, repo_type='model')
    print(f'LoRA: https://huggingface.co/{LORA_ID}', flush=True)
    print(f'Files ({len(files)}):', flush=True)
    for f in files:
        print(f'  - {f}', flush=True)
except Exception as e:
    print(f'ERR: {e}', flush=True)