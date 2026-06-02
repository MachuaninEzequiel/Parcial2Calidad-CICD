#!/usr/bin/env python3
"""Valida cada .md del catálogo contra schemas/game.schema.yaml.

SDD · Capa A en acción: este script es el guardián estructural del catálogo.
Usa el parsing compartido de catalog_io (parse_game + load_schema) y valida el
objeto resultante contra el schema con la librería jsonschema (draft-07).

Por qué la librería jsonschema y no la CLI check-jsonschema:
    Para que cualquiera corra la validación local sin instalar binarios extra.
    En el CI (Paso 6), check-jsonschema valida el MISMO schema draft-07, así que
    local y CI chequean exactamente lo mismo.

Uso:
    python scripts/validate_catalog.py                  # valida todo catalog/*.md
    python scripts/validate_catalog.py a.md b.md        # valida archivos puntuales
    python scripts/validate_catalog.py --expect-fail x  # test negativo (ver abajo)

El flag --expect-fail INVIERTE el código de salida: termina en 0 SOLO si el/los
archivo(s) NO cumplen el schema. Lo usa el verification hook del Paso 1 para
probar, de forma automatizable, que el validador efectivamente rechaza basura.
"""

import sys
from pathlib import Path

from catalog_io import CATALOG_DIR, load_schema, parse_game
from jsonschema import Draft7Validator

# Windows usa cp1252 en la consola por defecto y no puede imprimir los símbolos
# ✓/✗. Forzamos UTF-8 en la salida para que el script corra igual en cualquier
# plataforma (Windows local y el runner Linux del CI) sin configuración extra.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def validate_file(validator, md_path):
    """Devuelve la lista de errores de un archivo (vacía si es válido)."""
    try:
        game = parse_game(md_path)
    except ValueError as exc:
        return [str(exc)]

    # iter_errors junta TODAS las violaciones, no solo la primera: feedback útil.
    errors = sorted(validator.iter_errors(game), key=lambda e: list(e.path))
    return [_format_error(e) for e in errors]


def _format_error(error):
    location = ".".join(str(p) for p in error.path) or "(raíz)"
    return f"[{location}] {error.message}"


def collect_targets(args):
    """Resuelve qué archivos validar: los pasados por CLI, o todo el catálogo."""
    if args:
        return [Path(a) for a in args]
    return sorted(CATALOG_DIR.glob("*.md"))


def main(argv):
    expect_fail = "--expect-fail" in argv
    targets = collect_targets([a for a in argv if a != "--expect-fail"])

    if not targets:
        print("⚠ No se encontraron archivos .md para validar.")
        return 1

    validator = Draft7Validator(load_schema())

    failed = []
    for md_path in targets:
        errors = validate_file(validator, md_path)
        if errors:
            failed.append(md_path)
            print(f"✗ {md_path.name}")
            for err in errors:
                print(f"    {err}")
        else:
            print(f"✓ {md_path.name}")

    ok = len(targets) - len(failed)
    print(f"\n{ok}/{len(targets)} archivos válidos.")

    if expect_fail:
        # Modo test negativo: ÉXITO significa que el target NO cumple el schema.
        if failed:
            print("✓ --expect-fail: rechazado como se esperaba.")
            return 0
        print("✗ --expect-fail: se esperaba un rechazo, pero todo validó OK.")
        return 1

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
