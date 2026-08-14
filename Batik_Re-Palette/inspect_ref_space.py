# -*- coding: utf-8 -*-
"""Inspect reference Space SIGMA5488/Batik_Re-Palette."""
import sys
from huggingface_hub import HfApi

TOKEN = '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'
REF_SPACE = 'SIGMA5488/Batik_Re-Palette'

api = HfApi(token=TOKEN)

# 1. List files di Space
print('=== FILE LISTING ===', flush=True)
try:
    files = api.list_repo_files(REF_SPACE, repo_type='space')
    print(f'Space: https://huggingface.co/spaces/{REF_SPACE}', flush=True)
    print(f'SDK: dari file list dan nama Space (Static biasanya)', flush=True)
    print(f'Files ({len(files)}):', flush=True)
    for f in files:
        size_info = ''
        print(f'  - {f}{size_info}', flush=True)
except Exception as e:
    print(f'ERR list: {e}', flush=True)

# 2. Download dan tampilkan index.html
print('', flush=True)
print('=== INDEX.HTML (500 char pertama) ===', flush=True)
try:
    from huggingface_hub import hf_hub_download
    path = hf_hub_download(
        repo_id=REF_SPACE,
        filename='index.html',
        repo_type='space',
        cache_dir='./.hf_cache_ref',
    )
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    print(f'File size: {len(content)} chars', flush=True)
    print('--- SNIPPET (first 1500 chars) ---', flush=True)
    print(content[:1500], flush=True)
    print('---', flush=True)
except Exception as e:
    print(f'ERR download index.html: {e}', flush=True)

# 3. Download dan tampilkan README.md
print('', flush=True)
print('=== README.MD ===', flush=True)
try:
    path = hf_hub_download(
        repo_id=REF_SPACE,
        filename='README.md',
        repo_type='space',
        cache_dir='./.hf_cache_ref',
    )
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    print(content, flush=True)
except Exception as e:
    print(f'ERR download README.md: {e}', flush=True)