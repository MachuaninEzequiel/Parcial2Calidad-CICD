#!/usr/bin/env bash
# Entrypoint del contenedor (Paso 7). Despacha por subcomando. REUSA los mismos
# scripts/comandos que el CI (.github/workflows/ci.yml) y el dev local — acá NO
# se reimplementa nada de la lógica del proyecto.
#
#   ci         pipeline completo (paridad con GitHub Actions). Es el default.
#   vectorize  regenera dist/embeddings.json (montá un volumen para sacarlo).
#   reference  regenera dist/embeddings.json + el fixture dorado de equivalencia
#              (tests/fixtures/query-vectors.reference.json) DENTRO de Linux, para
#              que los artefactos golden se generen en el MISMO SO que el CI de
#              GitHub Actions (ubuntu) y no haya deriva numérica Windows↔Ubuntu en
#              el top-k. Montá volúmenes sobre dist/ y tests/fixtures/ para sacarlos.
#   serve      sirve el sitio estático en :8000 (http://localhost:8000/site/).
set -euo pipefail

run_ci() {
  # MISMO orden que el workflow del Paso 6. Falla (set -e) si un gate falla.
  python scripts/download_model.py
  ruff check .
  python scripts/validate_catalog.py
  python scripts/validate_catalog.py --expect-fail tests/fixtures/invalid-game.md
  python scripts/vectorize.py
  python -m pytest tests/ -q
  python scripts/check_site.py
  node --test site/js/search.test.mjs
  node --test tests/equivalence/embed.equiv.test.mjs
}

usage() {
  echo "Uso: docker run [...] <imagen> [ci|vectorize|reference|serve]" >&2
  echo "  ci         pipeline completo (paridad con el CI). Default." >&2
  echo "  vectorize  regenera dist/embeddings.json." >&2
  echo "  reference  regenera dist/embeddings.json + el fixture dorado (Linux-origin)." >&2
  echo "  serve      sirve el sitio en :8000 (http://localhost:8000/site/)." >&2
}

cmd="${1:-ci}"
case "$cmd" in
  ci)
    run_ci
    ;;
  vectorize)
    python scripts/vectorize.py
    ;;
  reference)
    # Genera los artefactos golden EN LINUX (mismo SO que el CI). El orden
    # importa: emit_reference_vectors.py lee dist/embeddings.json para calcular el
    # top-k de referencia, así que primero vectorizamos el catálogo.
    python scripts/vectorize.py
    python scripts/emit_reference_vectors.py
    ;;
  serve)
    # Si todavía no hay embeddings (p. ej. se montó un dist/ vacío), los generamos.
    if [ ! -f dist/embeddings.json ]; then
      echo "dist/embeddings.json no está; generándolo antes de servir..." >&2
      python scripts/vectorize.py
    fi
    # exec: que http.server reciba las señales (Ctrl+C corta limpio).
    exec python -m http.server 8000
    ;;
  help | -h | --help)
    usage
    ;;
  *)
    echo "Subcomando desconocido: '$cmd'. Corriendo 'ci' por defecto." >&2
    usage
    run_ci
    ;;
esac
