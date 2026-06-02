#!/usr/bin/env python3
"""Baja el modelo ONNX y su tokenizer si no están presentes (Paso 2).

Trae dos archivos del repo Xenova/all-MiniLM-L6-v2 en HuggingFace Hub:
  - onnx/model_quantized.onnx → models/model.onnx     (~23 MB, int8)
  - tokenizer.json            → models/tokenizer.json

Por qué el modelo QUANTIZED (int8) y por qué ESTE repo:
    Pesa ~23 MB (entra en el presupuesto de descarga del browser, Paso 4) y es
    EXACTAMENTE el mismo archivo que correrá en el navegador con onnxruntime-web.
    Mismo modelo en CI y en el cliente → mismo espacio semántico → comparaciones
    válidas (ver ADR-001).

Idempotente: si los archivos ya existen en models/, no vuelve a descargar.
"""

import os
import shutil
import sys
from pathlib import Path

# El cache de huggingface_hub usa symlinks; en Windows sin Developer Mode eso
# dispara un warning largo e inofensivo. Lo silenciamos para que la salida quede
# limpia (importa para la demo en vivo). Debe setearse ANTES de importar la lib.
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

from huggingface_hub import hf_hub_download  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ID = "Xenova/all-MiniLM-L6-v2"
REPO_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = REPO_ROOT / "models"

# (archivo remoto en el repo del Hub, nombre local en models/)
FILES = [
    ("onnx/model_quantized.onnx", "model.onnx"),
    ("tokenizer.json", "tokenizer.json"),
]


def download_one(remote_path, local_name):
    """Descarga models/<local_name> desde el Hub si todavía no está."""
    dest = MODELS_DIR / local_name
    if dest.exists():
        print(f"✓ {local_name} ya está ({dest.stat().st_size // 1024} KB); no se re-baja.")
        return

    print(f"↓ Bajando {remote_path} de {REPO_ID} ...")
    cached = hf_hub_download(repo_id=REPO_ID, filename=remote_path)
    shutil.copyfile(cached, dest)
    print(f"✓ {local_name} guardado ({dest.stat().st_size // 1024} KB).")


def main():
    MODELS_DIR.mkdir(exist_ok=True)
    for remote_path, local_name in FILES:
        download_one(remote_path, local_name)
    print("\nModelo y tokenizer listos en models/.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
