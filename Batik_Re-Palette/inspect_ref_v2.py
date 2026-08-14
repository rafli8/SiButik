# -*- coding: utf-8 -*-
"""Inspect reference Space - download app.py & README properly."""
import sys
import io
from huggingface_hub import HfApi

TOKEN = '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'
REF_SPACE = 'SIGMA5488/Batik_Re-Palette'

api = HfApi(token=TOKEN)

# 1. Get space info to determine SDK
print('=== SPACE INFO ===', flush=True)
try:
    info = api.repo_info(REF_SPACE, repo_type='space')
    print(f'Space: {info.id}', flush=True)
    print(f'SDK: {getattr(info, "sdk", "?")}', flush=True)
    print(f'Visibility: {getattr(info, "private", "?")}', flush=True)
    if hasattr(info, 'space_runtime'):
        print(f'Runtime: {info.space_runtime}', flush=True)
except Exception as e:
    print(f'ERR info: {e}', flush=True)

# 2. Download app.py
print('', flush=True)
print('=== APP.PY ===', flush=True)
try:
    from huggingforce_hub import hf_hub_download
except ImportError:
    from huggingface_hub import hf_hub_download
try:
    path = hf_hub_download(
        repo_id=REF_SPACE,
        filename='app.py',
        repo_type='space',
        cache_dir='./.hf_cache_ref',
    )
    with io.open(path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    print(f'File size: {len(content)} chars', flush=True)
    print('--- SNIPPET (first 3000 chars) ---', flush=True)
    print(content[:3000], flush=True)
    print('---', flush=True)
except Exception as e:
    print(f'ERR app.py: {e}', flush=True)

# 3. Download requirements.txt
print('', flush=True)
print('=== REQUIREMENTS.TXT ===', flush=True)
try:
    path = hf_hub_download(
        repo_id=REF_SPACE,
        filename='requirements.txt',
        repo_type='space',
        cache_dir='./.hf_cache_ref',
    )
    with io.open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    print(content, flush=True)
except Exception as e:
    print(f'ERR requirements: {e}', flush=True)