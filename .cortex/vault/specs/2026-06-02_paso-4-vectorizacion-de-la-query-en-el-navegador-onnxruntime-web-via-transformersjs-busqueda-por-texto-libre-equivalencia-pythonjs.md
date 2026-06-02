---
schema_version: 1
doc_type: spec
title: 'Paso 4 — Vectorización de la query en el navegador (onnxruntime-web vía Transformers.js):
  búsqueda por texto libre + equivalencia Python↔JS'
created_at: '2026-06-02T19:18:19.081777Z'
updated_at: '2026-06-02T19:18:19.081777Z'
tags:
- spec
- spec
- sdd
- ci-cd
- paso-4
- frontend
- onnx
- onnxruntime-web
- transformers-js
- embeddings
- browser-vectorization
- equivalence
- cosine-similarity
- vanilla-js
- videojuegos
status: draft
links: []
vault_scope: local
fingerprint: 02d5ac49073c69e6e582c4f368365d56c229be3fdc4f876a3b6dd74ea2e99e39
verification_hooks:
- name: js-equivalence
  command: node --test tests/equivalence/embed.equiv.test.mjs
  required: true
  success_criteria: exit code 0 — el vector JS (Transformers.js) coincide con el de
    referencia Python dentro de tolerancia (objetivo 1e-5) y el ranking top-k es idéntico.
    Requiere `npm install` y el modelo accesible.
  timeout_seconds: 600
- name: js-pure-functions
  command: node --test site/js/search.test.mjs
  required: true
  success_criteria: exit code 0 — cosineSimilarity y topK siguen correctas y search.mjs
    sigue puro (sin dependencias).
  timeout_seconds: 180
- name: site-structure
  command: python scripts/check_site.py
  required: true
  success_criteria: exit code 0 — vectorizer.mjs presente, caja de texto libre habilitada,
    assets referenciados, embeddings.json (si existe) con dimensions==384.
  timeout_seconds: 120
- name: catalog-still-green
  command: python scripts/validate_catalog.py
  required: true
  success_criteria: exit code 0 — el Paso 4 no rompió la validación del catálogo (Pasos
    1-2).
  timeout_seconds: 120
- name: ruff-lint
  command: ruff check .
  required: false
  success_criteria: exit code 0 — código Python limpio (incl. emit_reference_vectors.py).
  timeout_seconds: 180
goal: 'Implementar de verdad el seam vectorizeQuery() para que el navegador convierta
  el texto libre del usuario en un vector de 384 dims usando el MISMO modelo del catálogo
  (Xenova/all-MiniLM-L6-v2 quantized), vía Transformers.js (que es onnxruntime-web
  por debajo) con feature-extraction + {pooling:''mean'', normalize:true}. Habilitar
  la caja de búsqueda por texto libre, reusar tal cual topK/cosineSimilarity de search.mjs
  para rankear contra los embeddings precomputados, y —el corazón del paso— PROBAR
  la equivalencia de vectorización Python↔JS (riesgo #1 del ADR-001) con un golden
  test: el lado Python emite vectores de referencia para queries fijas y un test en
  Node verifica que el lado JS coincide dentro de tolerancia (objetivo 1e-5) Y que
  el ranking top-k es idéntico. search.mjs queda 100% puro (la vectorización del browser
  vive en un módulo nuevo) para que sus tests sigan con node:test sin dependencias.
  Español rioplatense, didáctico, pensado para la defensa oral de 5 min.'
files_in_scope:
- site/js/vectorizer.mjs
- site/js/search.mjs
- site/js/app.mjs
- site/index.html
- site/css/styles.css
- scripts/emit_reference_vectors.py
- scripts/vectorize.py
- tests/equivalence/embed.equiv.test.mjs
- tests/fixtures/query-vectors.reference.json
- package.json
- .gitignore
- scripts/check_site.py
- README.md
- PRESENTACION.md
constraints:
- 'Arquitectura cerrada (ADR-001 + brief): sitio 100% estático, HTML + JS vanilla
  para la app, onnxruntime-web (vía Transformers.js) para la inferencia en el browser,
  similitud coseno client-side. NO introducir frameworks ni bundlers para el sitio
  (React/Vue/Vite/webpack quedan fuera). La ÚNICA dependencia JS nueva es Transformers.js:
  en el browser entra por import map → CDN (sin npm install), y en Node se instala
  solo para el equivalence test.'
- 'Mantener search.mjs PURO y testeable con node:test SIN dependencias: la vectorización
  del browser (Transformers.js/ort-web) vive en site/js/vectorizer.mjs. cosineSimilarity
  y topK no cambian. Si vectorizeQuery() importara la lib desde search.mjs, importar
  search.mjs en node:test arrastraría la dependencia — por eso se separa.'
- 'DRY: la búsqueda por texto libre reusa EXACTAMENTE topK/cosineSimilarity de search.mjs
  (la misma maquinaria que ''buscar similares'', solo cambia de dónde sale el queryVector).
  El generador de referencia reusa el embed() de vectorize.py; no se reescribe pooling/L2
  en Python.'
- 'Mismo modelo que el CI: Xenova/all-MiniLM-L6-v2 quantized (model_quantized.onnx),
  el mismo artefacto que fija download_model.py. Mismo modelo + mismo tokenizer.json
  + mismo mean pooling + L2 en ambos lados → mismo espacio semántico (ADR-001).'
- 'La equivalencia es el criterio de aceptación central (riesgo #1 del ADR-001): objetivo
  de tolerancia 1e-5 sobre el diff numérico MÁS identidad del ranking top-k como gate
  robusto. Si 1e-5 resulta inviable sobre el modelo int8 entre ort-Python y ort-web,
  documentar y justificar la tolerancia empírica elegida, manteniendo el ranking idéntico
  como condición dura.'
- 'FUERA de alcance del Paso 4: .github/workflows/ci.yml (Paso 6), Docker (Paso 7)
  y los tests de regresión semántica autogenerados desde search-expectations.yaml
  (Paso 5, aunque el Paso 4 los habilita). El hosting del modelo en producción (GitHub
  Pages; models/ es gitignored) se decide y cablea en el build del Paso 6 — en Paso
  4 solo se documenta y se hace andar el preview local.'
- 'No commitear nada pesado: models/, dist/ y node_modules/ siguen gitignored. No
  subir el modelo ni los embeddings al repo.'
- 'Avanzar paso a paso: al terminar el Paso 4, pausar y esperar confirmación del usuario
  antes del Paso 5. Cerrar con /cortex-documenter; si algún hook required falla (p.
  ej. la equivalencia no entra en tolerancia o el modelo no se pudo bajar en el entorno)
  o queda algo a medias, cerrar como ''handoff'', no ''closed''.'
- Español rioplatense (voseo), didáctico, pensado para la defensa oral de 5 min.
acceptance_criteria:
- Existe site/js/vectorizer.mjs y exporta async vectorizeQuery(text) que devuelve
  un vector L2-normalizado de 384 dims vía Transformers.js (feature-extraction, pooling:'mean',
  normalize:true), con el pipeline cacheado.
- La caja de búsqueda por texto libre de index.html está HABILITADA; al tipear una
  frase y enviar, se muestra el top-5 por coseno descendente (reusando topK), con
  un estado de carga durante la primera descarga del modelo y manejo de error si falla.
- 'search.mjs sigue puro (sin imports pesados): `node --test site/js/search.test.mjs`
  termina exit 0.'
- 'Existe el equivalence test y pasa: para las queries del fixture, max |diff| entre
  el vector JS y el de referencia Python < tolerancia (objetivo 1e-5; si se relaja,
  queda documentado) Y el ranking top-k (ids) coincide con el de Python.'
- scripts/emit_reference_vectors.py genera tests/fixtures/query-vectors.reference.json
  reusando el embed() de vectorize.py (no duplica pooling/L2).
- package.json declara la devDependency '@huggingface/transformers'; el sitio renderiza
  catálogo + 'buscar similares' SIN npm install (usa el import map al CDN).
- '`python scripts/check_site.py` termina exit 0: vectorizer.mjs presente, la caja
  de texto libre ya no está deshabilitada, assets referenciados.'
- '`python scripts/validate_catalog.py` sigue exit 0 y `ruff check .` sigue verde
  (Pasos 1-3 intactos).'
- README 'Estado actual' refleja Pasos 1-4 y PRESENTACION.md tiene el fragmento del
  Paso 4.
- 'Nada pesado commiteado: models/, dist/ y node_modules/ siguen gitignored.'
---

## Goal

Implementar de verdad el seam vectorizeQuery() para que el navegador convierta el texto libre del usuario en un vector de 384 dims usando el MISMO modelo del catálogo (Xenova/all-MiniLM-L6-v2 quantized), vía Transformers.js (que es onnxruntime-web por debajo) con feature-extraction + {pooling:'mean', normalize:true}. Habilitar la caja de búsqueda por texto libre, reusar tal cual topK/cosineSimilarity de search.mjs para rankear contra los embeddings precomputados, y —el corazón del paso— PROBAR la equivalencia de vectorización Python↔JS (riesgo #1 del ADR-001) con un golden test: el lado Python emite vectores de referencia para queries fijas y un test en Node verifica que el lado JS coincide dentro de tolerancia (objetivo 1e-5) Y que el ranking top-k es idéntico. search.mjs queda 100% puro (la vectorización del browser vive en un módulo nuevo) para que sus tests sigan con node:test sin dependencias. Español rioplatense, didáctico, pensado para la defensa oral de 5 min.

## Requirements

- site/js/vectorizer.mjs (NUEVO): módulo de vectorización del browser. Importa Transformers.js por bare specifier '@huggingface/transformers' y expone async vectorizeQuery(text) -> Promise<number[]> de 384 dims, usando pipeline('feature-extraction','Xenova/all-MiniLM-L6-v2', {quantized:true}) con {pooling:'mean', normalize:true}. Carga perezosa y cacheo del pipeline (se baja/instancia UNA vez y se reutiliza). Documentar por qué esto reproduce el pipeline de vectorize.py: mismo repo/modelo, mismo tokenizer.json, mismo mean pooling ponderado por attention_mask + L2. Soportar opcionalmente apuntar a models/ local (env.localModelPath / allowRemoteModels) para conservar 'el mismo archivo'; documentar el fallback al CDN de HF.
- site/js/search.mjs (EDITAR): QUITAR el seam vectorizeQuery() que lanzaba el Error 'Paso 4' (su nuevo hogar es vectorizer.mjs). cosineSimilarity y topK quedan IGUAL y 100% puras (cero imports pesados) para que node --test site/js/search.test.mjs siga corriendo sin instalar nada. Actualizar el comentario que mencionaba 'Paso 4'.
- site/js/app.mjs (EDITAR): importar vectorizeQuery desde vectorizer.mjs. Cablear la caja de texto libre: al enviar (submit/Enter), vectorizar la query -> topK(queryVector, items, 5) -> render del top-5 con su score (reusando la MISMA maquinaria de render que 'buscar similares'). Estado de carga para la primera query (el modelo ~23 MB se baja una vez): deshabilitar input + spinner/mensaje, rehabilitar al terminar. Manejo de error claro si el modelo no carga. Conservar intacto 'buscar similares'.
- site/index.html (EDITAR): HABILITAR el <input id='free-query'> (quitar disabled/aria-disabled), reemplazar la nota '🔒 Disponible en el Paso 4' por una pista de uso + aviso de que la primera búsqueda baja el modelo. Agregar un import map en <head> que mapee el bare specifier '@huggingface/transformers' a la URL ESM del CDN (para que el mismo vectorizer.mjs funcione en el browser sin bundler y en Node con el paquete instalado). Zona de estado/carga si hace falta.
- site/css/styles.css (EDITAR): estilos para la caja de búsqueda activa, el botón de buscar, y el estado de carga/spinner. Sin frameworks CSS.
- scripts/emit_reference_vectors.py (NUEVO): genera tests/fixtures/query-vectors.reference.json — para un set FIJO de queries (las de specs/search-expectations.yaml + alguna corta de control) calcula el embedding del lado Python REUSANDO el pipeline de vectorize.py (embed/mean_pooling/l2_normalize) y escribe {model, dimensions, tolerance, queries:[{text, vector}]}. Es la referencia dorada de la equivalencia. Reconfigurar stdout a UTF-8 como los demás scripts.
- scripts/vectorize.py (EDITAR si hace falta): exponer embed()/build de texto de forma reutilizable para que emit_reference_vectors.py NO duplique la lógica de tokenización + pooling + L2 (DRY). Sin cambiar el comportamiento del Paso 2.
- tests/equivalence/embed.equiv.test.mjs (NUEVO): test con el runner node:test que importa vectorizer.mjs (Transformers.js corre también en Node), calcula el embedding JS de cada query del fixture y verifica (a) max |diff| < tolerance contra el vector de referencia Python (objetivo 1e-5) y (b) que el ranking top-k (ids) de esa query coincide con el de Python. Si 1e-5 resulta inviable sobre el modelo int8, documentar la tolerancia elegida empíricamente y mantener la identidad de ranking como gate duro.
- package.json (NUEVO): declara la devDependency JS '@huggingface/transformers' (única que necesita el equivalence test en Node) y un script (ej. 'test:equiv'). Documentar que el SITIO no necesita npm install (usa el import del CDN); la instalación es solo para el gate de equivalencia en CI/local. type:module.
- .gitignore (EDITAR): ignorar node_modules/ (y cualquier cache de Transformers.js / .cache de modelos en Node).
- scripts/check_site.py (EDITAR): sumar checks portables — existe site/js/vectorizer.mjs; index.html ya NO tiene el input deshabilitado (la caja de texto libre está habilitada); index.html declara el import map / referencia vectorizer indirectamente vía app.mjs. Mantener el chequeo de embeddings.json. Mensajes claros estilo validate_catalog.py.
- README.md (EDITAR): actualizar 'Estado actual' a Pasos 1-4 (búsqueda por texto libre andando, vectorización en el browser, test de equivalencia como gate). Actualizar la estructura del repo (vectorizer.mjs, package.json, tests/equivalence) y aclarar que el hosting del modelo en producción y el CI se resuelven en Pasos 6+.
- PRESENTACION.md (EDITAR/append): fragmento del Paso 4 (~3 párrafos) — el mismo model.onnx vectorizando tu query en el navegador, por qué la equivalencia Python↔JS es el riesgo central y cómo el golden test la convierte en un gate de CI, y la demo de tipear una frase ('juego para jugar con amigos en el sillón') y obtener el top-5.

## Files in Scope

- `site/js/vectorizer.mjs`
- `site/js/search.mjs`
- `site/js/app.mjs`
- `site/index.html`
- `site/css/styles.css`
- `scripts/emit_reference_vectors.py`
- `scripts/vectorize.py`
- `tests/equivalence/embed.equiv.test.mjs`
- `tests/fixtures/query-vectors.reference.json`
- `package.json`
- `.gitignore`
- `scripts/check_site.py`
- `README.md`
- `PRESENTACION.md`

## Constraints

- Arquitectura cerrada (ADR-001 + brief): sitio 100% estático, HTML + JS vanilla para la app, onnxruntime-web (vía Transformers.js) para la inferencia en el browser, similitud coseno client-side. NO introducir frameworks ni bundlers para el sitio (React/Vue/Vite/webpack quedan fuera). La ÚNICA dependencia JS nueva es Transformers.js: en el browser entra por import map → CDN (sin npm install), y en Node se instala solo para el equivalence test.
- Mantener search.mjs PURO y testeable con node:test SIN dependencias: la vectorización del browser (Transformers.js/ort-web) vive en site/js/vectorizer.mjs. cosineSimilarity y topK no cambian. Si vectorizeQuery() importara la lib desde search.mjs, importar search.mjs en node:test arrastraría la dependencia — por eso se separa.
- DRY: la búsqueda por texto libre reusa EXACTAMENTE topK/cosineSimilarity de search.mjs (la misma maquinaria que 'buscar similares', solo cambia de dónde sale el queryVector). El generador de referencia reusa el embed() de vectorize.py; no se reescribe pooling/L2 en Python.
- Mismo modelo que el CI: Xenova/all-MiniLM-L6-v2 quantized (model_quantized.onnx), el mismo artefacto que fija download_model.py. Mismo modelo + mismo tokenizer.json + mismo mean pooling + L2 en ambos lados → mismo espacio semántico (ADR-001).
- La equivalencia es el criterio de aceptación central (riesgo #1 del ADR-001): objetivo de tolerancia 1e-5 sobre el diff numérico MÁS identidad del ranking top-k como gate robusto. Si 1e-5 resulta inviable sobre el modelo int8 entre ort-Python y ort-web, documentar y justificar la tolerancia empírica elegida, manteniendo el ranking idéntico como condición dura.
- FUERA de alcance del Paso 4: .github/workflows/ci.yml (Paso 6), Docker (Paso 7) y los tests de regresión semántica autogenerados desde search-expectations.yaml (Paso 5, aunque el Paso 4 los habilita). El hosting del modelo en producción (GitHub Pages; models/ es gitignored) se decide y cablea en el build del Paso 6 — en Paso 4 solo se documenta y se hace andar el preview local.
- No commitear nada pesado: models/, dist/ y node_modules/ siguen gitignored. No subir el modelo ni los embeddings al repo.
- Avanzar paso a paso: al terminar el Paso 4, pausar y esperar confirmación del usuario antes del Paso 5. Cerrar con /cortex-documenter; si algún hook required falla (p. ej. la equivalencia no entra en tolerancia o el modelo no se pudo bajar en el entorno) o queda algo a medias, cerrar como 'handoff', no 'closed'.
- Español rioplatense (voseo), didáctico, pensado para la defensa oral de 5 min.

## Acceptance Criteria

- [ ] Existe site/js/vectorizer.mjs y exporta async vectorizeQuery(text) que devuelve un vector L2-normalizado de 384 dims vía Transformers.js (feature-extraction, pooling:'mean', normalize:true), con el pipeline cacheado.
- [ ] La caja de búsqueda por texto libre de index.html está HABILITADA; al tipear una frase y enviar, se muestra el top-5 por coseno descendente (reusando topK), con un estado de carga durante la primera descarga del modelo y manejo de error si falla.
- [ ] search.mjs sigue puro (sin imports pesados): `node --test site/js/search.test.mjs` termina exit 0.
- [ ] Existe el equivalence test y pasa: para las queries del fixture, max |diff| entre el vector JS y el de referencia Python < tolerancia (objetivo 1e-5; si se relaja, queda documentado) Y el ranking top-k (ids) coincide con el de Python.
- [ ] scripts/emit_reference_vectors.py genera tests/fixtures/query-vectors.reference.json reusando el embed() de vectorize.py (no duplica pooling/L2).
- [ ] package.json declara la devDependency '@huggingface/transformers'; el sitio renderiza catálogo + 'buscar similares' SIN npm install (usa el import map al CDN).
- [ ] `python scripts/check_site.py` termina exit 0: vectorizer.mjs presente, la caja de texto libre ya no está deshabilitada, assets referenciados.
- [ ] `python scripts/validate_catalog.py` sigue exit 0 y `ruff check .` sigue verde (Pasos 1-3 intactos).
- [ ] README 'Estado actual' refleja Pasos 1-4 y PRESENTACION.md tiene el fragmento del Paso 4.
- [ ] Nada pesado commiteado: models/, dist/ y node_modules/ siguen gitignored.

## Verification Hooks

Commands that objectively prove the work is done. Run by
`cortex finish-session` (Pluggable Middle, Phase 01).

### js-equivalence
```bash
node --test tests/equivalence/embed.equiv.test.mjs
```

Success: exit code 0 — el vector JS (Transformers.js) coincide con el de referencia Python dentro de tolerancia (objetivo 1e-5) y el ranking top-k es idéntico. Requiere `npm install` y el modelo accesible. · Timeout: 600s
### js-pure-functions
```bash
node --test site/js/search.test.mjs
```

Success: exit code 0 — cosineSimilarity y topK siguen correctas y search.mjs sigue puro (sin dependencias). · Timeout: 180s
### site-structure
```bash
python scripts/check_site.py
```

Success: exit code 0 — vectorizer.mjs presente, caja de texto libre habilitada, assets referenciados, embeddings.json (si existe) con dimensions==384. · Timeout: 120s
### catalog-still-green
```bash
python scripts/validate_catalog.py
```

Success: exit code 0 — el Paso 4 no rompió la validación del catálogo (Pasos 1-2). · Timeout: 120s
### ruff-lint *(optional)*
```bash
ruff check .
```

Success: exit code 0 — código Python limpio (incl. emit_reference_vectors.py). · Timeout: 180s
