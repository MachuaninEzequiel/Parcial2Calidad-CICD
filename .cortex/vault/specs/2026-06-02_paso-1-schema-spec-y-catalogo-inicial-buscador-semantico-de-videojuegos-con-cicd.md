---
schema_version: 1
doc_type: spec
title: Paso 1 — Schema, Spec y Catálogo inicial (Buscador Semántico de Videojuegos
  con CI/CD)
created_at: '2026-06-02T15:56:37.931370Z'
updated_at: '2026-06-02T15:56:37.931370Z'
tags:
- spec
- sdd
- ci-cd
- paso-1
- schema
- catalogo
- json-schema
- validacion
- videojuegos
- greenfield
- embeddings
status: draft
links: []
vault_scope: local
fingerprint: d0b0a08dcf86a03f68823a428e99a827f2603b66f843e942f02ab9c9878be7ed
verification_hooks:
- name: validate-catalog-ok
  command: python scripts/validate_catalog.py
  required: true
  success_criteria: exit code 0 — los 8-10 catalog/*.md cumplen game.schema.yaml
  timeout_seconds: 120
- name: reject-malformed-md
  command: python scripts/validate_catalog.py --expect-fail tests/fixtures/invalid-game.md
  required: true
  success_criteria: exit code 0 — el validador rechaza el .md malformado (modo --expect-fail
    invierte el exit code)
  timeout_seconds: 120
- name: ruff-lint
  command: ruff check .
  required: false
  success_criteria: exit code 0 — el código Python pasa el linter
  timeout_seconds: 180
goal: 'Establecer la base Spec-Driven del proyecto: la estructura de carpetas, el
  schema estructural del ítem de catálogo (fuente de verdad de campos, géneros y plataformas),
  las expectativas declarativas de búsqueda, un catálogo inicial de 8-10 videojuegos
  en español con sinopsis ricas, un validador en Python que chequea cada .md contra
  el schema, y un README inicial que declara la postura SDD. Al cierre, el catálogo
  válido pasa la validación y un .md malformado de fixture la falla. NO se implementa
  vectorización ONNX, frontend ni CI todavía (eso es Paso 2 en adelante). Todo en
  español rioplatense (voseo), didáctico, pensado para una defensa oral de 5 minutos.'
files_in_scope:
- pyproject.toml
- .gitignore
- schemas/game.schema.yaml
- specs/search-expectations.yaml
- catalog/hollow-knight.md
- catalog/celeste.md
- catalog/overcooked-2.md
- catalog/gris.md
- catalog/journey.md
- catalog/firewatch.md
- catalog/disco-elysium.md
- catalog/witcher-3.md
- catalog/hades.md
- catalog/stardew-valley.md
- tests/fixtures/invalid-game.md
- scripts/validate_catalog.py
- README.md
constraints:
- 'Las decisiones de arquitectura de la sección 3 del brief están CERRADAS y no se
  re-discuten: videojuegos, sitio 100% estático sin backend, modelo ONNX all-MiniLM-L6-v2
  (384 dims), GitHub + GitHub Actions + GitHub Pages, Python, ruff, pytest, Docker,
  frontend HTML+JS vanilla, onnxruntime-web vía CDN, catálogo en español.'
- 'NO implementar en el Paso 1: descarga/uso del modelo ONNX, scripts/vectorize.py,
  scripts/download_model.py, embeddings.json, frontend (site/), ni .github/workflows/ci.yml.
  Eso es Paso 2 en adelante.'
- 'El modelo ONNX (~22 MB) NO se descarga ni se toca en este paso: cero descargas
  pesadas.'
- validate_catalog.py usa la librería jsonschema, NO shell-out a la CLI check-jsonschema;
  el mismo schema draft-07 se reutiliza con check-jsonschema en el CI del Paso 6,
  así que validación local y de CI chequean exactamente lo mismo.
- 'Sin dependencias innecesarias (sección 11 del brief): en este paso solo pyyaml
  + jsonschema.'
- El enum de géneros/plataformas vive SOLO en game.schema.yaml (única fuente de verdad);
  el frontend y los tests lo consumirán de ahí en pasos posteriores, no se hardcodea
  aparte.
- 'Avanzar paso a paso: al terminar el Paso 1, pausar y esperar confirmación del usuario
  antes del Paso 2. Cerrar la sesión con /cortex-documenter; si quedan verification
  hooks sin correr o archivos a medias, cerrar como ''handoff'', no ''closed''.'
acceptance_criteria:
- '`python scripts/validate_catalog.py` termina con exit code 0 cuando todos los catalog/*.md
  cumplen el schema.'
- '`python scripts/validate_catalog.py --expect-fail tests/fixtures/invalid-game.md`
  termina con exit code 0 (el validador detecta y reporta correctamente la violación
  de schema del .md malformado).'
- schemas/game.schema.yaml es un JSON Schema draft-07 válido y define géneros y plataformas
  como enum cerrado.
- specs/search-expectations.yaml tiene 4-6 expectativas y cada id en must_include_any_of
  existe como un archivo catalog/<id>.md.
- Hay entre 8 y 10 archivos .md en catalog/, todos pasan el schema, cada uno con summary
  de 80-1000 caracteres en español.
- README.md declara explícitamente la postura SDD y que schemas/ + specs/ son la fuente
  de verdad.
- '`ruff check .` y `ruff format --check .` pasan sobre validate_catalog.py (calidad
  de código; verificable una vez instalado ruff).'
---

## Goal

Establecer la base Spec-Driven del proyecto: la estructura de carpetas, el schema estructural del ítem de catálogo (fuente de verdad de campos, géneros y plataformas), las expectativas declarativas de búsqueda, un catálogo inicial de 8-10 videojuegos en español con sinopsis ricas, un validador en Python que chequea cada .md contra el schema, y un README inicial que declara la postura SDD. Al cierre, el catálogo válido pasa la validación y un .md malformado de fixture la falla. NO se implementa vectorización ONNX, frontend ni CI todavía (eso es Paso 2 en adelante). Todo en español rioplatense (voseo), didáctico, pensado para una defensa oral de 5 minutos.

## Requirements

- Crear la estructura de carpetas del Paso 1: schemas/, specs/, catalog/, scripts/, tests/fixtures/.
- schemas/game.schema.yaml: JSON Schema draft-07 escrito en YAML. required=[id,title,year,genres,summary]; additionalProperties=false. id: string slug kebab-case (pattern ^[a-z0-9-]+$). title: string 2-100. year: integer 1970-2030. genres: array 1-5 items, enum CERRADO [accion,aventura,rpg,indie,puzzle,terror,deportes,estrategia,simulacion,plataformas,shooter,casual,narrativo]. platforms: array, enum [pc,ps,xbox,switch,mobile]. summary: string 80-1000. Este enum es la ÚNICA fuente de verdad de géneros/plataformas (Capa C de SDD): no duplicarlo en código.
- specs/search-expectations.yaml: 4-6 expectativas, cada una con query (string), must_include_any_of (lista de ids de juegos) e in_top_k (int). TODOS los ids referenciados deben existir como catalog/<id>.md.
- catalog/*.md: 8-10 juegos en español con frontmatter YAML (id, title, year, genres, platforms) seguido de una sinopsis de ~150-300 palabras. Debe incluir al menos un id de cada must_include_any_of de las expectativas. CRÍTICO para la demo semántica del Paso 4: algunos summaries mencionan 'souls-like' literal y otros del mismo estilo NO, para que los embeddings demuestren valor sobre la búsqueda por palabra clave.
- tests/fixtures/invalid-game.md: un .md con frontmatter que viole el schema (ej. un género fuera del enum, o summary < 80 chars, o falta 'year') para el test negativo del validador.
- scripts/validate_catalog.py: lee schemas/game.schema.yaml, parsea el frontmatter YAML de cada .md y lo valida con la librería jsonschema (draft-07). Sin argumentos valida todos los catalog/*.md; con paths valida esos archivos; con flag --expect-fail INVIERTE el exit code (exit 0 si el target NO cumple el schema). Reporta OK/errores por archivo con mensajes claros. Comentarios que expliquen el 'por qué'.
- pyproject.toml: proyecto Python, dependencias mínimas (pyyaml + jsonschema) y config de ruff (line-length, target-version py311). Sin deps innecesarias; onnxruntime/numpy se agregan recién en Paso 2.
- .gitignore: ignora dist/, models/*.onnx, __pycache__/, .venv/, *.pyc.
- README.md inicial: título + descripción de una línea, qué es el proyecto, y la postura SDD (las tres capas) declarando explícitamente que schemas/ y specs/ son la fuente de verdad de la que derivan código y tests.
- Después del paso, producir un fragmento (~3 párrafos) para PRESENTACION.md que cubra el Paso 1 (requisito operativo del brief; el archivo PRESENTACION.md formal se consolida en el Paso 8).

## Files in Scope

- `pyproject.toml`
- `.gitignore`
- `schemas/game.schema.yaml`
- `specs/search-expectations.yaml`
- `catalog/hollow-knight.md`
- `catalog/celeste.md`
- `catalog/overcooked-2.md`
- `catalog/gris.md`
- `catalog/journey.md`
- `catalog/firewatch.md`
- `catalog/disco-elysium.md`
- `catalog/witcher-3.md`
- `catalog/hades.md`
- `catalog/stardew-valley.md`
- `tests/fixtures/invalid-game.md`
- `scripts/validate_catalog.py`
- `README.md`

## Constraints

- Las decisiones de arquitectura de la sección 3 del brief están CERRADAS y no se re-discuten: videojuegos, sitio 100% estático sin backend, modelo ONNX all-MiniLM-L6-v2 (384 dims), GitHub + GitHub Actions + GitHub Pages, Python, ruff, pytest, Docker, frontend HTML+JS vanilla, onnxruntime-web vía CDN, catálogo en español.
- NO implementar en el Paso 1: descarga/uso del modelo ONNX, scripts/vectorize.py, scripts/download_model.py, embeddings.json, frontend (site/), ni .github/workflows/ci.yml. Eso es Paso 2 en adelante.
- El modelo ONNX (~22 MB) NO se descarga ni se toca en este paso: cero descargas pesadas.
- validate_catalog.py usa la librería jsonschema, NO shell-out a la CLI check-jsonschema; el mismo schema draft-07 se reutiliza con check-jsonschema en el CI del Paso 6, así que validación local y de CI chequean exactamente lo mismo.
- Sin dependencias innecesarias (sección 11 del brief): en este paso solo pyyaml + jsonschema.
- El enum de géneros/plataformas vive SOLO en game.schema.yaml (única fuente de verdad); el frontend y los tests lo consumirán de ahí en pasos posteriores, no se hardcodea aparte.
- Avanzar paso a paso: al terminar el Paso 1, pausar y esperar confirmación del usuario antes del Paso 2. Cerrar la sesión con /cortex-documenter; si quedan verification hooks sin correr o archivos a medias, cerrar como 'handoff', no 'closed'.

## Acceptance Criteria

- [ ] `python scripts/validate_catalog.py` termina con exit code 0 cuando todos los catalog/*.md cumplen el schema.
- [ ] `python scripts/validate_catalog.py --expect-fail tests/fixtures/invalid-game.md` termina con exit code 0 (el validador detecta y reporta correctamente la violación de schema del .md malformado).
- [ ] schemas/game.schema.yaml es un JSON Schema draft-07 válido y define géneros y plataformas como enum cerrado.
- [ ] specs/search-expectations.yaml tiene 4-6 expectativas y cada id en must_include_any_of existe como un archivo catalog/<id>.md.
- [ ] Hay entre 8 y 10 archivos .md en catalog/, todos pasan el schema, cada uno con summary de 80-1000 caracteres en español.
- [ ] README.md declara explícitamente la postura SDD y que schemas/ + specs/ son la fuente de verdad.
- [ ] `ruff check .` y `ruff format --check .` pasan sobre validate_catalog.py (calidad de código; verificable una vez instalado ruff).

## Verification Hooks

Commands that objectively prove the work is done. Run by
`cortex finish-session` (Pluggable Middle, Phase 01).

### validate-catalog-ok
```bash
python scripts/validate_catalog.py
```

Success: exit code 0 — los 8-10 catalog/*.md cumplen game.schema.yaml · Timeout: 120s
### reject-malformed-md
```bash
python scripts/validate_catalog.py --expect-fail tests/fixtures/invalid-game.md
```

Success: exit code 0 — el validador rechaza el .md malformado (modo --expect-fail invierte el exit code) · Timeout: 120s
### ruff-lint *(optional)*
```bash
ruff check .
```

Success: exit code 0 — el código Python pasa el linter · Timeout: 180s
