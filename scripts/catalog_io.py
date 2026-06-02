#!/usr/bin/env python3
"""Parsing compartido del catálogo (SDD · Capa A).

Única fuente de la lógica que convierte un .md de catálogo en el objeto que
describe schemas/game.schema.yaml. Lo usan tanto validate_catalog.py (Paso 1)
como vectorize.py (Paso 2), así no se duplica ni diverge (DRY).

Decisión de formato (Paso 1): el ``summary`` es el CUERPO del .md, no un campo
del frontmatter. parse_game reconstruye ``{**frontmatter, "summary": <cuerpo>}``.
"""

from pathlib import Path

import yaml

# Rutas relativas a la raíz del repo (este módulo vive en scripts/).
REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "schemas" / "game.schema.yaml"
CATALOG_DIR = REPO_ROOT / "catalog"

FRONTMATTER_DELIM = "---"


def load_schema():
    """Carga el JSON Schema (escrito en YAML por legibilidad)."""
    with SCHEMA_PATH.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def parse_game(md_path):
    """Convierte un .md de catálogo en el objeto que describe el schema.

    Separa el frontmatter YAML del cuerpo y reconstruye el objeto del juego
    inyectando el cuerpo como ``summary``.
    """
    raw = md_path.read_text(encoding="utf-8")

    if not raw.lstrip().startswith(FRONTMATTER_DELIM):
        raise ValueError("falta el frontmatter YAML (no arranca con '---')")

    # Partimos en ['', frontmatter, cuerpo...]. maxsplit=2 preserva cualquier
    # '---' que aparezca dentro del cuerpo de la sinopsis.
    _, frontmatter_block, *body_parts = raw.split(FRONTMATTER_DELIM, 2)

    data = yaml.safe_load(frontmatter_block) or {}
    if not isinstance(data, dict):
        raise ValueError("el frontmatter no es un mapa YAML válido")

    # El cuerpo del .md ES la sinopsis. Pisa cualquier summary del frontmatter:
    # la única fuente de la sinopsis es el cuerpo del archivo.
    body = body_parts[0].strip() if body_parts else ""
    data["summary"] = body
    return data
