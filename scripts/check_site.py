#!/usr/bin/env python3
"""Chequeo estructural del sitio estático (Paso 3).

Verifica, sin levantar un navegador, que el frontend tiene todo lo que necesita:
los archivos del sitio existen, index.html referencia sus assets y —si está
disponible— dist/embeddings.json cumple el contrato esperado (model, dimensions
== 384, items con vector de 384). Es el guardián portable del Paso 3, el análogo
de validate_catalog.py para el frontend.

Python ya es dependencia del proyecto, así que no agrega nada nuevo (el brief
pide cero dependencias superfluas).

embeddings.json es gitignored (lo genera el Paso 2): si NO está, avisamos pero
NO fallamos por eso. Dónde vive al publicar es responsabilidad del build (Paso 6).

Uso:
    python scripts/check_site.py     # exit 0 si todo OK; exit 1 + lista si falta algo
"""

import json
import re
import sys
from pathlib import Path

# Windows usa cp1252 en consola y no puede imprimir ✓/✗. Forzamos UTF-8 en la
# salida para que el script corra igual en cualquier plataforma (Windows local y
# el runner Linux del CI) sin configuración extra. Mismo patrón que los demás
# scripts del proyecto.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_DIR = REPO_ROOT / "site"
EMBEDDINGS_PATH = REPO_ROOT / "dist" / "embeddings.json"

# Archivos que el sitio DEBE tener.
REQUIRED_FILES = [
    SITE_DIR / "index.html",
    SITE_DIR / "css" / "styles.css",
    SITE_DIR / "js" / "search.mjs",
    SITE_DIR / "js" / "app.mjs",
    SITE_DIR / "js" / "search.test.mjs",
    SITE_DIR / "js" / "vectorizer.mjs",  # Paso 4: vectorización en el browser
]

# Referencias que index.html debe incluir (substring check, no parseo de HTML).
REQUIRED_REFERENCES = [
    "css/styles.css",
    "js/app.mjs",
]

EXPECTED_DIMENSIONS = 384


def check_required_files(problems):
    """Verifica que existan todos los archivos del sitio."""
    for path in REQUIRED_FILES:
        rel = path.relative_to(REPO_ROOT).as_posix()
        if path.is_file():
            print(f"✓ {rel}")
        else:
            print(f"✗ falta {rel}")
            problems.append(f"falta el archivo {rel}")


def check_index_references(problems):
    """Verifica que index.html referencie sus assets (CSS + módulo ES)."""
    index = SITE_DIR / "index.html"
    if not index.is_file():
        # Ya se reportó como archivo faltante; no duplicamos el error.
        return

    html = index.read_text(encoding="utf-8")
    for ref in REQUIRED_REFERENCES:
        if ref in html:
            print(f"✓ index.html referencia {ref}")
        else:
            print(f"✗ index.html no referencia {ref}")
            problems.append(f"index.html no referencia {ref}")


def check_free_query_enabled(problems):
    """Verifica que la búsqueda por texto libre esté HABILITADA (Paso 4).

    Checks portables (con `re`, sin parsear HTML de verdad):
      - el <input id="free-query"> ya NO tiene el atributo `disabled`.
      - hay un <script type="importmap"> (wiring de Transformers.js → CDN).
      - ya no aparece la nota '🔒 Disponible en el Paso 4'.
    """
    index = SITE_DIR / "index.html"
    if not index.is_file():
        return  # ya se reportó como faltante

    html = index.read_text(encoding="utf-8")

    # Extraer el tag completo del input de la query (sin importar el orden de los
    # atributos) y chequear que no esté deshabilitado.
    match = re.search(r"<input\b[^>]*\bid=[\"']free-query[\"'][^>]*>", html, re.DOTALL)
    if not match:
        print("✗ index.html no tiene el <input id=\"free-query\">")
        problems.append("falta el input de búsqueda por texto libre")
    elif re.search(r"\bdisabled\b", match.group(0)):
        print("✗ la caja de texto libre sigue deshabilitada (tiene `disabled`)")
        problems.append("el input free-query sigue deshabilitado")
    else:
        print("✓ index.html: la caja de texto libre está habilitada")

    if re.search(r"<script\b[^>]*type=[\"']importmap[\"']", html):
        print("✓ index.html declara el import map (Transformers.js → CDN)")
    else:
        print("✗ index.html no declara el import map de Transformers.js")
        problems.append("falta el <script type=\"importmap\"> en index.html")

    if "Disponible en el Paso 4" in html:
        print("✗ index.html todavía dice 'Disponible en el Paso 4'")
        problems.append("la nota '🔒 Disponible en el Paso 4' sigue presente")
    else:
        print("✓ index.html: ya no aparece la nota '🔒 Disponible en el Paso 4'")


def check_embeddings(problems):
    """Valida el contrato de dist/embeddings.json SI existe (gitignored)."""
    if not EMBEDDINGS_PATH.is_file():
        print(
            "⚠ dist/embeddings.json no está (es gitignored). "
            "Generalo con `python scripts/vectorize.py` para la demo. "
            "No es un error del Paso 3."
        )
        return

    try:
        data = json.loads(EMBEDDINGS_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"✗ dist/embeddings.json no se pudo leer: {exc}")
        problems.append(f"embeddings.json ilegible: {exc}")
        return

    if "model" in data:
        print(f"✓ embeddings.json: model = {data['model']}")
    else:
        print("✗ embeddings.json no tiene la clave 'model'")
        problems.append("embeddings.json sin clave 'model'")

    dims = data.get("dimensions")
    if dims == EXPECTED_DIMENSIONS:
        print(f"✓ embeddings.json: dimensions = {dims}")
    else:
        print(f"✗ embeddings.json: dimensions = {dims} (se esperaba {EXPECTED_DIMENSIONS})")
        problems.append(f"dimensions = {dims}, se esperaba {EXPECTED_DIMENSIONS}")

    items = data.get("items")
    if not items:
        print("✗ embeddings.json no tiene items")
        problems.append("embeddings.json sin items")
        return

    print(f"✓ embeddings.json: {len(items)} items")

    first_vector = items[0].get("vector")
    if isinstance(first_vector, list) and len(first_vector) == EXPECTED_DIMENSIONS:
        print(f"✓ embeddings.json: el primer item tiene vector de {EXPECTED_DIMENSIONS}")
    else:
        got = len(first_vector) if isinstance(first_vector, list) else type(first_vector).__name__
        print(f"✗ embeddings.json: el primer item tiene vector inválido ({got})")
        problems.append(f"vector del primer item inválido ({got})")


def main():
    problems = []

    check_required_files(problems)
    check_index_references(problems)
    check_free_query_enabled(problems)
    check_embeddings(problems)

    print()
    if problems:
        print(f"✗ {len(problems)} problema(s) en el sitio:")
        for p in problems:
            print(f"    - {p}")
        return 1

    print("✓ El sitio estático está completo y coherente.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
