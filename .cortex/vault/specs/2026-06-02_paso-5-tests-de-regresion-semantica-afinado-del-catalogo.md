---
schema_version: 1
doc_type: spec
title: Paso 5 — Tests de regresión semántica + afinado del catálogo
created_at: '2026-06-02T20:20:21.922234Z'
updated_at: '2026-06-02T20:20:21.922234Z'
tags:
- spec
- spec
- sdd
- ci-cd
- paso-5
- regresion-semantica
- search-expectations
- catalogo
- embeddings
- pytest
- espanol
- adr-003
- adr-002
status: draft
links: []
vault_scope: local
fingerprint: e4f8c8ea314818ba41dc0d29bcc5dc14e20c605c0f369a017069f940b9887117
verification_hooks:
- name: semantic-regression
  command: python -m pytest tests/ -q
  required: true
  success_criteria: exit code 0 — las 5 expectativas de search-expectations.yaml pasan
    (must_include_any_of en top_k) y los tests unitarios del Paso 2 (mean_pooling/l2_normalize/estructura)
    siguen verdes. Requiere models/ + dist/embeddings.json regenerado.
  timeout_seconds: 300
- name: equivalence-still-green
  command: node --test tests/equivalence/embed.equiv.test.mjs
  required: true
  success_criteria: exit code 0 — tras re-emitir el fixture, el vector JS sigue coincidiendo
    con la referencia Python (<1e-5) y el ranking top-k es idéntico con el catálogo
    nuevo. Requiere npm install + modelo accesible.
  timeout_seconds: 600
- name: js-pure-functions
  command: node --test site/js/search.test.mjs
  required: true
  success_criteria: exit code 0 — cosineSimilarity y topK siguen correctas y search.mjs
    sigue puro (sin dependencias).
  timeout_seconds: 180
- name: catalog-still-green
  command: python scripts/validate_catalog.py
  required: true
  success_criteria: exit code 0 — los summaries editados siguen cumpliendo el schema
    (80-1000 chars, géneros del enum).
  timeout_seconds: 120
- name: site-structure
  command: python scripts/check_site.py
  required: true
  success_criteria: exit code 0 — el sitio sigue coherente y dist/embeddings.json
    (regenerado) tiene dimensions==384.
  timeout_seconds: 120
- name: ruff-lint
  command: ruff check .
  required: false
  success_criteria: exit code 0 — código Python limpio (incl. tests/test_search_regression.py).
  timeout_seconds: 180
goal: 'Cerrar el loop de regresión semántica del proyecto: agregar el test de regresión
  que DERIVA de specs/search-expectations.yaml (Capa B → tests) y afinar los summaries
  del catálogo en español para que, con el MISMO modelo chico de inglés (all-MiniLM-L6-v2
  int8, ADR-001), las 5 queries de la spec devuelvan los juegos esperados en su top-k.
  El test es un pytest parametrizado que lee el YAML en runtime, vectoriza cada query
  SIN padding (mismo régimen que el browser, ADR-002) reusando embed() de vectorize.py,
  rankea contra dist/embeddings.json y exige que must_include_any_of caiga en el top-k.
  La calidad se logra afinando el CONTENIDO en español (ADR-003), no cambiando el
  modelo ni traduciendo queries. Tras editar el catálogo se re-vectoriza (dist/embeddings.json)
  y se re-emite el fixture del Paso 4 (query-vectors.reference.json), manteniendo
  VERDE la equivalencia Python↔JS. Se alinean las docs: la demo estrella "juego para
  jugar con amigos en el sillón" → Overcooked 2 pasa de aspiracional a REAL. Español
  rioplatense, didáctico, para la defensa oral de 5 min.'
files_in_scope:
- tests/test_search_regression.py
- catalog/overcooked-2.md
- catalog/hollow-knight.md
- dist/embeddings.json
- tests/fixtures/query-vectors.reference.json
- README.md
- PRESENTACION.md
- specs/search-expectations.yaml
constraints:
- 'Modelo FIJO: all-MiniLM-L6-v2 int8 quantized (ADR-001). NO cambiar de modelo (ADR-003):
  la calidad semántica se logra afinando el CONTENIDO del catálogo en español, no
  cambiando el modelo ni traduciendo la query a inglés.'
- 'Reescribir summaries en español NATURAL, rico y honesto (rioplatense, didáctico),
  respetando el género real del juego y el schema (summary minLength 80, maxLength
  1000). PROHIBIDO keyword-stuffing o repetir la query literal: el ranking debe lograrse
  con prosa bien alineada (el experimento del Paso 4 confirmó que alcanza con texto
  natural).'
- 'NO debilitar specs/search-expectations.yaml para forzar verde: las expectativas
  son Capa B (fuente de verdad). El gate se pasa tuneando el catálogo.'
- 'DRY: el test de regresión reusa embed()/load_model() de vectorize.py y vectoriza
  la query SIN padding (tokenizer.no_padding()) para reproducir el browser (ADR-002).
  No reescribe pooling/L2 ni la lógica de ranking si puede reusarla.'
- 'Mantener VERDE todo lo de Pasos 1-4: validate_catalog.py, la equivalencia Python↔JS
  (re-emitir el fixture tras re-vectorizar), search.mjs puro (node --test site/js/search.test.mjs)
  y check_site.py.'
- Re-vectorizar (python scripts/vectorize.py) y re-emitir el fixture (python scripts/emit_reference_vectors.py)
  DESPUÉS de editar el catálogo; embeddings.json sigue 10×384.
- 'FUERA de alcance: .github/workflows/ci.yml (Paso 6), Docker (Paso 7), el motor
  de ranking (search.mjs) y vectorizer.mjs. NO se toca el modelo, download_model.py
  ni vectorize.py (salvo reuso read-only de embed/load_model desde el test).'
- 'Avanzar paso a paso: al terminar el Paso 5, pausar y esperar confirmación del usuario
  antes del Paso 6. Cerrar con /cortex-documenter; si alguna expectativa required
  no entra o queda algo a medias, cerrar como ''handoff'', no ''closed''.'
- Español rioplatense (voseo), didáctico, pensado para la defensa oral de 5 min.
acceptance_criteria:
- 'Las 5 expectativas de specs/search-expectations.yaml pasan: para cada query, must_include_any_of
  ∩ top_k (k=in_top_k) ≠ ∅, rankeando la query vectorizada SIN padding contra dist/embeddings.json.'
- 'En particular: ''juego para jugar con amigos en el sillón'' devuelve overcooked-2
  en el top-5, y ''souls-like para principiantes'' devuelve hollow-knight en el top-5.'
- tests/test_search_regression.py existe, es pytest parametrizado que LEE search-expectations.yaml
  en runtime (un caso por expectativa) y reusa embed() de vectorize.py (no duplica
  pooling/L2). `python -m pytest tests/` termina exit 0.
- Los summaries editados (overcooked-2, hollow-knight) siguen cumpliendo el schema
  → `python scripts/validate_catalog.py` exit 0.
- dist/embeddings.json regenerado (10 items × 384 dims) y tests/fixtures/query-vectors.reference.json
  re-emitido; `node --test tests/equivalence/embed.equiv.test.mjs` sigue exit 0 (ranking
  identity con el catálogo nuevo).
- 'search.mjs sigue puro: `node --test site/js/search.test.mjs` exit 0. `python scripts/check_site.py`
  exit 0.'
- README 'Estado actual' refleja Pasos 1-5 y el headline (línea 5) ahora es real;
  PRESENTACION tiene el fragmento del Paso 5.
- NO se debilitaron las expectativas de search-expectations.yaml para forzar verde.
- 'Nada pesado commiteado: models/, dist/ y node_modules/ siguen gitignored.'
---

## Goal

Cerrar el loop de regresión semántica del proyecto: agregar el test de regresión que DERIVA de specs/search-expectations.yaml (Capa B → tests) y afinar los summaries del catálogo en español para que, con el MISMO modelo chico de inglés (all-MiniLM-L6-v2 int8, ADR-001), las 5 queries de la spec devuelvan los juegos esperados en su top-k. El test es un pytest parametrizado que lee el YAML en runtime, vectoriza cada query SIN padding (mismo régimen que el browser, ADR-002) reusando embed() de vectorize.py, rankea contra dist/embeddings.json y exige que must_include_any_of caiga en el top-k. La calidad se logra afinando el CONTENIDO en español (ADR-003), no cambiando el modelo ni traduciendo queries. Tras editar el catálogo se re-vectoriza (dist/embeddings.json) y se re-emite el fixture del Paso 4 (query-vectors.reference.json), manteniendo VERDE la equivalencia Python↔JS. Se alinean las docs: la demo estrella "juego para jugar con amigos en el sillón" → Overcooked 2 pasa de aspiracional a REAL. Español rioplatense, didáctico, para la defensa oral de 5 min.

## Requirements

- tests/test_search_regression.py (NUEVO): pytest PARAMETRIZADO que lee specs/search-expectations.yaml en runtime (un caso de test por expectativa). Por cada expectativa: vectoriza la query con embed() reusado de scripts/vectorize.py + tokenizer.no_padding() (régimen browser, ADR-002), rankea contra dist/embeddings.json por coseno (producto punto, vectores L2-normalizados), toma el top-k (= in_top_k de la expectativa, default 5) y ASSERT que la intersección con must_include_any_of no es vacía. Mensaje de fallo claro: qué query, qué juegos esperaba, qué top-k salió. Reusar load_model() de vectorize.py. Si falta models/ o dist/embeddings.json, fallar con mensaje accionable (o skip con reason explícito) — NUNCA falso verde silencioso. Incluir además un test que valide la REGLA del YAML: cada id en must_include_any_of existe como catalog/<id>.md.
- catalog/overcooked-2.md (EDITAR el summary): reescribir en español natural y rico para que LIDERE con el ángulo social-couch de la query ('jugar con amigos en el sillón', cooperativo local, multijugador en el mismo sillón, partidas en grupo), sin perder qué es el juego (cocina caótica contrarreloj). Objetivo medible: overcooked-2 entra al top-5 de 'juego para jugar con amigos en el sillón'. Respetar schema (summary 80-1000 chars). NADA de keyword-stuffing ni repetir la query literal.
- catalog/hollow-knight.md (EDITAR el summary): reforzar en español natural el ángulo 'souls-like accesible / desafiante pero justo / para quien arranca en el género' sin perder su identidad metroidvania. Objetivo medible: hollow-knight entra al top-5 de 'souls-like para principiantes', sin romper 'plataformas con dificultad muy alta' (donde también es esperado). Respetar schema.
- dist/embeddings.json (REGENERAR, no editar a mano): correr `python scripts/vectorize.py` tras editar el catálogo. Debe seguir con 10 items × 384 dims, L2-normalizados. Gitignored.
- tests/fixtures/query-vectors.reference.json (RE-EMITIR): correr `python scripts/emit_reference_vectors.py` tras re-vectorizar. Cambian los top_k_ids (catálogo nuevo); los vectores de las queries NO cambian (las queries son las mismas). El test de equivalencia del Paso 4 debe seguir exit 0.
- README.md (EDITAR): 'Estado actual' → Pasos 1-5 (red de regresión semántica andando; el catálogo afinado hace que la búsqueda por texto libre devuelva lo esperado). Confirmar que la línea 5 (headline sillón→Overcooked 2) ahora es REAL. Sumar tests/test_search_regression.py a la estructura del repo. Aclarar que el CI (Paso 6) correrá estos tests.
- PRESENTACION.md (EDITAR/append): fragmento del Paso 5 (~3 párrafos): la red de regresión semántica que nace de search-expectations.yaml (Capa B → tests), por qué se afinó el CONTENIDO del catálogo en español en vez de cambiar el modelo (ADR-003), y la demo en vivo: ahora 'juego para jugar con amigos en el sillón' devuelve Overcooked 2. Revisar el fragmento del Paso 4 para que ya no suene aspiracional.
- specs/search-expectations.yaml (FUENTE DE VERDAD, NO debilitar): sólo se puede tocar para AGREGAR expectativas o corregir un id mal escrito; NUNCA para relajar una expectativa que no entra. El gate se pasa tuneando el catálogo, no la spec.

## Files in Scope

- `tests/test_search_regression.py`
- `catalog/overcooked-2.md`
- `catalog/hollow-knight.md`
- `dist/embeddings.json`
- `tests/fixtures/query-vectors.reference.json`
- `README.md`
- `PRESENTACION.md`
- `specs/search-expectations.yaml`

## Constraints

- Modelo FIJO: all-MiniLM-L6-v2 int8 quantized (ADR-001). NO cambiar de modelo (ADR-003): la calidad semántica se logra afinando el CONTENIDO del catálogo en español, no cambiando el modelo ni traduciendo la query a inglés.
- Reescribir summaries en español NATURAL, rico y honesto (rioplatense, didáctico), respetando el género real del juego y el schema (summary minLength 80, maxLength 1000). PROHIBIDO keyword-stuffing o repetir la query literal: el ranking debe lograrse con prosa bien alineada (el experimento del Paso 4 confirmó que alcanza con texto natural).
- NO debilitar specs/search-expectations.yaml para forzar verde: las expectativas son Capa B (fuente de verdad). El gate se pasa tuneando el catálogo.
- DRY: el test de regresión reusa embed()/load_model() de vectorize.py y vectoriza la query SIN padding (tokenizer.no_padding()) para reproducir el browser (ADR-002). No reescribe pooling/L2 ni la lógica de ranking si puede reusarla.
- Mantener VERDE todo lo de Pasos 1-4: validate_catalog.py, la equivalencia Python↔JS (re-emitir el fixture tras re-vectorizar), search.mjs puro (node --test site/js/search.test.mjs) y check_site.py.
- Re-vectorizar (python scripts/vectorize.py) y re-emitir el fixture (python scripts/emit_reference_vectors.py) DESPUÉS de editar el catálogo; embeddings.json sigue 10×384.
- FUERA de alcance: .github/workflows/ci.yml (Paso 6), Docker (Paso 7), el motor de ranking (search.mjs) y vectorizer.mjs. NO se toca el modelo, download_model.py ni vectorize.py (salvo reuso read-only de embed/load_model desde el test).
- Avanzar paso a paso: al terminar el Paso 5, pausar y esperar confirmación del usuario antes del Paso 6. Cerrar con /cortex-documenter; si alguna expectativa required no entra o queda algo a medias, cerrar como 'handoff', no 'closed'.
- Español rioplatense (voseo), didáctico, pensado para la defensa oral de 5 min.

## Acceptance Criteria

- [ ] Las 5 expectativas de specs/search-expectations.yaml pasan: para cada query, must_include_any_of ∩ top_k (k=in_top_k) ≠ ∅, rankeando la query vectorizada SIN padding contra dist/embeddings.json.
- [ ] En particular: 'juego para jugar con amigos en el sillón' devuelve overcooked-2 en el top-5, y 'souls-like para principiantes' devuelve hollow-knight en el top-5.
- [ ] tests/test_search_regression.py existe, es pytest parametrizado que LEE search-expectations.yaml en runtime (un caso por expectativa) y reusa embed() de vectorize.py (no duplica pooling/L2). `python -m pytest tests/` termina exit 0.
- [ ] Los summaries editados (overcooked-2, hollow-knight) siguen cumpliendo el schema → `python scripts/validate_catalog.py` exit 0.
- [ ] dist/embeddings.json regenerado (10 items × 384 dims) y tests/fixtures/query-vectors.reference.json re-emitido; `node --test tests/equivalence/embed.equiv.test.mjs` sigue exit 0 (ranking identity con el catálogo nuevo).
- [ ] search.mjs sigue puro: `node --test site/js/search.test.mjs` exit 0. `python scripts/check_site.py` exit 0.
- [ ] README 'Estado actual' refleja Pasos 1-5 y el headline (línea 5) ahora es real; PRESENTACION tiene el fragmento del Paso 5.
- [ ] NO se debilitaron las expectativas de search-expectations.yaml para forzar verde.
- [ ] Nada pesado commiteado: models/, dist/ y node_modules/ siguen gitignored.

## Verification Hooks

Commands that objectively prove the work is done. Run by
`cortex finish-session` (Pluggable Middle, Phase 01).

### semantic-regression
```bash
python -m pytest tests/ -q
```

Success: exit code 0 — las 5 expectativas de search-expectations.yaml pasan (must_include_any_of en top_k) y los tests unitarios del Paso 2 (mean_pooling/l2_normalize/estructura) siguen verdes. Requiere models/ + dist/embeddings.json regenerado. · Timeout: 300s
### equivalence-still-green
```bash
node --test tests/equivalence/embed.equiv.test.mjs
```

Success: exit code 0 — tras re-emitir el fixture, el vector JS sigue coincidiendo con la referencia Python (<1e-5) y el ranking top-k es idéntico con el catálogo nuevo. Requiere npm install + modelo accesible. · Timeout: 600s
### js-pure-functions
```bash
node --test site/js/search.test.mjs
```

Success: exit code 0 — cosineSimilarity y topK siguen correctas y search.mjs sigue puro (sin dependencias). · Timeout: 180s
### catalog-still-green
```bash
python scripts/validate_catalog.py
```

Success: exit code 0 — los summaries editados siguen cumpliendo el schema (80-1000 chars, géneros del enum). · Timeout: 120s
### site-structure
```bash
python scripts/check_site.py
```

Success: exit code 0 — el sitio sigue coherente y dist/embeddings.json (regenerado) tiene dimensions==384. · Timeout: 120s
### ruff-lint *(optional)*
```bash
ruff check .
```

Success: exit code 0 — código Python limpio (incl. tests/test_search_regression.py). · Timeout: 180s
