"""Tests de REGRESIÓN SEMÁNTICA del Paso 5 — derivados de la spec (Capa B).

Esta es la red de seguridad que cierra el loop SDD del proyecto: las
expectativas declarativas de ``specs/search-expectations.yaml`` (Capa B) se
convierten, en runtime, en un test parametrizado (un caso por expectativa). Si
un cambio en el catálogo degrada el ranking de una query que antes andaba bien,
estos tests lo frenan en el CI.

Cómo funciona cada caso:
  1. Vectoriza la query reusando ``embed()`` + ``load_model()`` de
     ``scripts/vectorize.py`` (DRY: no se reescribe ni pooling ni L2).
  2. Vectoriza la query SIN padding (``tokenizer.no_padding()``) para reproducir
     EXACTO el régimen del navegador (ADR-002): la query se vectoriza en vivo en
     el browser sin relleno, el catálogo se precomputó con padding en el CI. Como
     ambos lados están L2-normalizados y se comparan por coseno, el ranking es
     estable pese a la asimetría.
  3. Rankea contra ``dist/embeddings.json`` por coseno = producto punto (los
     vectores ya están L2-normalizados).
  4. Toma el top-k (k = ``in_top_k`` de la expectativa, default 5) y exige que la
     intersección con ``must_include_any_of`` NO sea vacía.

No hay falso verde: si falta ``models/`` o ``dist/embeddings.json`` se hace
``pytest.skip`` con una razón ACCIONABLE (qué comando correr). Un skip queda
visible en el reporte; nunca pasa por verde silencioso.

La calidad semántica se logra afinando el CONTENIDO del catálogo en español
(ADR-003), no cambiando el modelo (all-MiniLM-L6-v2 int8, ADR-001) ni traduciendo
la query a inglés.
"""

import json
import sys
from pathlib import Path

import pytest
import yaml

# vectorize.py vive en scripts/; lo agregamos al path para reusar embed/load_model
# (mismo patrón de import que tests/test_vectorize.py).
REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from vectorize import embed, load_model  # noqa: E402

EXPECTATIONS_PATH = REPO_ROOT / "specs" / "search-expectations.yaml"
EMBEDDINGS_PATH = REPO_ROOT / "dist" / "embeddings.json"
CATALOG_DIR = REPO_ROOT / "catalog"

DEFAULT_TOP_K = 5


def load_expectations():
    """Lee las expectativas de la spec (Capa B) en runtime.

    Devuelve la lista cruda de dicts ``{query, must_include_any_of, in_top_k?}``.
    """
    data = yaml.safe_load(EXPECTATIONS_PATH.read_text(encoding="utf-8"))
    return data["expectations"]


EXPECTATIONS = load_expectations()


def cosine_topk(query_vector, items, k):
    """Rankea ids del catálogo por coseno (= producto punto: vectores L2=1).

    Misma operación que cosine_topk_ids() de emit_reference_vectors.py y topK()
    de search.mjs: devuelve los k ids con mayor similitud, de mayor a menor, con
    su score, para poder armar un mensaje de fallo legible.
    """
    scored = []
    for item in items:
        vec = item["vector"]
        dot = sum(q * v for q, v in zip(query_vector, vec, strict=True))
        scored.append((dot, item["id"]))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return scored[:k]


@pytest.fixture(scope="module")
def ranker():
    """Carga modelo + tokenizer (sin padding) + catálogo UNA vez por módulo.

    Si falta el modelo o el catálogo vectorizado, hace skip con una razón
    accionable: NUNCA un falso verde silencioso. Vectorizar la query sin padding
    (tokenizer.no_padding()) reproduce el régimen del navegador (ADR-002).
    """
    try:
        session, tokenizer, input_names = load_model()
    except FileNotFoundError as exc:
        pytest.skip(
            f"Falta el modelo ONNX ({exc}). Corré: python scripts/download_model.py"
        )

    if not EMBEDDINGS_PATH.is_file():
        pytest.skip(
            "Falta dist/embeddings.json. Generalo con: python scripts/vectorize.py"
        )

    # CLAVE (ADR-002): la query se vectoriza SIN padding, igual que el browser.
    tokenizer.no_padding()

    embeddings = json.loads(EMBEDDINGS_PATH.read_text(encoding="utf-8"))
    items = embeddings["items"]

    def rank(query, k):
        vector = [float(x) for x in embed(query, session, tokenizer, input_names)]
        return cosine_topk(vector, items, k)

    return rank


@pytest.mark.parametrize(
    "expectation",
    EXPECTATIONS,
    ids=[e["query"] for e in EXPECTATIONS],
)
def test_expectativa_de_busqueda(ranker, expectation):
    """Para cada expectativa de la spec: must_include_any_of ∩ top_k ≠ ∅."""
    query = expectation["query"]
    expected = expectation["must_include_any_of"]
    k = expectation.get("in_top_k", DEFAULT_TOP_K)

    top = ranker(query, k)
    top_ids = [item_id for _, item_id in top]

    hit = set(top_ids) & set(expected)
    if not hit:
        ranking_legible = ", ".join(
            f"{item_id} ({score:.3f})" for score, item_id in top
        )
        pytest.fail(
            f"Regresión semántica para la query {query!r}:\n"
            f"  esperaba alguno de: {expected}\n"
            f"  top-{k} real:        {ranking_legible}\n"
            f"  → ninguno de los esperados entró en el top-{k}. "
            f"Afiná el summary en español del catálogo (ADR-003), "
            f"no debilites specs/search-expectations.yaml."
        )


def test_regla_del_yaml_ids_existen_en_catalogo():
    """REGLA de la spec: cada id de must_include_any_of existe como catalog/<id>.md.

    Esto protege contra typos en la spec (un id mal escrito jamás entraría al
    top-k y daría un rojo críptico). Es un check estructural puro: no necesita el
    modelo, así que corre siempre (no se saltea).
    """
    huerfanos = []
    for expectation in EXPECTATIONS:
        for game_id in expectation["must_include_any_of"]:
            if not (CATALOG_DIR / f"{game_id}.md").is_file():
                huerfanos.append((expectation["query"], game_id))

    assert not huerfanos, (
        "Hay ids en search-expectations.yaml sin catalog/<id>.md:\n"
        + "\n".join(f"  query {q!r} → falta catalog/{gid}.md" for q, gid in huerfanos)
    )
