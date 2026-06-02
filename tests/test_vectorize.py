"""Tests unitarios del Paso 2: funciones puras + estructura de embeddings.json.

Las pruebas de mean_pooling y l2_normalize NO requieren el modelo ONNX (son
funciones puras de numpy). La de estructura del JSON se saltea si todavía no se
corrió vectorize.py, para que `pytest` pase sin forzar una descarga de ~23 MB.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pytest

# vectorize.py vive en scripts/; lo agregamos al path para poder importarlo.
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from vectorize import EMBED_DIM, l2_normalize, mean_pooling  # noqa: E402

EMBEDDINGS_PATH = Path(__file__).resolve().parent.parent / "dist" / "embeddings.json"


def test_mean_pooling_ignora_padding():
    # 3 tokens de dim 2; el tercero es padding (mask=0) y NO debe contar.
    token_embeddings = np.array([[1.0, 1.0], [3.0, 3.0], [99.0, 99.0]])
    mask = np.array([1, 1, 0])
    pooled = mean_pooling(token_embeddings, mask)
    # Promedio de los dos tokens reales: (1+3)/2 = 2 en cada dimensión.
    assert np.allclose(pooled, [2.0, 2.0])


def test_l2_normalize_da_norma_unitaria():
    v = np.array([3.0, 4.0])  # norma 5
    out = l2_normalize(v)
    assert np.isclose(np.linalg.norm(out), 1.0, atol=1e-6)
    assert np.allclose(out, [0.6, 0.8])


def test_l2_normalize_vector_cero_no_explota():
    out = l2_normalize(np.zeros(4))
    assert np.allclose(out, np.zeros(4))  # no hay división por cero


@pytest.mark.skipif(not EMBEDDINGS_PATH.exists(), reason="dist/embeddings.json todavía no generado")
def test_estructura_embeddings_json():
    data = json.loads(EMBEDDINGS_PATH.read_text(encoding="utf-8"))
    assert data["dimensions"] == EMBED_DIM
    assert len(data["items"]) == 10
    for item in data["items"]:
        for key in ("id", "title", "year", "genres", "summary", "vector"):
            assert key in item, f"falta '{key}' en {item.get('id')}"
        assert len(item["vector"]) == EMBED_DIM
        norm = float(np.linalg.norm(item["vector"]))
        assert abs(norm - 1.0) < 1e-5, f"{item['id']} no está normalizado (norma={norm})"
