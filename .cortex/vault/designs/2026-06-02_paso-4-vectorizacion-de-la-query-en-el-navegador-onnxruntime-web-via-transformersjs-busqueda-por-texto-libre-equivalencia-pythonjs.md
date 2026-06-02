---
schema_version: 1
doc_type: design
title: 'Paso 4 — Design doc: vectorización en el browser + equivalencia Python↔JS'
session_id: 2026-06-02_paso-4-vectorizacion-de-la-query-en-el-navegador-onnxruntime-web-via-transformersjs-busqueda-por-texto-libre-equivalencia-pythonjs
created_at: '2026-06-02T19:25:00Z'
---

# Design — Paso 4

Producido por `cortex-SDDwork` (rol designer; el subagent `cortex-code-designer`
no está registrado en este IDE). El implementer DEBE seguir este doc: no
improvisar decisiones de arquitectura.

## 1. Architecture decision

- **Aislar la dependencia pesada.** Toda la vectorización del browser
  (Transformers.js = onnxruntime-web por debajo) vive en un módulo NUEVO
  `site/js/vectorizer.mjs`. `site/js/search.mjs` queda 100% puro: se le QUITA el
  seam `vectorizeQuery()` (que hoy lanza el Error "Paso 4", líneas 76-95) y su
  comentario que menciona "Paso 4". Motivo (constraint del spec): si
  `vectorizeQuery` viviera en search.mjs, importar search.mjs en `node:test`
  arrastraría `@huggingface/transformers` y rompería `node --test
  site/js/search.test.mjs`, que debe seguir corriendo sin instalar nada.
- **El test de las funciones puras pierde la verificación del seam.** En
  `site/js/search.test.mjs` (líneas 13 y 88-90) hay un import de `vectorizeQuery`
  y un test `assert.throws(... /Paso 4/)`. Ambos deben ELIMINARSE (el seam ya no
  vive en search.mjs). NO agregar un import de vectorizer.mjs a search.test.mjs:
  contaminaría el test puro con la dependencia. La equivalencia se prueba en su
  propio archivo (`tests/equivalence/embed.equiv.test.mjs`).
- **Mismo bare specifier en browser y Node.** `vectorizer.mjs` importa
  `'@huggingface/transformers'`. En el browser el bare specifier lo resuelve un
  **import map** en `<head>` → CDN ESM (sin bundler, sin npm install). En Node lo
  resuelve la devDependency instalada (solo para el gate de equivalencia).
  **El número de versión del import map y el de package.json DEBEN coincidir
  exactamente** para que browser y Node ejecuten el mismo código.
- **DRY en el ranking.** La búsqueda por texto libre reusa `topK` /
  `cosineSimilarity` de search.mjs tal cual. Lo único que cambia respecto a
  "buscar similares" es de dónde sale el `queryVector` (de `vectorizeQuery`
  en vez del vector de un item).
- **DRY en Python.** `emit_reference_vectors.py` reusa `embed()` de
  `vectorize.py` (tokenización + mean pooling + L2). No se reescribe el pipeline.

## 2. API contracts

### `site/js/vectorizer.mjs` (NUEVO)
```js
import { pipeline /*, env */ } from '@huggingface/transformers';

let _extractorPromise = null;            // pipeline cacheado (se baja/instancia 1 vez)

function getExtractor() {
  if (!_extractorPromise) {
    // dtype 'q8' = carga onnx/model_quantized.onnx (int8): el MISMO artefacto
    // que models/model.onnx (download_model.py baja onnx/model_quantized.onnx).
    _extractorPromise = pipeline('feature-extraction', 'Xenova/all-MiniLM-L6-v2', { dtype: 'q8' });
  }
  return _extractorPromise;
}

export async function vectorizeQuery(text) {
  const extractor = await getExtractor();
  const output = await extractor(text, { pooling: 'mean', normalize: true });
  return Array.from(output.data);        // 384 floats, L2-normalizado
}
```
- **CRÍTICO (equivalencia):** Node DEBE cargar el modelo **int8 quantized**
  (`model_quantized.onnx`), igual que Python. Con el paquete v3
  `@huggingface/transformers` el knob es `dtype:'q8'` (NO `{quantized:true}`, que
  era la API de v2 `@xenova/transformers`). El spec escribió `{quantized:true}`
  como intención; traducila al knob correcto de la versión que instales y
  **verificá que efectivamente carga `model_quantized.onnx`** (si carga fp32, el
  diff numérico contra Python int8 explota). Documentá en un comentario qué
  versión instalaste y qué opción usaste.
- `{pooling:'mean', normalize:true}` reproduce el mean pooling ponderado por
  attention_mask + L2 de `vectorize.py` (`mean_pooling` + `l2_normalize`).
- Modelo: por defecto se baja de HF Hub (repo `Xenova/all-MiniLM-L6-v2`, el mismo
  que `download_model.py`) y queda cacheado. Documentá en comentario el fallback
  opcional a `models/` local vía `env.localModelPath` / `env.allowRemoteModels`
  (no es obligatorio cablearlo: el spec pide "documentar el fallback al CDN").

### `scripts/emit_reference_vectors.py` (NUEVO)
Genera `tests/fixtures/query-vectors.reference.json`:
```json
{
  "model": "all-MiniLM-L6-v2",
  "dimensions": 384,
  "tolerance": 1e-5,
  "queries": [
    { "text": "...", "vector": [384 floats], "top_k_ids": ["id1", ...] }
  ]
}
```
- Reconfigurar stdout a UTF-8 (patrón de los demás scripts).
- Reusar de `vectorize.py`: `embed`, y el setup de session+tokenizer. Para evitar
  duplicar el setup, **refactor mínimo en `vectorize.py`**: extraé un helper
  `load_model()` que devuelva `(session, tokenizer, input_names)` y usalo tanto en
  `vectorize.main()` como acá. NO cambiar el comportamiento del Paso 2
  (los embeddings.json deben salir idénticos).
- Queries FIJAS = las 5 de `specs/search-expectations.yaml` + 1 corta de control
  (ej. `"hola"`). Leé el YAML con `yaml.safe_load` (pyyaml ya es dependencia).
- `top_k_ids`: rankear cada query contra `dist/embeddings.json` por coseno
  (= producto punto, vectores normalizados), tomar los 5 mejores ids. Esto es la
  referencia de ranking que el test JS debe reproducir idéntica.
- **Precisión:** NO redondear los floats del vector a 8 decimales (vectorize.py
  redondea a 8 para embeddings.json, pero acá necesitamos full precision para
  comparar contra 1e-5). Escribí los floats nativos.

### `tests/equivalence/embed.equiv.test.mjs` (NUEVO)
- Runner `node:test`. Importa `vectorizeQuery` de `../../site/js/vectorizer.mjs`
  y `topK` de `../../site/js/search.mjs`. Carga el fixture y
  `../../dist/embeddings.json` (rutas robustas vía `new URL(..., import.meta.url)`).
- Por cada query del fixture:
  - `jsVec = await vectorizeQuery(text)`; assert `jsVec.length === 384`.
  - `maxAbsDiff(jsVec, refVec) < tolerance` (tolerance leída del fixture).
  - `topK(jsVec, items, 5)` → ids; `assert.deepEqual(ids, query.top_k_ids)`
    (identidad de ranking = **gate duro**).
- Un solo `getExtractor` se cachea entre queries (la primera baja el modelo).
- Subí el timeout si hace falta (la primera corrida baja ~23 MB).

## 3. Wiring del DOM — `site/js/app.mjs` (EDITAR)

- **Lazy import:** NO importar vectorizer.mjs estáticamente arriba. Importarlo con
  `await import('./vectorizer.mjs')` recién cuando el usuario hace la PRIMERA
  búsqueda por texto. Así el catálogo y "buscar similares" funcionan aunque el
  CDN de Transformers.js falle o tarde (cumple "el sitio renderiza catálogo +
  similares SIN npm install" y agrega resiliencia).
- Guardar los `items` cargados en una variable de módulo (hoy `init()` los pasa a
  `renderCatalog` y se pierden) para que el handler de texto libre los use.
- **Refactor DRY de render:** extraer de `showSimilar` una función
  `renderResults(headingText, ranked)` que arme la `<ol>` de resultados, y que
  TANTO "buscar similares" COMO la búsqueda por texto libre la usen. No duplicar
  el render.
- Handler de la caja: en `submit` (envolver el input en un `<form>` o escuchar
  Enter + botón). Al enviar con texto no vacío:
  1. estado de carga: deshabilitar input/botón, mostrar mensaje tipo "Bajando el
     modelo (~23 MB la primera vez)…" / spinner.
  2. `const { vectorizeQuery } = await import('./vectorizer.mjs')`.
  3. `const qv = await vectorizeQuery(text)`.
  4. `const ranked = topK(qv, items, 5)`; `renderResults('Resultados para "<q>"', ranked)`.
  5. rehabilitar input/botón. `try/catch` con mensaje de error claro si el modelo
     no carga (reusar el estilo `.error`).
- "Buscar similares" queda intacto en comportamiento.

## 4. `site/index.html` (EDITAR)
- **HABILITAR** `<input id="free-query">`: quitar `disabled` y `aria-disabled`.
  Actualizar `placeholder` a algo usable (ej. `juego para jugar con amigos en el
  sillón`). Envolverlo en `<form>` con un botón "Buscar".
- Reemplazar la nota `🔒 Disponible en el Paso 4` por una pista de uso + aviso de
  que la PRIMERA búsqueda baja el modelo (~23 MB) y puede tardar.
- Agregar en `<head>`, **antes** del `<script type="module" src="js/app.mjs">`, un
  `<script type="importmap">` que mapee `@huggingface/transformers` a la URL ESM
  del CDN, con la **misma versión** que package.json. Ej.:
  `https://cdn.jsdelivr.net/npm/@huggingface/transformers@<VERSION>`.
- Opcional: zona/estado de carga (puede vivir dentro de la `.search-box`).
- Actualizar el comentario que dice "deshabilitada hasta el Paso 4" y el footer
  ("Paso 3"/"llega en el Paso 4") para reflejar Paso 4.

## 5. `site/css/styles.css` (EDITAR)
- La regla `.search-box input[type="search"]` hoy tiene `cursor: not-allowed` y
  color apagado (estado deshabilitado). Darle estilo de input ACTIVO (cursor
  text, foco visible). Estilos para el botón "Buscar" y para el estado de
  carga/spinner. Sin frameworks CSS.

## 6. `package.json` (NUEVO, raíz)
- `"type": "module"`, `"private": true`.
- `devDependencies`: `"@huggingface/transformers": "<VERSION exacta instalada>"`.
- `scripts`: `"test:equiv": "node --test tests/equivalence/embed.equiv.test.mjs"`,
  `"test:pure": "node --test site/js/search.test.mjs"`.
- Comentario/README: el SITIO no necesita `npm install` (usa el import map al
  CDN); la instalación es solo para el gate de equivalencia en CI/local.

## 7. `.gitignore` (EDITAR)
- Agregar `node_modules/` y el cache de modelos de Transformers.js en Node
  (`.cache/`). models/, dist/ ya están ignorados.

## 8. `scripts/check_site.py` (EDITAR)
- Sumar `site/js/vectorizer.mjs` a `REQUIRED_FILES`.
- Nuevo check portable: la caja de texto libre está HABILITADA. Con `re`,
  extraer el tag `<input ... id="free-query" ...>` y assert que NO contiene
  `disabled`. Assert que `<script type="importmap"` está en el html (prueba el
  wiring de Transformers.js). Assert que ya NO aparece `Disponible en el Paso 4`.
- Mantener el check de `dist/embeddings.json` (dimensions==384). Mensajes estilo
  validate_catalog.py.

## 9. Docs
- `README.md`: "Estado actual" → Pasos 1-4 (búsqueda por texto libre andando,
  vectorización en el browser, test de equivalencia como gate). Actualizar la
  estructura del repo (vectorizer.mjs, package.json, tests/equivalence/) y aclarar
  que el hosting del modelo en producción y el CI se resuelven en Pasos 6+.
- `PRESENTACION.md`: append "Fragmento · Paso 4" (~3 párrafos): el mismo
  model.onnx vectorizando tu query en el navegador; por qué la equivalencia
  Python↔JS es el riesgo #1 del ADR-001 y cómo el golden test la vuelve un gate de
  CI; demo de tipear "juego para jugar con amigos en el sillón" → top-5 con
  Overcooked 2. Voseo rioplatense, didáctico.

## 10. Test plan (orden de verificación)
1. `python scripts/vectorize.py` (regenera embeddings.json; debe seguir 10 items).
2. `python scripts/emit_reference_vectors.py` → genera el fixture.
3. `npm install` (instala @huggingface/transformers + onnxruntime-node).
4. `node --test tests/equivalence/embed.equiv.test.mjs` → diff < tolerance y
   ranking idéntico.
5. `node --test site/js/search.test.mjs` → sigue verde y SIN dependencias
   (debe correr aunque node_modules tenga transformers: search.mjs no lo importa).
6. `python scripts/check_site.py` → exit 0.
7. `python scripts/validate_catalog.py` → exit 0 (Paso 1-2 intactos).
8. `ruff check .` → verde (incl. emit_reference_vectors.py).

## 11. Riesgos y reglas de decisión
- **Equivalencia 1e-5 sobre int8 (riesgo #1 ADR-001).** Si el `max |diff|` no
  entra en 1e-5 entre ort-Python y onnxruntime-node (mismo .onnx int8, mismo
  tokenizer.json), el spec PERMITE relajar la tolerancia documentándola
  empíricamente, PERO la **identidad del ranking top-k es condición dura** y NO se
  relaja. Procedimiento: correr el test, observar el `max |diff|` real, fijar
  `tolerance` en el fixture al valor empírico (ej. 1e-3) con un comentario que
  explique por qué, y mantener el assert de ranking. Loguear el diff observado.
- **dtype incorrecto.** Si Node carga fp32 en vez de int8, el diff explota.
  Verificá el modelo cargado.
- **Pureza de search.mjs.** Si `node --test site/js/search.test.mjs` empieza a
  requerir npm, algo importó la lib en la cadena de search.mjs → revertir.
- **Cierre.** Si algún hook required falla (equivalencia fuera de tolerancia
  incluso relajada, o el modelo no se pudo bajar en el entorno) o queda algo a
  medias → la sesión se cierra como **handoff**, no closed (decisión del
  documenter; el implementer solo reporta el estado real en su checkpoint).
- **Nada pesado commiteado:** models/, dist/, node_modules/ siguen gitignored.
