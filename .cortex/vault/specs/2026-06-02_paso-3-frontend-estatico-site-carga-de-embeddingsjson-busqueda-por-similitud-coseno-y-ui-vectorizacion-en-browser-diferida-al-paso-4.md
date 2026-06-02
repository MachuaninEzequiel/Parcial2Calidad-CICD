---
schema_version: 1
doc_type: spec
title: 'Paso 3 — Frontend estático (site/): carga de embeddings.json, búsqueda por
  similitud coseno y UI (vectorización en browser diferida al Paso 4)'
created_at: '2026-06-02T17:35:33.607021Z'
updated_at: '2026-06-02T17:35:33.607021Z'
tags:
- spec
- spec
- sdd
- ci-cd
- paso-3
- frontend
- static-site
- onnx
- cosine-similarity
- vanilla-js
- embeddings
- videojuegos
status: draft
links: []
vault_scope: local
fingerprint: 86dcddf623d587aa9574ee913ef6a8222372f2869ddf17b52e78519450b74f3f
verification_hooks:
- name: js-pure-functions
  command: node --test site/js/search.test.mjs
  required: true
  success_criteria: exit code 0 — cosineSimilarity y topK correctas (+ test condicional
    de embeddings.json)
  timeout_seconds: 180
- name: site-structure
  command: python scripts/check_site.py
  required: true
  success_criteria: exit code 0 — archivos del sitio presentes, index.html referencia
    los assets, embeddings.json (si existe) con dimensions==384
  timeout_seconds: 120
- name: catalog-still-green
  command: python scripts/validate_catalog.py
  required: true
  success_criteria: exit code 0 — el Paso 3 no rompió la validación del catálogo (Pasos
    1-2)
  timeout_seconds: 120
- name: ruff-lint
  command: ruff check .
  required: false
  success_criteria: exit code 0 — código Python limpio (incl. check_site.py)
  timeout_seconds: 180
goal: 'Construir la primera mitad del frontend (el README declara "frontend Pasos
  3-4"): un sitio 100% estático en site/ (HTML + CSS + JS vanilla, sin frameworks
  ni bundlers) que carga dist/embeddings.json, renderiza el catálogo de 10 juegos
  y hace búsqueda semántica por similitud coseno client-side. El paso query→vector
  queda aislado tras un seam vectorizeQuery() respaldado por un stub demoable: modo
  "buscá juegos similares" (item-to-item, usando los vectores ya precomputados del
  embeddings.json) — una feature semántica completa y mostrable SIN tocar el modelo.
  Las funciones puras (cosineSimilarity, topK) viven en un módulo ES sin dependencias
  de DOM y se testean con el runner nativo node:test (cero npm). El onnxruntime-web
  real en el browser + el tokenizer + la vectorización de texto libre + el test de
  equivalencia Python↔JS (tolerancia 1e-5, riesgo #1 del ADR-001) se reservan para
  el Paso 4: el seam vectorizeQuery() existe pero lanza un Error explícito "implementado
  en el Paso 4". Español rioplatense, didáctico, pensado para la defensa oral de 5
  min.'
files_in_scope:
- site/index.html
- site/css/styles.css
- site/js/search.mjs
- site/js/app.mjs
- site/js/search.test.mjs
- scripts/check_site.py
- PRESENTACION.md
- README.md
constraints:
- 'Decisiones de arquitectura cerradas (ADR-001 + brief): sitio 100% estático, HTML
  + JS vanilla, onnxruntime-web vía CDN, similitud coseno client-side. NO re-discutir
  ni introducir frameworks, bundlers ni paquetes npm (React/Vue/Vite/webpack quedan
  fuera).'
- 'NO implementar en el Paso 3: vectorización de la query en el browser (onnxruntime-web
  + tokenizer), test de equivalencia Python↔JS (tolerancia 1e-5), .github/workflows/ci.yml,
  Docker. Eso es Paso 4 en adelante. El seam vectorizeQuery() existe pero LANZA un
  Error ''Paso 4'' — no devuelve resultados vacíos en silencio.'
- 'Reuso/DRY: la lógica de coseno + ranking (search.mjs) es la MISMA que el Paso 4
  reutilizará tras enchufar la vectorización real; no duplicarla ni reescribirla en
  el Paso 4.'
- 'cosineSimilarity asume vectores L2-normalizados (premisa establecida en el Paso
  2 y el glosario): se reduce a producto punto. Documentar la premisa en el código.'
- 'embeddings.json es gitignored (lo genera el Paso 2): el sitio lo fetchea por path
  relativo. Dónde vive el archivo al publicar es responsabilidad del build (Paso 6);
  en Paso 3 solo se documenta cómo servir el preview local (ej. python -m http.server
  con embeddings.json accesible junto al sitio).'
- 'Tests JS con el runner nativo node:test: CERO paquetes npm (respeta ''sin dependencias
  innecesarias'' del brief). Asume Node ≥18 disponible; en GitHub Actions viene preinstalado.'
- 'Avanzar paso a paso: al terminar el Paso 3, pausar y esperar confirmación del usuario
  antes del Paso 4. Cerrar con /cortex-documenter; si algún hook required falla o
  queda algo a medias, cerrar como ''handoff'', no ''closed''.'
- Español rioplatense (voseo), didáctico, pensado para la defensa oral de 5 min.
acceptance_criteria:
- Existen site/index.html, site/css/styles.css, site/js/search.mjs, site/js/app.mjs
  y site/js/search.test.mjs.
- '`node --test site/js/search.test.mjs` termina con exit 0: funciones puras coseno/topK
  correctas + test condicional del JSON.'
- '`python scripts/check_site.py` termina con exit 0: los archivos del sitio existen,
  index.html referencia los assets y (si está dist/embeddings.json) el JSON tiene
  model + dimensions==384 + items con vector.'
- Sirviendo el sitio localmente con embeddings.json accesible, se listan los 10 juegos
  y la acción 'buscar similares' devuelve top-5 ordenados por coseno descendente,
  excluyendo al propio juego.
- La caja de búsqueda por texto libre está presente pero claramente marcada/deshabilitada
  como 'Paso 4'; vectorizeQuery() lanza un Error explícito (no resultados vacíos en
  silencio).
- 'El frontend NO hardcodea el enum de géneros: consume los genres del dato (embeddings.json).'
- '`ruff check .` sigue verde sobre el código Python (incluido scripts/check_site.py).'
- '`python scripts/validate_catalog.py` sigue exit 0 (el Paso 3 no rompió los Pasos
  1-2).'
- PRESENTACION.md tiene el fragmento del Paso 3 y README 'Estado actual' quedó actualizado.
- 'Nada pesado nuevo commiteado: ni models/ ni dist/; embeddings.json sigue gitignored.'
---

## Goal

Construir la primera mitad del frontend (el README declara "frontend Pasos 3-4"): un sitio 100% estático en site/ (HTML + CSS + JS vanilla, sin frameworks ni bundlers) que carga dist/embeddings.json, renderiza el catálogo de 10 juegos y hace búsqueda semántica por similitud coseno client-side. El paso query→vector queda aislado tras un seam vectorizeQuery() respaldado por un stub demoable: modo "buscá juegos similares" (item-to-item, usando los vectores ya precomputados del embeddings.json) — una feature semántica completa y mostrable SIN tocar el modelo. Las funciones puras (cosineSimilarity, topK) viven en un módulo ES sin dependencias de DOM y se testean con el runner nativo node:test (cero npm). El onnxruntime-web real en el browser + el tokenizer + la vectorización de texto libre + el test de equivalencia Python↔JS (tolerancia 1e-5, riesgo #1 del ADR-001) se reservan para el Paso 4: el seam vectorizeQuery() existe pero lanza un Error explícito "implementado en el Paso 4". Español rioplatense, didáctico, pensado para la defensa oral de 5 min.

## Requirements

- site/index.html (NUEVO): estructura semántica de la página — header con título y descripción del buscador, una caja de búsqueda por texto libre PRESENTE pero claramente marcada como 'disponible en el Paso 4' (deshabilitada), una sección de catálogo que lista los 10 juegos (title, year, genres, summary) y por cada juego una acción 'buscar similares', y una zona de resultados. Carga site/css/styles.css y el módulo ES site/js/app.mjs (type=module). HTML + JS vanilla, sin frameworks (decisión cerrada del ADR-001/brief).
- site/css/styles.css (NUEVO): estilos propios, legibles y con responsive básico, pensados para una demo en proyector (defensa oral). Sin frameworks CSS.
- site/js/search.mjs (NUEVO): módulo ES con FUNCIONES PURAS testeables y CERO dependencias de DOM — cosineSimilarity(a, b) (producto punto; documentar la premisa de que los vectores vienen L2-normalizados desde el Paso 2, por lo que el coseno se reduce a producto punto), topK(queryVector, items, k=5) que rankea items por coseno descendente y devuelve los k mejores con su score, y el SEAM vectorizeQuery(text) que por ahora lanza un Error explícito 'implementado en el Paso 4 (onnxruntime-web)'. Esta lógica es la MISMA que reutilizará el Paso 4 tras enchufar la vectorización real.
- site/js/app.mjs (NUEVO): wiring de DOM — fetch de embeddings.json (path relativo configurable, default ./embeddings.json), render del catálogo a partir de items, manejo del 'buscar similares' (toma el vector del juego elegido, llama topK contra el resto excluyendo al propio juego, renderiza top-5 con su score), y estado deshabilitado + mensaje claro para la caja de texto libre. Importa search.mjs. Manejo de errores de carga: mensaje claro y accionable si falta o no se puede leer embeddings.json.
- site/js/search.test.mjs (NUEVO): tests con el runner nativo node:test (sin npm install) de las funciones puras: (a) cosineSimilarity con vectores conocidos (idénticos→1, ortogonales→0, opuestos→-1); (b) topK devuelve exactamente k items ordenados desc por score y respeta k; (c) test CONDICIONAL: si dist/embeddings.json existe, lo carga, toma un item y verifica que topK(suVector, items, 5) lo rankea primero (auto-similitud ≈1) y devuelve 5 resultados. No requiere descargar el modelo.
- scripts/check_site.py (NUEVO): chequeo estructural portable (Python ya es dep del proyecto) — verifica que existen site/index.html, site/css/styles.css y site/js/{search,app,search.test}.mjs; que index.html referencia styles.css y app.mjs; y (si existe dist/embeddings.json) que tiene las claves esperadas (model, dimensions==384, items con vector de 384). Exit 0 si todo OK, mensajes claros estilo validate_catalog.py. Reconfigurar stdout a UTF-8 como los otros scripts.
- Capa C de SDD: el frontend NO re-hardcodea el enum de géneros/plataformas — consume los genres de cada item del propio embeddings.json (que deriva del catálogo y, en última instancia, del schema).
- PRESENTACION.md (EDITAR/append): fragmento (~3 párrafos) cubriendo el Paso 3 — qué es la similitud coseno, por qué con vectores L2-normalizados el coseno es un producto punto, y por qué la vectorización real de la query (el mismo model.onnx corriendo en el browser) se deja para el Paso 4.
- README.md (EDITAR): actualizar la sección 'Estado actual' para reflejar Pasos 1-3 y aclarar que la búsqueda por texto libre llega en el Paso 4; mantener el roadmap y la estructura del repo (agregar site/).

## Files in Scope

- `site/index.html`
- `site/css/styles.css`
- `site/js/search.mjs`
- `site/js/app.mjs`
- `site/js/search.test.mjs`
- `scripts/check_site.py`
- `PRESENTACION.md`
- `README.md`

## Constraints

- Decisiones de arquitectura cerradas (ADR-001 + brief): sitio 100% estático, HTML + JS vanilla, onnxruntime-web vía CDN, similitud coseno client-side. NO re-discutir ni introducir frameworks, bundlers ni paquetes npm (React/Vue/Vite/webpack quedan fuera).
- NO implementar en el Paso 3: vectorización de la query en el browser (onnxruntime-web + tokenizer), test de equivalencia Python↔JS (tolerancia 1e-5), .github/workflows/ci.yml, Docker. Eso es Paso 4 en adelante. El seam vectorizeQuery() existe pero LANZA un Error 'Paso 4' — no devuelve resultados vacíos en silencio.
- Reuso/DRY: la lógica de coseno + ranking (search.mjs) es la MISMA que el Paso 4 reutilizará tras enchufar la vectorización real; no duplicarla ni reescribirla en el Paso 4.
- cosineSimilarity asume vectores L2-normalizados (premisa establecida en el Paso 2 y el glosario): se reduce a producto punto. Documentar la premisa en el código.
- embeddings.json es gitignored (lo genera el Paso 2): el sitio lo fetchea por path relativo. Dónde vive el archivo al publicar es responsabilidad del build (Paso 6); en Paso 3 solo se documenta cómo servir el preview local (ej. python -m http.server con embeddings.json accesible junto al sitio).
- Tests JS con el runner nativo node:test: CERO paquetes npm (respeta 'sin dependencias innecesarias' del brief). Asume Node ≥18 disponible; en GitHub Actions viene preinstalado.
- Avanzar paso a paso: al terminar el Paso 3, pausar y esperar confirmación del usuario antes del Paso 4. Cerrar con /cortex-documenter; si algún hook required falla o queda algo a medias, cerrar como 'handoff', no 'closed'.
- Español rioplatense (voseo), didáctico, pensado para la defensa oral de 5 min.

## Acceptance Criteria

- [ ] Existen site/index.html, site/css/styles.css, site/js/search.mjs, site/js/app.mjs y site/js/search.test.mjs.
- [ ] `node --test site/js/search.test.mjs` termina con exit 0: funciones puras coseno/topK correctas + test condicional del JSON.
- [ ] `python scripts/check_site.py` termina con exit 0: los archivos del sitio existen, index.html referencia los assets y (si está dist/embeddings.json) el JSON tiene model + dimensions==384 + items con vector.
- [ ] Sirviendo el sitio localmente con embeddings.json accesible, se listan los 10 juegos y la acción 'buscar similares' devuelve top-5 ordenados por coseno descendente, excluyendo al propio juego.
- [ ] La caja de búsqueda por texto libre está presente pero claramente marcada/deshabilitada como 'Paso 4'; vectorizeQuery() lanza un Error explícito (no resultados vacíos en silencio).
- [ ] El frontend NO hardcodea el enum de géneros: consume los genres del dato (embeddings.json).
- [ ] `ruff check .` sigue verde sobre el código Python (incluido scripts/check_site.py).
- [ ] `python scripts/validate_catalog.py` sigue exit 0 (el Paso 3 no rompió los Pasos 1-2).
- [ ] PRESENTACION.md tiene el fragmento del Paso 3 y README 'Estado actual' quedó actualizado.
- [ ] Nada pesado nuevo commiteado: ni models/ ni dist/; embeddings.json sigue gitignored.

## Verification Hooks

Commands that objectively prove the work is done. Run by
`cortex finish-session` (Pluggable Middle, Phase 01).

### js-pure-functions
```bash
node --test site/js/search.test.mjs
```

Success: exit code 0 — cosineSimilarity y topK correctas (+ test condicional de embeddings.json) · Timeout: 180s
### site-structure
```bash
python scripts/check_site.py
```

Success: exit code 0 — archivos del sitio presentes, index.html referencia los assets, embeddings.json (si existe) con dimensions==384 · Timeout: 120s
### catalog-still-green
```bash
python scripts/validate_catalog.py
```

Success: exit code 0 — el Paso 3 no rompió la validación del catálogo (Pasos 1-2) · Timeout: 120s
### ruff-lint *(optional)*
```bash
ruff check .
```

Success: exit code 0 — código Python limpio (incl. check_site.py) · Timeout: 180s
