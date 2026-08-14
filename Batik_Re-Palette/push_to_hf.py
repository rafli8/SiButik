# -*- coding: utf-8 -*-
"""
push_to_hf.py
==============
Script CLI untuk push folder Batik_Re-Palette ke Hugging Face Spaces
dan upload file LoRA .safetensors ke Hugging Face Model Hub.

Prasyarat:
    pip install -U "huggingface_hub>=0.20.0"

Login dulu (salah satu):
    huggingface-cli login              # interaktif
    export HF_TOKEN=hf_xxxxxxxxxxxxx  # env var

Cara pakai:
    # 1) Push kode web ke Space (sekali jalan untuk membuat Space)
    python push_to_hf.py space \
        --space-id username/batik-fusion-space \
        --token hf_xxxx

    # 2) Upload LoRA .safetensors ke HF Model Hub
    python push_to_hf.py lora \
        --repo-id username/batik-joint-lora \
        --file "madura-madura_pola_kompleks-joint-lora-000001.safetensors" \
        --token hf_xxxx

    # 3) Push keduanya sekaligus
    python push_to_hf.py all \
        --space-id username/batik-fusion-space \
        --repo-id username/batik-joint-lora \
        --file "*.safetensors" \
        --token hf_xxxx
"""

import argparse
import os
import sys
from pathlib import Path


def get_hf():
    try:
        from huggingface_hub import (
            HfApi, login, whoami,
            create_repo, upload_folder, upload_file,
        )
        return HfApi, login, whoami, create_repo, upload_folder, upload_file
    except ImportError:
        print("[ERROR] Library 'huggingface_hub' belum terinstall.")
        print("        Jalankan: pip install -U 'huggingface_hub>=0.20.0'")
        sys.exit(1)


def ensure_login(token: str = None):
    HfApi, login, *_ = get_hf()
    if token:
        login(token=token, add_to_git_credential=False)
    else:
        # Coba pakai cached token dari huggingface-cli
        try:
            from huggingface_hub import HfFolder
            cached = HfFolder.get_token()
            if cached:
                print(f"[INFO] Pakai cached token: {cached[:8]}...")
            else:
                print("[WARN] Belum login. Jalankan 'huggingface-cli login' atau pass --token.")
                sys.exit(1)
        except Exception:
            print("[WARN] Belum login. Jalankan 'huggingface-cli login' atau pass --token.")
            sys.exit(1)


def push_space(space_id: str, token: str = None,
               folder: str = ".", commit_msg: str = "Update Batik Fusion Space"):
    """Upload folder ke Hugging Face Space (sdk=gradio)."""
    HfApi, *_ = get_hf()
    ensure_login(token)

    api = HfApi()
    print(f"[INFO] Membuat/mengambil Space: {space_id} ...")
    api.create_repo(
        repo_id=space_id,
        repo_type="space",
        space_sdk="gradio",
        exist_ok=True,
        token=token,
    )

    print(f"[INFO] Upload folder {folder} ke Space {space_id} ...")
    api.upload_folder(
        folder_path=folder,
        repo_id=space_id,
        repo_type="space",
        commit_message=commit_msg,
        ignore_patterns=[
            "*.pyc", "__pycache__", ".git", "*.zip",
            ".lora-cache", "*.safetensors",  # skip file besar di Space
        ],
        token=token,
    )
    print(f"[OK] Space siap: https://huggingface.co/spaces/{space_id}")


def push_lora(repo_id: str, file: str, token: str = None,
              commit_msg: str = "Upload LoRA .safetensors"):
    """Upload file .safetensors ke Hugging Face Model Hub."""
    HfApi, *_ = get_hf()
    ensure_login(token)

    api = HfApi()
    print(f"[INFO] Membuat/mengambil repo: {repo_id} ...")
    api.create_repo(
        repo_id=repo_id,
        repo_type="model",
        exist_ok=True,
        token=token,
    )

    # Dukung glob pattern atau path tunggal
    import glob as _glob
    files = _glob.glob(file) if any(c in file for c in "*?[") else [file]

    if not files:
        print(f"[ERROR] Tidak ada file yang cocok dengan pola: {file}")
        sys.exit(1)

    for fpath in files:
        if not os.path.isfile(fpath):
            print(f"[WARN] Lewati, bukan file: {fpath}")
            continue
        size_mb = os.path.getsize(fpath) / (1024 * 1024)
        print(f"[INFO] Upload {fpath} ({size_mb:.1f} MB) -> {repo_id}/{os.path.basename(fpath)} ...")
        api.upload_file(
            path_or_fileobj=fpath,
            path_in_repo=os.path.basename(fpath),
            repo_id=repo_id,
            repo_type="model",
            commit_message=commit_msg,
            token=token,
        )
        print(f"[OK] Uploaded: {os.path.basename(fpath)}")

    print(f"[OK] Repo LoRA siap: https://huggingface.co/{repo_id}")
    print(f"[INFO] Cara pakai di web app:")
    print(f"       HF Repo ID  : {repo_id}")
    print(f"       HF Filename : {os.path.basename(files[0])}")


def main():
    parser = argparse.ArgumentParser(
        description="Push Batik Fusion ke Hugging Face (Space + LoRA Model)."
    )
    parser.add_argument("action", choices=["space", "lora", "all"],
                        help="Aksi: space / lora / all")
    parser.add_argument("--space-id", help="HF Space repo id, mis. username/batik-fusion-space")
    parser.add_argument("--repo-id", help="HF Model repo id untuk LoRA, mis. username/batik-joint-lora")
    parser.add_argument("--file", help="Path/glob ke file .safetensors")
    parser.add_argument("--folder", default=".",
                        help="Folder lokal yang akan di-upload ke Space (default: folder skrip)")
    parser.add_argument("--token", help="HF token (kalau tidak pakai cached token)")
    parser.add_argument("--commit-msg", help="Pesan commit untuk upload")
    args = parser.parse_args()

    if args.action in ("space", "all"):
        if not args.space_id:
            print("[ERROR] --space-id wajib untuk aksi 'space'")
            sys.exit(1)
        push_space(
            space_id=args.space_id,
            token=args.token,
            folder=args.folder,
            commit_msg=args.commit_msg or "Update Batik Fusion Space",
        )

    if args.action in ("lora", "all"):
        if not args.repo_id or not args.file:
            print("[ERROR] --repo-id dan --file wajib untuk aksi 'lora'")
            sys.exit(1)
        push_lora(
            repo_id=args.repo_id,
            file=args.file,
            token=args.token,
            commit_msg=args.commit_msg or "Upload LoRA .safetensors",
        )


if __name__ == "__main__":
    main()
