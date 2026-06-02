#!/usr/bin/env python3
"""Genera la referencia DORADA de la equivalencia Python↔JS (Paso 4).

El corazón del Paso 4 es probar que el navegador vectoriza una query EXACTAMENTE
igual que el pipeline de Python del CI (riesgo #1 del ADR-001). Para eso, este
script calcula —del lado Python, con el MISMO modelo y tokenizer— el embedding de
un set FIJO de queries y lo escribe en tests/fixtures/query-vectors.reference.json.
Después, tests/equivalence/embed.equiv.test.mjs corre las MISMAS queries por
Transformers.js en Node y verifica que coinciden (diff < tolerancia) y que el
ranking top-k es idéntico.

DRY: reusa embed() + load_model() de vectorize.py. NO reescribe pooling/L2.

Las queries son las 5 de specs/search-expectations.yaml (las que tienen que andar
en la demo) + 1 corta de control ("hola") para cubrir un caso de pocos tokens.

Precisión: a diferencia de embeddings.json (que redondea a 8 decimales para que el
JSON sea liviano), acá escribimos los floats en FULL precision: la comparación a
1e-5 contra el lado JS necesita todos los dígitos.

Uso:
    python scripts/emit_reference_vectors.py   # genera el fixture; exit 0 si OK
"""

import json
import sys
from pathlib import Path

import yaml
from vectorize import EMBED_DIM, MODEL_NAME, embed, load_model

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
EXPECTATIONS_PATH = REPO_ROOT / "specs" / "search-expectations.yaml"
EMBEDDINGS_PATH = REPO_ROOT / "dist" / "embeddings.json"
OUTPUT_PATH = REPO_ROOT / "tests" / "fixtures" / "query-vectors.reference.json"

# Query corta de control: pocos tokens, sin relación semántica clara con el
# catálogo. Sirve para detectar divergencias de tokenización en casos chicos.
CONTROL_QUERY = "hola"

# Tolerancia OBJETIVO sobre el diff numérico (ver design doc / ADR-001). Si la
# corrida empírica del test JS no entra acá, se sube este número documentándolo,
# pero la identidad del ranking top-k NO se relaja. Es la fuente de verdad: el
# test JS lee la tolerancia desde el fixture.
TOLERANCE = 1e-5

TOP_K = 5


def load_queries():
    """Las 5 queries de la spec de búsqueda + 1 corta de control."""
    data = yaml.safe_load(EXPECTATIONS_PATH.read_text(encoding="utf-8"))
    queries = [e["query"] for e in data["expectations"]]
    queries.append(CONTROL_QUERY)
    return queries


def cosine_topk_ids(query_vector, items, k):
    """Rankea ids del catálogo por coseno (= producto punto: vectores L2=1).

    Devuelve los k ids con mayor similitud, de mayor a menor. Es la MISMA
    operación que topK() en search.mjs: el test JS debe reproducir esta lista
    idéntica (gate duro de la equivalencia).
    """
    scored = []
    for item in items:
        vec = item["vector"]
        dot = sum(q * v for q, v in zip(query_vector, vec, strict=True))
        scored.append((dot, item["id"]))
    # Orden estable: primero por score desc. Empata como JS (sort estable de V8).
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [item_id for _, item_id in scored[:k]]


def main():
    try:
        session, tokenizer, input_names = load_model()
    except FileNotFoundError as exc:
        print(f"✗ {exc}")
        return 1

    # CLAVE de la equivalencia (riesgo #1 del ADR-001): vectorizar la query SIN
    # padding, igual que el navegador.
    #
    # El tokenizer.json del modelo viene con padding fijo a 128 tokens, así que
    # vectorize.py (el catálogo, Paso 2) corre el modelo sobre secuencias de 128.
    # Transformers.js en el browser NO pad-ea: corre el modelo solo sobre los
    # tokens reales de la query. En un modelo int8, la cuantización dinámica de la
    # atención depende del LARGO de la secuencia, así que padded≠unpadded (medido:
    # ~3e-2 de diff, idéntico al diff Python-padded↔JS). Igualando a "sin padding"
    # de ambos lados, el diff cae a ~4e-8 (< 1e-5, dentro del objetivo).
    #
    # Esto reproduce EXACTAMENTE lo que pasa en producción: la query se vectoriza
    # en el browser (sin padding) y se rankea contra embeddings.json (el catálogo,
    # vectorizado con padding en el CI). NO tocamos vectorize.py: el Paso 2 queda
    # igual. La asimetría query/catálogo es la realidad del sistema, no un bug.
    tokenizer.no_padding()

    if not EMBEDDINGS_PATH.is_file():
        print(
            "✗ Falta dist/embeddings.json. Generalo con `python scripts/vectorize.py` "
            "antes de emitir los vectores de referencia (se necesita para el ranking)."
        )
        return 1

    embeddings = json.loads(EMBEDDINGS_PATH.read_text(encoding="utf-8"))
    items = embeddings["items"]

    queries = load_queries()
    out_queries = []
    for text in queries:
        vector = embed(text, session, tokenizer, input_names)
        vector_list = [float(x) for x in vector]  # full precision, sin redondeo
        top_k_ids = cosine_topk_ids(vector_list, items, TOP_K)
        out_queries.append(
            {
                "text": text,
                "vector": vector_list,
                "top_k_ids": top_k_ids,
            }
        )
        print(f"✓ \"{text}\" → vector de {len(vector_list)} dims · top-{TOP_K}: {top_k_ids}")

    payload = {
        "model": MODEL_NAME,
        "dimensions": EMBED_DIM,
        "tolerance": TOLERANCE,
        "queries": out_queries,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\n{len(out_queries)} queries de referencia → {OUTPUT_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
