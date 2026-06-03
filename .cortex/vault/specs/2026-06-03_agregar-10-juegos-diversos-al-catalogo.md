---
schema_version: 1
doc_type: spec
title: Agregar 10 juegos diversos al catálogo
created_at: '2026-06-03T02:16:35.358539Z'
updated_at: '2026-06-03T02:16:35.358539Z'
tags:
- spec
- spec
- sdd
- ci-cd
- catalogo
- juegos
- generos
- schema
- competitivo
- multijugador
- search-expectations
- ingles
- adr-004
status: draft
links: []
vault_scope: local
fingerprint: 29e605055a6a788a3f9b89f41b3710d23d6bb88963a26d0781103fcae18cde8a
verification_hooks:
- name: catalog-20-and-genres
  command: python -c "import glob,yaml;n=len(glob.glob('catalog/*.md'));assert n==20,f'{n}
    .md, esperaba 20';e=yaml.safe_load(open('schemas/game.schema.yaml',encoding='utf-8'))['properties']['genres']['items']['enum'];assert
    all(g in e for g in ['moba','racing','battle-royale','fighting','sandbox','party']);print('20
    juegos + enum extendido OK')"
  required: true
  success_criteria: exit code 0 — hay 20 catalog/*.md y el enum del schema tiene los
    6 géneros nuevos.
  timeout_seconds: 60
- name: catalog-valid
  command: python scripts/validate_catalog.py
  required: true
  success_criteria: exit code 0 — los 20 .md validan contra el schema (genres del
    enum, sinopsis 80-1000).
  timeout_seconds: 120
- name: semantic-regression
  command: python -m pytest tests/ -q
  required: true
  success_criteria: exit code 0 — todas las expectativas (5 viejas + nuevas) pasan
    + el unit test de estructura (ahora 20 items). Requiere models/ + dist/embeddings.json
    regenerado.
  timeout_seconds: 300
- name: equivalence
  command: node --test tests/equivalence/embed.equiv.test.mjs
  required: true
  success_criteria: exit code 0 — equivalencia Python↔JS verde tras re-vectorizar
    y re-emitir el fixture (diff < tolerancia + top-k como conjunto).
  timeout_seconds: 600
- name: js-pure-functions
  command: node --test site/js/search.test.mjs
  required: true
  success_criteria: exit code 0 — search.mjs puro + el test condicional de embeddings.json
    espera 20 juegos.
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
goal: 'Enriquecer el catálogo agregando 10 juegos de categorías MUY distintas a las
  actuales (hoy son 10 indies single-player; faltan shooter, terror, moba, racing,
  fighting, battle-royale, party, co-op), para que la búsqueda semántica tenga variedad
  real. El catálogo pasa de 10 a 20. Contenido en INGLÉS (ADR-004: el modelo all-MiniLM-L6-v2
  lee inglés). Implica: (a) EXTENDER el enum de géneros del schema (Capa A) con 6
  valores nuevos (moba, racing, battle-royale, fighting, sandbox, party); (b) crear
  10 catalog/<id>.md nuevos con frontmatter válido y sinopsis inglesas ricas y distintivas
  (80-1000 chars), usando búsqueda web para datos exactos (año, géneros, detalles);
  (c) sumar expectativas a search-expectations.yaml (Capa B) para las categorías nuevas;
  (d) actualizar los 2 tests con count hardcodeado (10→20: tests/test_vectorize.py
  y site/js/search.test.mjs); (e) re-vectorizar (embeddings.json→20 items), re-emitir
  el fixture de equivalencia y re-validar TODO. El modelo, el pipeline, download_model.py,
  vectorizer.mjs, search.mjs y la arquitectura NO cambian. El frontend renderea catálogo
  y géneros desde los datos, así que muestra los 20 solo. Los 10 juegos: counter-strike-2,
  league-of-legends, rocket-league, among-us, fortnite, street-fighter-6, minecraft,
  resident-evil-4, it-takes-two, mario-kart-8-deluxe.'
files_in_scope:
- schemas/game.schema.yaml
- catalog/counter-strike-2.md
- catalog/league-of-legends.md
- catalog/rocket-league.md
- catalog/among-us.md
- catalog/fortnite.md
- catalog/street-fighter-6.md
- catalog/minecraft.md
- catalog/resident-evil-4.md
- catalog/it-takes-two.md
- catalog/mario-kart-8-deluxe.md
- specs/search-expectations.yaml
- tests/test_vectorize.py
- site/js/search.test.mjs
- dist/embeddings.json
- tests/fixtures/query-vectors.reference.json
- README.md
- PRESENTACION.md
constraints:
- 'El contenido que impacta al modelo va en INGLÉS (ADR-004): sinopsis, géneros y
  queries. README/PRESENTACION y el chrome de UI quedan en español.'
- El modelo (all-MiniLM-L6-v2 int8), el pipeline (vectorize.py/emit_reference_vectors.py/equivalencia),
  download_model.py, site/js/vectorizer.mjs, site/js/search.mjs y la arquitectura
  NO cambian. Es contenido (Capa C) + extensión del enum (Capa A) + 2 ajustes de count
  en tests.
- 'Cambio ATÓMICO de Capa A: el enum extendido del schema y los genres de los 10 .md
  nuevos deben ser coherentes (additionalProperties:false + enum cerrado) o validate_catalog
  falla.'
- Los 2 counts hardcodeados (tests/test_vectorize.py línea ~49; site/js/search.test.mjs
  línea ~107) DEBEN pasar de 10 a 20, o el gate de tests rompe.
- Sinopsis inglesas naturales, ricas y DISTINTIVAS (80-1000 chars); prosa propia,
  no marketing copiado. Usar búsqueda web para datos correctos (año de lanzamiento,
  géneros, plataformas).
- 'NO debilitar specs/search-expectations.yaml: TODAS las expectativas (5 viejas +
  ~8 nuevas) deben pasar con 20 juegos. Si una no entra (un juego nuevo empujó al
  esperado fuera del top-5), afinar la sinopsis del juego esperado, NO relajar la
  expectativa.'
- 'Mantener VERDE todo: validate_catalog.py, equivalencia Python↔JS (re-emitir el
  fixture; sigue < tolerancia + ranking como conjunto), regresión (pytest), check_site.py,
  search.test.mjs, ruff. Re-vectorizar y re-emitir el fixture DESPUÉS de editar schema+catálogo+expectations.'
- Cada id slug = nombre de archivo (kebab-case); cada id de must_include_any_of debe
  existir como catalog/<id>.md. Nada pesado commiteado (models/, dist/, node_modules/
  gitignored).
acceptance_criteria:
- El enum de géneros de schemas/game.schema.yaml incluye los 6 nuevos (moba, racing,
  battle-royale, fighting, sandbox, party) además de los 13 existentes.
- Existen los 10 catalog/<id>.md nuevos, válidos contra el schema (genres del enum,
  sinopsis inglesa 80-1000 chars, year/platforms correctos). El catálogo tiene 20
  juegos. `python scripts/validate_catalog.py` exit 0.
- 'specs/search-expectations.yaml tiene las expectativas nuevas (inglés) + las 5 existentes;
  TODAS pasan: `python -m pytest tests/ -q` exit 0 (incluye el unit test de estructura
  que ahora espera 20).'
- dist/embeddings.json regenerado (20 items × 384) y el fixture re-emitido; `node
  --test tests/equivalence/embed.equiv.test.mjs` exit 0.
- tests/test_vectorize.py y site/js/search.test.mjs esperan 20 (no 10); `node --test
  site/js/search.test.mjs` exit 0; `python scripts/check_site.py` exit 0; `ruff check
  .` verde.
- README.md y PRESENTACION.md reflejan el catálogo de 20 juegos.
- El modelo, download_model.py, vectorizer.mjs, search.mjs y la arquitectura NO cambiaron.
  Nada pesado commiteado.
---

## Goal

Enriquecer el catálogo agregando 10 juegos de categorías MUY distintas a las actuales (hoy son 10 indies single-player; faltan shooter, terror, moba, racing, fighting, battle-royale, party, co-op), para que la búsqueda semántica tenga variedad real. El catálogo pasa de 10 a 20. Contenido en INGLÉS (ADR-004: el modelo all-MiniLM-L6-v2 lee inglés). Implica: (a) EXTENDER el enum de géneros del schema (Capa A) con 6 valores nuevos (moba, racing, battle-royale, fighting, sandbox, party); (b) crear 10 catalog/<id>.md nuevos con frontmatter válido y sinopsis inglesas ricas y distintivas (80-1000 chars), usando búsqueda web para datos exactos (año, géneros, detalles); (c) sumar expectativas a search-expectations.yaml (Capa B) para las categorías nuevas; (d) actualizar los 2 tests con count hardcodeado (10→20: tests/test_vectorize.py y site/js/search.test.mjs); (e) re-vectorizar (embeddings.json→20 items), re-emitir el fixture de equivalencia y re-validar TODO. El modelo, el pipeline, download_model.py, vectorizer.mjs, search.mjs y la arquitectura NO cambian. El frontend renderea catálogo y géneros desde los datos, así que muestra los 20 solo. Los 10 juegos: counter-strike-2, league-of-legends, rocket-league, among-us, fortnite, street-fighter-6, minecraft, resident-evil-4, it-takes-two, mario-kart-8-deluxe.

## Requirements

- schemas/game.schema.yaml (EDITAR — Capa A): EXTENDER el enum de géneros agregando 6 valores: moba, racing, battle-royale, fighting, sandbox, party. CONSERVAR los 13 existentes (action, adventure, rpg, indie, puzzle, horror, sports, strategy, simulation, platformer, shooter, casual, narrative). NO cambiar additionalProperties:false, required, las longitudes de summary (80-1000), ni el enum de platforms.
- Crear los 10 catalog/<id>.md NUEVOS (counter-strike-2, league-of-legends, rocket-league, among-us, fortnite, street-fighter-6, minecraft, resident-evil-4, it-takes-two, mario-kart-8-deluxe). Cada uno: frontmatter válido (id slug kebab-case = nombre de archivo; title; year correcto [USAR BÚSQUEDA WEB]; genres del enum [1-5]; platforms del enum) + SINOPSIS (cuerpo) en INGLÉS natural, rica y DISTINTIVA (80-1000 chars) que capture la categoría/modo (competitivo, online, party, co-op, survival horror, etc.) para que el modelo discrimine. Géneros sugeridos (ajustar con web): counter-strike-2=[shooter,strategy]; league-of-legends=[moba,strategy]; rocket-league=[sports,racing]; among-us=[party,casual]; fortnite=[battle-royale,shooter]; street-fighter-6=[fighting,action]; minecraft=[sandbox,simulation,adventure]; resident-evil-4=[horror,action,shooter]; it-takes-two=[adventure,platformer,puzzle]; mario-kart-8-deluxe=[racing,casual]. No copiar marketing literal; prosa propia.
- specs/search-expectations.yaml (EDITAR): AGREGAR ~8 expectativas nuevas (una por categoría nueva), queries en inglés + must_include_any_of con los ids nuevos. Mantener las 5 existentes. Sugeridas: 'competitive tactical shooter'→[counter-strike-2]; 'moba'→[league-of-legends]; 'battle royale'→[fortnite]; 'fighting game'→[street-fighter-6]; 'survival horror'→[resident-evil-4]; 'party game to play online with friends'→[among-us]; 'kart racing'→[mario-kart-8-deluxe]; 'two player co-op'→[it-takes-two]. NO debilitar: si una no entra, afinar la sinopsis del juego, no relajar.
- tests/test_vectorize.py (EDITAR): cambiar `assert len(data["items"]) == 10` (línea ~49) a `== 20`. NO tocar el resto (mean_pooling/l2_normalize).
- site/js/search.test.mjs (EDITAR): cambiar `assert.equal(data.items.length, 10, ...)` (línea ~107) a `20` y el texto del mensaje. NO tocar las unit tests sintéticas (cosineSimilarity/topK con datos inventados).
- dist/embeddings.json (REGENERAR): `python scripts/vectorize.py` tras editar schema+catálogo. Pasa a 20 items × 384 dims. Gitignored.
- tests/fixtures/query-vectors.reference.json (RE-EMITIR): `python scripts/emit_reference_vectors.py` tras re-vectorizar (las queries salen de search-expectations.yaml, ahora con las nuevas). La equivalencia debe seguir verde.
- README.md y PRESENTACION.md (EDITAR, quedan en ESPAÑOL): actualizar las menciones de 'catálogo de 10 juegos' → 20 y reflejar la variedad de categorías nuevas (competitivos, multijugador, etc.).

## Files in Scope

- `schemas/game.schema.yaml`
- `catalog/counter-strike-2.md`
- `catalog/league-of-legends.md`
- `catalog/rocket-league.md`
- `catalog/among-us.md`
- `catalog/fortnite.md`
- `catalog/street-fighter-6.md`
- `catalog/minecraft.md`
- `catalog/resident-evil-4.md`
- `catalog/it-takes-two.md`
- `catalog/mario-kart-8-deluxe.md`
- `specs/search-expectations.yaml`
- `tests/test_vectorize.py`
- `site/js/search.test.mjs`
- `dist/embeddings.json`
- `tests/fixtures/query-vectors.reference.json`
- `README.md`
- `PRESENTACION.md`

## Constraints

- El contenido que impacta al modelo va en INGLÉS (ADR-004): sinopsis, géneros y queries. README/PRESENTACION y el chrome de UI quedan en español.
- El modelo (all-MiniLM-L6-v2 int8), el pipeline (vectorize.py/emit_reference_vectors.py/equivalencia), download_model.py, site/js/vectorizer.mjs, site/js/search.mjs y la arquitectura NO cambian. Es contenido (Capa C) + extensión del enum (Capa A) + 2 ajustes de count en tests.
- Cambio ATÓMICO de Capa A: el enum extendido del schema y los genres de los 10 .md nuevos deben ser coherentes (additionalProperties:false + enum cerrado) o validate_catalog falla.
- Los 2 counts hardcodeados (tests/test_vectorize.py línea ~49; site/js/search.test.mjs línea ~107) DEBEN pasar de 10 a 20, o el gate de tests rompe.
- Sinopsis inglesas naturales, ricas y DISTINTIVAS (80-1000 chars); prosa propia, no marketing copiado. Usar búsqueda web para datos correctos (año de lanzamiento, géneros, plataformas).
- NO debilitar specs/search-expectations.yaml: TODAS las expectativas (5 viejas + ~8 nuevas) deben pasar con 20 juegos. Si una no entra (un juego nuevo empujó al esperado fuera del top-5), afinar la sinopsis del juego esperado, NO relajar la expectativa.
- Mantener VERDE todo: validate_catalog.py, equivalencia Python↔JS (re-emitir el fixture; sigue < tolerancia + ranking como conjunto), regresión (pytest), check_site.py, search.test.mjs, ruff. Re-vectorizar y re-emitir el fixture DESPUÉS de editar schema+catálogo+expectations.
- Cada id slug = nombre de archivo (kebab-case); cada id de must_include_any_of debe existir como catalog/<id>.md. Nada pesado commiteado (models/, dist/, node_modules/ gitignored).

## Acceptance Criteria

- [ ] El enum de géneros de schemas/game.schema.yaml incluye los 6 nuevos (moba, racing, battle-royale, fighting, sandbox, party) además de los 13 existentes.
- [ ] Existen los 10 catalog/<id>.md nuevos, válidos contra el schema (genres del enum, sinopsis inglesa 80-1000 chars, year/platforms correctos). El catálogo tiene 20 juegos. `python scripts/validate_catalog.py` exit 0.
- [ ] specs/search-expectations.yaml tiene las expectativas nuevas (inglés) + las 5 existentes; TODAS pasan: `python -m pytest tests/ -q` exit 0 (incluye el unit test de estructura que ahora espera 20).
- [ ] dist/embeddings.json regenerado (20 items × 384) y el fixture re-emitido; `node --test tests/equivalence/embed.equiv.test.mjs` exit 0.
- [ ] tests/test_vectorize.py y site/js/search.test.mjs esperan 20 (no 10); `node --test site/js/search.test.mjs` exit 0; `python scripts/check_site.py` exit 0; `ruff check .` verde.
- [ ] README.md y PRESENTACION.md reflejan el catálogo de 20 juegos.
- [ ] El modelo, download_model.py, vectorizer.mjs, search.mjs y la arquitectura NO cambiaron. Nada pesado commiteado.

## Verification Hooks

Commands that objectively prove the work is done. Run by
`cortex finish-session` (Pluggable Middle, Phase 01).

### catalog-20-and-genres
```bash
python -c "import glob,yaml;n=len(glob.glob('catalog/*.md'));assert n==20,f'{n} .md, esperaba 20';e=yaml.safe_load(open('schemas/game.schema.yaml',encoding='utf-8'))['properties']['genres']['items']['enum'];assert all(g in e for g in ['moba','racing','battle-royale','fighting','sandbox','party']);print('20 juegos + enum extendido OK')"
```

Success: exit code 0 — hay 20 catalog/*.md y el enum del schema tiene los 6 géneros nuevos. · Timeout: 60s
### catalog-valid
```bash
python scripts/validate_catalog.py
```

Success: exit code 0 — los 20 .md validan contra el schema (genres del enum, sinopsis 80-1000). · Timeout: 120s
### semantic-regression
```bash
python -m pytest tests/ -q
```

Success: exit code 0 — todas las expectativas (5 viejas + nuevas) pasan + el unit test de estructura (ahora 20 items). Requiere models/ + dist/embeddings.json regenerado. · Timeout: 300s
### equivalence
```bash
node --test tests/equivalence/embed.equiv.test.mjs
```

Success: exit code 0 — equivalencia Python↔JS verde tras re-vectorizar y re-emitir el fixture (diff < tolerancia + top-k como conjunto). · Timeout: 600s
### js-pure-functions
```bash
node --test site/js/search.test.mjs
```

Success: exit code 0 — search.mjs puro + el test condicional de embeddings.json espera 20 juegos. · Timeout: 180s
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
