#!/usr/bin/env python3
"""Vectoriza el catálogo y genera dist/embeddings.json (Paso 2).

Pipeline por cada juego:
  1. parse_game → arma el texto: title + summary + genres.
  2. Tokeniza con el tokenizer de all-MiniLM-L6-v2 (WordPiece, max_len=128).
  3. Corre el modelo ONNX → token embeddings (last_hidden_state).
  4. MEAN POOLING ponderado por attention_mask (promedia solo tokens reales,
     ignora el padding; NO usa el token CLS).
  5. NORMALIZACIÓN L2 → vector unitario de 384 dims.

Por qué mean pooling + L2:
    all-MiniLM-L6-v2 (sentence-transformers) produce el significado de la
    oración promediando los embeddings de sus tokens, no leyendo el CLS.
    Normalizar a L2=1 hace que la similitud coseno sea un simple producto
    punto: barato y estable.

CRÍTICO: el Paso 4 replica EXACTAMENTE estos dos pasos en JavaScript. Por eso
mean_pooling() y l2_normalize() son funciones puras y autocontenidas.
"""

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import onnxruntime as ort
from catalog_io import CATALOG_DIR, parse_game
from tokenizers import Tokenizer

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = REPO_ROOT / "models" / "model.onnx"
TOKENIZER_PATH = REPO_ROOT / "models" / "tokenizer.json"
OUTPUT_PATH = REPO_ROOT / "dist" / "embeddings.json"

MODEL_NAME = "all-MiniLM-L6-v2"
MAX_LENGTH = 128
EMBED_DIM = 384


def build_text(game):
    """Texto que se vectoriza: título + sinopsis + géneros, en ese orden."""
    genres = " ".join(game.get("genres", []))
    return f"{game['title']} {game['summary']} {genres}"


def mean_pooling(token_embeddings, attention_mask):
    """Promedia los embeddings de tokens ponderando por la máscara.

    token_embeddings: array (n_tokens, dim) — salida del modelo.
    attention_mask:   array (n_tokens,)     — 1 en tokens reales, 0 en padding.

    Suma solo los tokens reales y divide por su cantidad: el padding no aporta.
    Es la misma operación que se replica en JS en el Paso 4.
    """
    mask = attention_mask.astype(np.float32)[:, None]  # (n_tokens, 1)
    summed = (token_embeddings * mask).sum(axis=0)  # (dim,)
    count = np.clip(mask.sum(axis=0), 1e-9, None)  # evita división por cero
    return summed / count


def l2_normalize(vector):
    """Escala el vector a norma euclidiana 1 (el vector cero queda igual)."""
    norm = np.linalg.norm(vector)
    if norm < 1e-12:
        return vector
    return vector / norm


def embed(text, session, tokenizer, input_names):
    """Texto → vector de 384 dims (mean pooling + L2)."""
    enc = tokenizer.encode(text)
    input_ids = np.array([enc.ids], dtype=np.int64)
    attention_mask = np.array([enc.attention_mask], dtype=np.int64)

    # Pasamos solo los inputs que el modelo declara (algunos exports ONNX no
    # incluyen token_type_ids).
    feed = {"input_ids": input_ids, "attention_mask": attention_mask}
    if "token_type_ids" in input_names:
        feed["token_type_ids"] = np.zeros_like(input_ids)

    token_embeddings = session.run(None, feed)[0][0]  # (n_tokens, dim)
    pooled = mean_pooling(token_embeddings, np.array(enc.attention_mask))
    return l2_normalize(pooled)


def main():
    if not MODEL_PATH.exists() or not TOKENIZER_PATH.exists():
        print("✗ Falta el modelo o el tokenizer. Corré: python scripts/download_model.py")
        return 1

    session = ort.InferenceSession(str(MODEL_PATH), providers=["CPUExecutionProvider"])
    input_names = {i.name for i in session.get_inputs()}
    tokenizer = Tokenizer.from_file(str(TOKENIZER_PATH))
    tokenizer.enable_truncation(max_length=MAX_LENGTH)

    items = []
    for md_path in sorted(CATALOG_DIR.glob("*.md")):
        game = parse_game(md_path)
        vector = embed(build_text(game), session, tokenizer, input_names)
        items.append(
            {
                "id": md_path.stem,
                "title": game["title"],
                "year": game["year"],
                "genres": game["genres"],
                "summary": game["summary"],
                "vector": [round(float(x), 8) for x in vector],
            }
        )
        print(f"✓ {md_path.stem} → vector de {len(vector)} dims")

    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    payload = {
        "model": MODEL_NAME,
        "dimensions": EMBED_DIM,
        "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "items": items,
    }
    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n{len(items)} juegos vectorizados → {OUTPUT_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
