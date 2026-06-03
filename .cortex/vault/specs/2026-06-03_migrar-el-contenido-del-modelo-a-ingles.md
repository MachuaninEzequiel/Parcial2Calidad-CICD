---
schema_version: 1
doc_type: spec
title: Migrar el contenido del modelo a inglés
created_at: '2026-06-03T01:51:00.711445Z'
updated_at: '2026-06-03T01:51:00.711445Z'
tags:
- spec
- spec
- sdd
- ci-cd
- ingles
- catalogo
- schema
- generos
- search-expectations
- re-vectorizar
- modelo
- adr-003
- calidad-busqueda
status: draft
links: []
vault_scope: local
fingerprint: 9994de14ca3329e58af1b42ac41f82cb0b2ce5db08b742cdcbf69f9f634f180e
verification_hooks:
- name: schema-english
  command: python -c "import yaml;e=yaml.safe_load(open('schemas/game.schema.yaml',encoding='utf-8'))['properties']['genres']['items']['enum'];assert
    'action' in e and 'accion' not in e and 'horror' in e;print('enum de generos en
    ingles OK')"
  required: true
  success_criteria: exit code 0 — el enum de géneros del schema está en inglés (action/horror
    presentes, accion ausente).
  timeout_seconds: 60
- name: catalog-valid
  command: python scripts/validate_catalog.py
  required: true
  success_criteria: exit code 0 — los 10 .md validan contra el schema nuevo (genres
    ingleses, sinopsis 80-1000).
  timeout_seconds: 120
- name: semantic-regression
  command: python -m pytest tests/ -q
  required: true
  success_criteria: exit code 0 — las 5 expectativas (queries inglesas) pasan + units
    del Paso 2. Requiere models/ + dist/embeddings.json regenerado.
  timeout_seconds: 300
- name: equivalence
  command: node --test tests/equivalence/embed.equiv.test.mjs
  required: true
  success_criteria: exit code 0 — equivalencia Python↔JS sigue verde tras re-vectorizar
    y re-emitir el fixture (diff < tolerancia + top-k como conjunto). Requiere npm
    install + modelo.
  timeout_seconds: 600
- name: js-pure-functions
  command: node --test site/js/search.test.mjs
  required: true
  success_criteria: exit code 0 — search.mjs sigue puro y correcto.
  timeout_seconds: 180
- name: site-structure
  command: python scripts/check_site.py
  required: true
  success_criteria: exit code 0 — el sitio sigue coherente; embeddings.json 384 dims.
  timeout_seconds: 120
- name: ruff-lint
  command: ruff check .
  required: false
  success_criteria: exit code 0 — código Python limpio.
  timeout_seconds: 180
goal: 'Alinear el IDIOMA DEL CONTENIDO al modelo de IA local (all-MiniLM-L6-v2, que
  es de inglés) para que la búsqueda por texto libre funcione bien, manteniendo el
  modelo chico de 23MB en vez de cambiar a uno multilingüe pesado. Diagnóstico que
  lo motiva: con queries en español el modelo no discrimina (casi toda query devuelve
  disco-elysium/gris); con queries en inglés ya mejora (''relaxing farming game''
  → stardew-valley #1, que en español ni aparecía). Se migra a INGLÉS sólo lo que
  impacta al modelo: las sinopsis de los 10 catalog/*.md, el enum de géneros del schema
  (Capa A) + el campo genres de los .md, las 5 queries de search-expectations.yaml,
  y el ejemplo/placeholder de búsqueda en index.html. Quedan en ESPAÑOL (no impactan
  al modelo): README.md, PRESENTACION.md y el chrome de UI. Después se re-vectoriza,
  se re-emite el fixture de equivalencia y se re-valida todo. El modelo, el pipeline
  (vectorize/equivalencia), download_model.py, vectorizer.mjs y la arquitectura NO
  cambian. Esta decisión amienda/supersede el ADR-003 (afinar el catálogo en español
  sólo parcheaba 5 queries; el fix real es alinear el idioma del contenido al modelo).'
files_in_scope:
- schemas/game.schema.yaml
- catalog/celeste.md
- catalog/disco-elysium.md
- catalog/firewatch.md
- catalog/gris.md
- catalog/hades.md
- catalog/hollow-knight.md
- catalog/journey.md
- catalog/overcooked-2.md
- catalog/stardew-valley.md
- catalog/witcher-3.md
- specs/search-expectations.yaml
- site/index.html
- dist/embeddings.json
- tests/fixtures/query-vectors.reference.json
- README.md
- PRESENTACION.md
constraints:
- 'Sólo va a INGLÉS el contenido que IMPACTA AL MODELO: sinopsis del catálogo, enum
  de géneros + campo genres, queries de las expectativas, y el ejemplo de búsqueda
  de la UI. README.md, PRESENTACION.md y el chrome de UI quedan en ESPAÑOL (la defensa
  oral es en español).'
- El modelo (all-MiniLM-L6-v2 int8, 23MB), el pipeline (vectorize.py/emit_reference_vectors.py/equivalencia),
  download_model.py, site/js/vectorizer.mjs, site/js/search.mjs y la arquitectura
  NO cambian. Es una migración de CONTENIDO + el enum de Capa A; cero cambio de modelo
  o de lógica.
- 'Cambio ATÓMICO de Capa A: el enum de géneros del schema y el campo genres de los
  10 .md se editan JUNTOS (additionalProperties:false + enum cerrado → si no matchean,
  validate_catalog falla).'
- Las sinopsis en inglés deben ser naturales, ricas y distintivas (no traducción literal
  pobre, sin keyword-stuffing), respetando minLength 80 / maxLength 1000.
- 'NO debilitar specs/search-expectations.yaml: las expectativas (must_include_any_of)
  son Capa B / fuente de verdad. Si una query no entra, afinar la sinopsis inglesa
  del juego, NO relajar la expectativa.'
- 'Mantener VERDE todo: validate_catalog.py (schema nuevo), equivalencia Python↔JS
  (re-emitir fixture; sigue < tolerancia + ranking como conjunto), regresión semántica
  (queries inglesas), check_site.py, ruff. Re-vectorizar y re-emitir el fixture DESPUÉS
  de editar catálogo+schema.'
- Esta decisión AMIENDA/SUPERSEDE el ADR-003 (de 'afinar el catálogo en español' a
  'alinear el idioma del contenido al modelo = inglés'). El documenter registra el
  ADR/decision nuevo al cierre.
- 'Nada pesado commiteado: models/, dist/, node_modules/ siguen gitignored. Español
  rioplatense en README/PRESENTACION; inglés natural en catálogo/queries.'
acceptance_criteria:
- El enum de géneros de schemas/game.schema.yaml está en inglés (action/horror/platformer/etc.,
  sin los slugs en español); los 10 catalog/*.md tienen `genres` con los slugs ingleses
  y la sinopsis en inglés (80-1000 chars). `python scripts/validate_catalog.py` exit
  0.
- specs/search-expectations.yaml tiene las 5 queries en inglés; los `must_include_any_of`
  (ids) y los in_top_k intactos; NO debilitadas.
- 'La búsqueda por texto libre mejora: las 5 expectativas pasan (`python -m pytest
  tests/` exit 0) y queries arbitrarias en inglés devuelven resultados con sentido
  (verificable, ej. ''relaxing farming game'' → stardew-valley en top-5).'
- dist/embeddings.json regenerado (10×384) y tests/fixtures/query-vectors.reference.json
  re-emitido; `node --test tests/equivalence/embed.equiv.test.mjs` exit 0.
- 'site/index.html: el ejemplo/placeholder de búsqueda está en inglés; el chrome (títulos,
  footer) sigue en español. `python scripts/check_site.py` exit 0. `node --test site/js/search.test.mjs`
  exit 0.'
- README (en español) con ejemplos de query en inglés + la decisión de idioma aclarada;
  PRESENTACION (en español) con la demo phrase en inglés + el párrafo de la decisión.
- El modelo, download_model.py, vectorizer.mjs, search.mjs y la arquitectura NO cambiaron.
  Nada pesado commiteado (models/, dist/, node_modules/ gitignored).
---

## Goal

Alinear el IDIOMA DEL CONTENIDO al modelo de IA local (all-MiniLM-L6-v2, que es de inglés) para que la búsqueda por texto libre funcione bien, manteniendo el modelo chico de 23MB en vez de cambiar a uno multilingüe pesado. Diagnóstico que lo motiva: con queries en español el modelo no discrimina (casi toda query devuelve disco-elysium/gris); con queries en inglés ya mejora ('relaxing farming game' → stardew-valley #1, que en español ni aparecía). Se migra a INGLÉS sólo lo que impacta al modelo: las sinopsis de los 10 catalog/*.md, el enum de géneros del schema (Capa A) + el campo genres de los .md, las 5 queries de search-expectations.yaml, y el ejemplo/placeholder de búsqueda en index.html. Quedan en ESPAÑOL (no impactan al modelo): README.md, PRESENTACION.md y el chrome de UI. Después se re-vectoriza, se re-emite el fixture de equivalencia y se re-valida todo. El modelo, el pipeline (vectorize/equivalencia), download_model.py, vectorizer.mjs y la arquitectura NO cambian. Esta decisión amienda/supersede el ADR-003 (afinar el catálogo en español sólo parcheaba 5 queries; el fix real es alinear el idioma del contenido al modelo).

## Requirements

- schemas/game.schema.yaml (EDITAR — Capa A): traducir el enum cerrado de géneros al inglés: accion→action, aventura→adventure, rpg→rpg, indie→indie, puzzle→puzzle, terror→horror, deportes→sports, estrategia→strategy, simulacion→simulation, plataformas→platformer, shooter→shooter, casual→casual, narrativo→narrative. Actualizar la description de `summary` ('Sinopsis rica en español' → inglés). NO cambiar platforms (pc/ps/xbox/switch/mobile ya universales), ni additionalProperties:false, ni required, ni longitudes (summary 80-1000).
- catalog/*.md (EDITAR los 10: celeste, disco-elysium, firewatch, gris, hades, hollow-knight, journey, overcooked-2, stardew-valley, witcher-3): traducir la SINOPSIS (cuerpo del .md) a inglés natural, rico y distintivo (respetando 80-1000 chars; sin traducción literal pobre ni keyword-stuffing) y actualizar el campo `genres` del frontmatter a los slugs ingleses nuevos. Los `id`, `title` (ya inglés), `year` y `platforms` NO cambian. CAMBIO ATÓMICO con el schema: los genres deben matchear el enum nuevo o validate_catalog falla.
- specs/search-expectations.yaml (EDITAR): traducir las 5 `query` a inglés natural (ej. 'souls-like for beginners', 'couch co-op game to play with friends', 'short emotional indie game with a story', 'rpg with choices that matter', 'very hard platformer'). Los `must_include_any_of` (ids/slugs de juegos) y los `in_top_k` NO cambian. NO debilitar las expectativas: si una no entra, afinar la sinopsis inglesa del juego, no relajar la expectativa.
- site/index.html (EDITAR): poner el ejemplo/placeholder de la caja de búsqueda en INGLÉS (ej. 'couch co-op game to play with friends') para guiar queries en inglés. El chrome de UI (títulos de sección, footer, notas) queda en ESPAÑOL. Los chips de género se renderean solos desde los datos (app.mjs no hardcodea géneros), así que se actualizan al cambiar los .md — no hace falta tocar app.mjs salvo algún string de ejemplo de query.
- dist/embeddings.json (REGENERAR): correr `python scripts/vectorize.py` tras editar catálogo + schema. Sigue 10 items × 384 dims. Gitignored.
- tests/fixtures/query-vectors.reference.json (RE-EMITIR): correr `python scripts/emit_reference_vectors.py` tras re-vectorizar (las queries del fixture salen de search-expectations.yaml, ahora en inglés). La equivalencia debe seguir verde.
- README.md (EDITAR, queda en ESPAÑOL): actualizar los ejemplos de query a inglés (la demo headline pasa a algo como 'couch co-op game to play with friends' → Overcooked 2) y agregar una línea aclarando la decisión de idioma (el CONTENIDO va en inglés porque el modelo es de inglés; la UI/docs siguen en español). Ajustar cualquier mención a 'sinopsis en español'.
- PRESENTACION.md (EDITAR, queda en ESPAÑOL): actualizar la demo phrase a inglés y agregar/ajustar un párrafo que explique la decisión — alinear el idioma del contenido al modelo en vez de cambiar a un modelo multilingüe más pesado (buen punto de ingeniería para la defensa).

## Files in Scope

- `schemas/game.schema.yaml`
- `catalog/celeste.md`
- `catalog/disco-elysium.md`
- `catalog/firewatch.md`
- `catalog/gris.md`
- `catalog/hades.md`
- `catalog/hollow-knight.md`
- `catalog/journey.md`
- `catalog/overcooked-2.md`
- `catalog/stardew-valley.md`
- `catalog/witcher-3.md`
- `specs/search-expectations.yaml`
- `site/index.html`
- `dist/embeddings.json`
- `tests/fixtures/query-vectors.reference.json`
- `README.md`
- `PRESENTACION.md`

## Constraints

- Sólo va a INGLÉS el contenido que IMPACTA AL MODELO: sinopsis del catálogo, enum de géneros + campo genres, queries de las expectativas, y el ejemplo de búsqueda de la UI. README.md, PRESENTACION.md y el chrome de UI quedan en ESPAÑOL (la defensa oral es en español).
- El modelo (all-MiniLM-L6-v2 int8, 23MB), el pipeline (vectorize.py/emit_reference_vectors.py/equivalencia), download_model.py, site/js/vectorizer.mjs, site/js/search.mjs y la arquitectura NO cambian. Es una migración de CONTENIDO + el enum de Capa A; cero cambio de modelo o de lógica.
- Cambio ATÓMICO de Capa A: el enum de géneros del schema y el campo genres de los 10 .md se editan JUNTOS (additionalProperties:false + enum cerrado → si no matchean, validate_catalog falla).
- Las sinopsis en inglés deben ser naturales, ricas y distintivas (no traducción literal pobre, sin keyword-stuffing), respetando minLength 80 / maxLength 1000.
- NO debilitar specs/search-expectations.yaml: las expectativas (must_include_any_of) son Capa B / fuente de verdad. Si una query no entra, afinar la sinopsis inglesa del juego, NO relajar la expectativa.
- Mantener VERDE todo: validate_catalog.py (schema nuevo), equivalencia Python↔JS (re-emitir fixture; sigue < tolerancia + ranking como conjunto), regresión semántica (queries inglesas), check_site.py, ruff. Re-vectorizar y re-emitir el fixture DESPUÉS de editar catálogo+schema.
- Esta decisión AMIENDA/SUPERSEDE el ADR-003 (de 'afinar el catálogo en español' a 'alinear el idioma del contenido al modelo = inglés'). El documenter registra el ADR/decision nuevo al cierre.
- Nada pesado commiteado: models/, dist/, node_modules/ siguen gitignored. Español rioplatense en README/PRESENTACION; inglés natural en catálogo/queries.

## Acceptance Criteria

- [ ] El enum de géneros de schemas/game.schema.yaml está en inglés (action/horror/platformer/etc., sin los slugs en español); los 10 catalog/*.md tienen `genres` con los slugs ingleses y la sinopsis en inglés (80-1000 chars). `python scripts/validate_catalog.py` exit 0.
- [ ] specs/search-expectations.yaml tiene las 5 queries en inglés; los `must_include_any_of` (ids) y los in_top_k intactos; NO debilitadas.
- [ ] La búsqueda por texto libre mejora: las 5 expectativas pasan (`python -m pytest tests/` exit 0) y queries arbitrarias en inglés devuelven resultados con sentido (verificable, ej. 'relaxing farming game' → stardew-valley en top-5).
- [ ] dist/embeddings.json regenerado (10×384) y tests/fixtures/query-vectors.reference.json re-emitido; `node --test tests/equivalence/embed.equiv.test.mjs` exit 0.
- [ ] site/index.html: el ejemplo/placeholder de búsqueda está en inglés; el chrome (títulos, footer) sigue en español. `python scripts/check_site.py` exit 0. `node --test site/js/search.test.mjs` exit 0.
- [ ] README (en español) con ejemplos de query en inglés + la decisión de idioma aclarada; PRESENTACION (en español) con la demo phrase en inglés + el párrafo de la decisión.
- [ ] El modelo, download_model.py, vectorizer.mjs, search.mjs y la arquitectura NO cambiaron. Nada pesado commiteado (models/, dist/, node_modules/ gitignored).

## Verification Hooks

Commands that objectively prove the work is done. Run by
`cortex finish-session` (Pluggable Middle, Phase 01).

### schema-english
```bash
python -c "import yaml;e=yaml.safe_load(open('schemas/game.schema.yaml',encoding='utf-8'))['properties']['genres']['items']['enum'];assert 'action' in e and 'accion' not in e and 'horror' in e;print('enum de generos en ingles OK')"
```

Success: exit code 0 — el enum de géneros del schema está en inglés (action/horror presentes, accion ausente). · Timeout: 60s
### catalog-valid
```bash
python scripts/validate_catalog.py
```

Success: exit code 0 — los 10 .md validan contra el schema nuevo (genres ingleses, sinopsis 80-1000). · Timeout: 120s
### semantic-regression
```bash
python -m pytest tests/ -q
```

Success: exit code 0 — las 5 expectativas (queries inglesas) pasan + units del Paso 2. Requiere models/ + dist/embeddings.json regenerado. · Timeout: 300s
### equivalence
```bash
node --test tests/equivalence/embed.equiv.test.mjs
```

Success: exit code 0 — equivalencia Python↔JS sigue verde tras re-vectorizar y re-emitir el fixture (diff < tolerancia + top-k como conjunto). Requiere npm install + modelo. · Timeout: 600s
### js-pure-functions
```bash
node --test site/js/search.test.mjs
```

Success: exit code 0 — search.mjs sigue puro y correcto. · Timeout: 180s
### site-structure
```bash
python scripts/check_site.py
```

Success: exit code 0 — el sitio sigue coherente; embeddings.json 384 dims. · Timeout: 120s
### ruff-lint *(optional)*
```bash
ruff check .
```

Success: exit code 0 — código Python limpio. · Timeout: 180s
