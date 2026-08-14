# -*- coding: utf-8 -*-
"""
lora_generator.py
=================
Modul untuk memuat model **SDXL** + LoRA joint-training (kohya-ss) dan
melakukan image generation untuk fitur Cultural Fusion.

Pendekatan loader: pakai `networks.lora_diffusers` dari kohya-ss/sd-scripts
(WAJIB untuk SDXL 2 text encoder — loader bawaan diffusers masih buggy).

Pendekatan sumber LoRA:
  - `HF_LORA_REPO_ID` + `HF_LORA_FILENAME` -> otomatis di-download
    dari Hugging Face Hub lewat `huggingface_hub`.
  - Atau path lokal di filesystem.

Fallback generator sintetis tetap ada untuk mode demo tanpa GPU / tanpa
library diffusers.
"""

from __future__ import annotations

import os
import glob
import shutil
from pathlib import Path
from typing import Optional, Tuple, List

import numpy as np
from PIL import Image


# -------------------------------------------------------------------
# Deteksi library ML
# -------------------------------------------------------------------
try:
    import torch
    DIFFUSERS_TERSEDIA = True
except Exception:
    DIFFUSERS_TERSEDIA = False
    torch = None  # type: ignore


# -------------------------------------------------------------------
# Konfigurasi default untuk SDXL + LoRA batik joint training
# -------------------------------------------------------------------
# Base model SDXL (WAJIB sama dengan training, beda -> LoRA tidak berguna)
DEFAULT_BASE_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"

# VAE fp16-fix (WAJIB, mencegah NaN/gambar flat - sesuai notebook testing)
DEFAULT_VAE = "madebyollin/sdxl-vae-fp16-fix"

# Default scheduler (sama dengan di notebook training)
DEFAULT_SCHEDULER = "euler_a"  # DPMSolverMultistepScheduler di-convert otomatis


# -------------------------------------------------------------------
# Cache pipeline + network
# -------------------------------------------------------------------
_PIPELINE = None
_NETWORK = None
_LORA_PATH_SAAT_INI = None


# -------------------------------------------------------------------
# Utilitas: cari & download LoRA
# -------------------------------------------------------------------
def _cari_lora_lokal(patterns: Optional[List[str]] = None) -> Optional[str]:
    """Cari file .safetensors di filesystem lokal."""
    if patterns is None:
        patterns = ["*.safetensors", "**/*.safetensors"]
    semua: List[str] = []
    for pola in patterns:
        semua.extend(glob.glob(pola, recursive=True))
    if not semua:
        return None
    # Prioritaskan yang mengandung 'joint-lora' atau 'lora' di nama
    for kandidat in semua:
        nama = Path(kandidat).name.lower()
        if "joint-lora" in nama or ("lora" in nama and "madura" in nama):
            return kandidat
    return semua[0]


def download_lora_dari_hf(
    repo_id: str,
    filename: str,
    cache_dir: str = "./.lora-cache",
    token: Optional[str] = None,
) -> str:
    """
    Download file LoRA dari Hugging Face Hub.
    Mengembalikan path lokal (cached) ke file .safetensors.

    Contoh:
        download_lora_dari_hf(
            "username/batik-joint-lora",
            "madura-jawa_barat-joint-lora-000004.safetensors"
        )
    """
    try:
        from huggingface_hub import hf_hub_download
    except ImportError as e:
        raise RuntimeError(
            "Library 'huggingface_hub' belum terinstall. "
            "Tambahkan `huggingface_hub` ke requirements.txt lalu "
            "`pip install huggingface_hub`."
        ) from e

    os.makedirs(cache_dir, exist_ok=True)
    print(f"[lora_generator] Mendownload {filename} dari {repo_id} ...")
    local_path = hf_hub_download(
        repo_id=repo_id,
        filename=filename,
        cache_dir=cache_dir,
        token=token or os.environ.get("HF_TOKEN"),
    )
    print(f"[lora_generator] Tersimpan di: {local_path}")
    return local_path


def resolve_lora_path(
    lora_path: Optional[str] = None,
    hf_repo_id: Optional[str] = None,
    hf_filename: Optional[str] = None,
) -> Optional[str]:
    """
    Resolver path LoRA dengan prioritas:
      1. `lora_path` eksplisit (kalau ada di disk)
      2. `hf_repo_id` + `hf_filename` -> download dari HuggingFace
      3. Cari otomatis di filesystem lokal
      4. None (mode sintetis)
    """
    # 1) Path eksplisit
    if lora_path and os.path.isfile(lora_path):
        return lora_path

    # 2) Download dari HuggingFace
    if hf_repo_id and hf_filename:
        try:
            return download_lora_dari_hf(hf_repo_id, hf_filename)
        except Exception as e:
            print(f"[lora_generator] Gagal download dari HF: {e}")

    # 3) Cari lokal
    found = _cari_lora_lokal()
    if found:
        return found

    return None


# -------------------------------------------------------------------
# Setup pipeline SDXL + loader LoRA kohya-ss
# -------------------------------------------------------------------
def _setup_loader_kohya(repo_path: str = "/kaggle/working/sd-scripts",
                        local_path: str = "./sd-scripts"):
    """
    Menyiapkan loader LoRA native kohya-ss. Clone repo kalau belum ada.

    Untuk deployment HuggingFace Spaces, repo ini akan di-skip dan
    kita pakai fallback path `local_path` di Space (jika ada).
    """
    # Coba pakai path lokal dulu (untuk HF Spaces yang menyertakan file ini)
    target = local_path if os.path.isdir(local_path) else repo_path
    if not os.path.isdir(target):
        # Coba clone (hanya untuk environment dengan internet + git)
        import subprocess
        try:
            print(f"[lora_generator] Cloning sd-scripts ke {target} ...")
            subprocess.run(
                ["git", "clone", "--depth", "1",
                 "https://github.com/kohya-ss/sd-scripts.git", target],
                check=True, timeout=120,
            )
        except Exception as e:
            raise RuntimeError(
                f"Tidak bisa menemukan/meng-clone sd-scripts: {e}\n"
                "Pastikan folder `sd-scripts/` ada di root Space, atau "
                "library `networks.lora_diffusers` sudah terinstall."
            ) from e
    if target not in os.sys.path:
        import sys
        sys.path.insert(0, target)
    return target


def _muat_pipeline_sdxl(base_model: str = DEFAULT_BASE_MODEL,
                         vae_id: str = DEFAULT_VAE,
                         dtype=None):
    """Muat pipeline SDXL dengan VAE fp16-fix."""
    global _PIPELINE
    if _PIPELINE is not None:
        return _PIPELINE

    if not DIFFUSERS_TERSEDIA:
        raise RuntimeError("torch/diffusers tidak tersedia.")

    from diffusers import StableDiffusionXLPipeline, AutoencoderKL
    if dtype is None:
        dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    print(f"[lora_generator] Memuat VAE fp16-fix: {vae_id} ...")
    fixed_vae = AutoencoderKL.from_pretrained(vae_id, torch_dtype=dtype)

    print(f"[lora_generator] Memuat SDXL pipeline: {base_model} ...")
    pipe = StableDiffusionXLPipeline.from_pretrained(
        base_model,
        vae=fixed_vae,
        torch_dtype=dtype,
        variant="fp16",
        use_safetensors=True,
    )
    pipe.set_progress_bar_config(disable=True)
    if torch.cuda.is_available():
        pipe = pipe.to("cuda")
        try:
            pipe.enable_xformers_memory_efficient_attention()
        except Exception:
            pass
    else:
        pipe = pipe.to("cpu")

    _PIPELINE = pipe
    return pipe


def _muat_lora_kohya(lora_path: str, multiplier: float = 1.0):
    """Muat LoRA via loader native kohya-ss (create_network_from_weights)."""
    global _NETWORK, _LORA_PATH_SAAT_INI
    if _NETWORK is not None and _LORA_PATH_SAAT_INI == lora_path:
        return _NETWORK

    # 1) Pastikan sd-scripts tersedia
    try:
        _setup_loader_kohya()
    except Exception as e:
        print(f"[lora_generator] Peringatan setup kohya: {e}")
        raise

    # 2) Import modul kohya
    try:
        from networks.lora_diffusers import create_network_from_weights
    except Exception as e:
        raise RuntimeError(
            f"Gagal import networks.lora_diffusers: {e}\n"
            "Pastikan repo `kohya-ss/sd-scripts` sudah ter-clone dan "
            "ada di sys.path."
        ) from e

    from safetensors.torch import load_file

    # 3) Muat pipeline kalau belum
    pipe = _muat_pipeline_sdxl()

    # 4) Buat network dari file LoRA
    text_encoders = [pipe.text_encoder, pipe.text_encoder_2]
    lora_sd = load_file(lora_path)
    network = create_network_from_weights(
        text_encoders, pipe.unet, lora_sd, multiplier=multiplier
    )
    network.load_state_dict(lora_sd)
    if torch.cuda.is_available():
        network.to("cuda", dtype=pipe.unet.dtype)

    _NETWORK = network
    _LORA_PATH_SAAT_INI = lora_path
    return network


# -------------------------------------------------------------------
# Generator utama: SDXL + LoRA
# -------------------------------------------------------------------
def generate_batik_dengan_lora(
    prompt: str,
    negative_prompt: str = "blurry, low quality, deformed, watermark, text, extra limbs, distorted pattern",
    lora_path: Optional[str] = None,
    hf_repo_id: Optional[str] = None,
    hf_filename: Optional[str] = None,
    lora_scale: float = 1.0,
    num_steps: int = 30,
    guidance: float = 7.0,
    ukuran: int = 1024,           # SDXL default 1024
    seed: int = -1,
    base_model: str = DEFAULT_BASE_MODEL,
) -> Image.Image:
    """
    Hasilkan gambar batik pakai SDXL + LoRA joint-training.
    Mengikuti pola dari `testing2daerah (3).ipynb`:
      - Base: stabilityai/stable-diffusion-xl-base-1.0
      - VAE: madebyollin/sdxl-vae-fp16-fix
      - Loader: networks.lora_diffusers.create_network_from_weights
    """
    if not DIFFUSERS_TERSEDIA:
        return _generate_sintetis(prompt, ukuran)

    # Resolve path LoRA (download dari HF kalau perlu)
    resolved = resolve_lora_path(lora_path, hf_repo_id, hf_filename)
    if resolved is None:
        print("[lora_generator] Tidak ada LoRA; pakai generator sintetis.")
        return _generate_sintetis(prompt, ukuran)

    try:
        pipe = _muat_pipeline_sdxl(base_model=base_model)
        network = _muat_lora_kohya(resolved, multiplier=lora_scale)

        # Merge LoRA -> generate -> restore (sesuai pola notebook testing)
        applied = False
        if lora_scale != 0:
            network.set_multiplier(lora_scale)
            network.merge_to()
            applied = True

        try:
            gen_device = "cuda" if torch.cuda.is_available() else "cpu"
            generator = torch.Generator(device=gen_device)
            if seed and seed > 0:
                generator.manual_seed(int(seed))

            image = pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                num_inference_steps=num_steps,
                guidance_scale=guidance,
                height=ukuran,
                width=ukuran,
                generator=generator,
            ).images[0]
        finally:
            if applied:
                network.restore_from()

        return image

    except Exception as e:
        print(f"[lora_generator] Gagal generate dengan SDXL+LoRA: {e}\n"
              f"Traceback akan diloncati -> fallback sintetis.")
        return _generate_sintetis(prompt, ukuran)


# -------------------------------------------------------------------
# Generator sintetis (fallback tanpa GPU / diffusers / LoRA)
# -------------------------------------------------------------------
def _hash_dari_string(s: str) -> int:
    h = 0
    for c in s:
        h = (h * 31 + ord(c)) & 0xFFFFFFFF
    return h


def _generate_sintetis(prompt: str, ukuran: int = 512) -> Image.Image:
    """Hasilkan gambar batik sintetis deterministik dari prompt (untuk demo UI)."""
    rng = np.random.default_rng(_hash_dari_string(prompt) & 0x7FFFFFFF)
    palet_kandidat = [
        ("#8B4513", "#D2691E", "#F4A460"),   # coklat soga klasik
        ("#1e3a8a", "#fbbf24", "#dc2626"),   # biru-emas-merah (Madura/keraton)
        ("#064e3b", "#facc15", "#7f1d1d"),   # hijau-emas-merah tua
        ("#312e81", "#e11d48", "#fde047"),   # indigo-magenta-kuning
        ("#0f766e", "#f97316", "#fef3c7"),   # teal-orange-ivory
    ]
    palet = palet_kandidat[_hash_dari_string(prompt) % len(palet_kandidat)]
    warna_hex = []
    for h in palet:
        h = h.lstrip("#")
        warna_hex.append([int(h[i:i+2], 16) for i in (0, 2, 4)])
    warna_hex = np.array(warna_hex, dtype=np.uint8)

    canvas = np.full((ukuran, ukuran, 3), 250, dtype=np.uint8)
    yy, xx = np.mgrid[0:ukuran, 0:ukuran].astype(np.float32)
    cx, cy = ukuran / 2, ukuran / 2
    r = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    r_norm = r / r.max()
    base = (warna_hex[2] * (1 - r_norm[..., None]) +
            warna_hex[0] * r_norm[..., None] * 0.4 + 200).astype(np.uint8)
    canvas = base

    num_motif = 5
    for layer in range(num_motif):
        scale = 1.0 - layer * 0.15
        warna = warna_hex[layer % len(warna_hex)]
        n = 6 + layer * 2
        for i in range(n):
            sudut = (2 * np.pi * i / n) + layer * 0.3
            r_jari = ukuran * 0.18 * scale
            cx_l = int(ukuran / 2 + r_jari * np.cos(sudut))
            cy_l = int(ukuran / 2 + r_jari * np.sin(sudut))
            jari = int(ukuran * (0.10 - layer * 0.012))
            cv_circle = np.zeros_like(canvas)
            _gambar_lingkaran(cv_circle, (cx_l, cy_l), jari, warna.tolist())
            mask = cv_circle.sum(axis=2) > 0
            canvas[mask] = (canvas[mask] * 0.4 + cv_circle[mask] * 0.6).astype(np.uint8)

    n_titik = 800
    ys = rng.integers(0, ukuran, n_titik)
    xs = rng.integers(0, ukuran, n_titik)
    for y, x in zip(ys, xs):
        canvas[y, x] = warna_hex[rng.integers(0, len(warna_hex))]

    border = 6
    canvas[:border, :] = warna_hex[0] // 2
    canvas[-border:, :] = warna_hex[0] // 2
    canvas[:, :border] = warna_hex[0] // 2
    canvas[:, -border:] = warna_hex[0] // 2

    return Image.fromarray(canvas)


def _gambar_lingkaran(canvas, center, radius, color):
    H, W = canvas.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    dist = np.sqrt((xx - center[0]) ** 2 + (yy - center[1]) ** 2)
    mask = dist <= radius
    canvas[mask] = color
    mask_edge = (dist > radius) & (dist <= radius + 1.5)
    if mask_edge.any():
        alpha = np.clip(1.0 - (dist[mask_edge] - radius) / 1.5, 0, 1)
        for c in range(3):
            canvas[mask_edge, c] = (
                canvas[mask_edge, c] * (1 - alpha) + color[c] * alpha
            ).astype(np.uint8)


# -------------------------------------------------------------------
# Cleanup utility (untuk Space yang perlu hemat memori)
# -------------------------------------------------------------------
def bersihkan_pipeline():
    """Bebaskan VRAM dengan unload pipeline + LoRA."""
    global _PIPELINE, _NETWORK, _LORA_PATH_SAAT_INI
    try:
        if _NETWORK is not None:
            del _NETWORK
            _NETWORK = None
        if _PIPELINE is not None:
            del _PIPELINE
            _PIPELINE = None
        if DIFFUSERS_TERSEDIA and torch.cuda.is_available():
            torch.cuda.empty_cache()
        _LORA_PATH_SAAT_INI = None
    except Exception:
        pass
