# 🎮 Buscador Semántico de Videojuegos

> Catálogo de videojuegos en Markdown que se vectoriza con un modelo de IA dentro del pipeline de CI y se busca por **significado** —no por palabras clave— 100% en el navegador.

Escribís *"juego para jugar con amigos en el sillón"* y te devuelve **Overcooked 2**, aunque esa frase no aparezca escrita en ningún lado. Eso son **embeddings**: representar texto como vectores numéricos y comparar por cercanía semántica.

> Este proyecto sigue **Spec Driven Development**: los archivos `schemas/` y `specs/` son la **fuente de verdad**, y el código y los tests se derivan de ellos.

---

## ¿Cómo funciona? (flujo de punta a punta)

```
[Dev local]  edita un .md de un juego  ──git push──▶  [GitHub repo]
                                                            │ trigger
                                                            ▼
                                              [GitHub Actions = servidor de CI]
   1. Valida el schema (SDD)   check-jsonschema sobre cada .md
   2. Lint & tests             ruff + pytest
   3. Vectoriza                model.onnx → embeddings.json
   4. Build                    empaqueta el sitio estático
                                                            │ deploy (si es main)
                                                            ▼
                                              [GitHub Pages = producción]
                                                            │
                                                            ▼
[Browser]  el MISMO model.onnx vectoriza tu query
           → similitud coseno contra embeddings.json → top 5 resultados
```

La pieza central: **el mismo `model.onnx` corre en dos lugares**. En el CI (con Python) vectoriza el catálogo entero; en el navegador (con JavaScript) vectoriza tu búsqueda. Mismo modelo → mismo espacio semántico → las comparaciones son válidas.

---

## Cómo se mapea a la consigna de CI/CD

| Bloque del esquema teórico | Implementación concreta |
|---|---|
| Control de versiones | GitHub (`main` + feature branches + PRs) |
| Servidor de Integración Continua | GitHub Actions |
| Entorno del dev con build local | Docker + script de vectorización local |
| Prueba automatizada | pytest (unitarios) + tests semánticos desde la spec |
| Build que despliega | Job de deploy en Actions → GitHub Pages |
| Entornos de entrega | GitHub Pages (producción) |
| Mecanismo de feedback | Status checks en PRs + badges + notificaciones de GitHub |

> **CI (Integración Continua):** cada push se integra, valida y prueba automáticamente.
> **CD (Entrega Continua):** si todo pasa, se despliega solo a producción.

---

## Spec Driven Development — las tres capas

- **Capa A · Schema estructural** (`schemas/game.schema.yaml`): define qué campos tiene un juego y qué valores son válidos (géneros, plataformas, longitudes). El CI rechaza cualquier `.md` que no lo cumpla.
- **Capa B · Expectativas de búsqueda** (`specs/search-expectations.yaml`): declara qué juegos deberían aparecer para ciertas queries. De acá salen tests de **regresión semántica**: si un juego nuevo degrada una búsqueda que antes andaba, el CI avisa.
- **Capa C · La spec como postura**: la lista de géneros vive **solo** en el schema; el frontend y los tests la consumen de ahí. Un campo nuevo se agrega primero al schema, después a los `.md`, después al frontend. Nunca al revés.

---

## Estado actual — Pasos 1-4 ✅

- **Paso 1 ✅ · base SDD:** schema, expectativas, catálogo inicial (10 juegos) y el validador.
- **Paso 2 ✅ · vectorización ONNX:** `scripts/vectorize.py` recorre el catálogo, lo pasa por **all-MiniLM-L6-v2** (ONNX), aplica mean pooling + normalización L2 y genera `dist/embeddings.json` (10 items, vectores de 384 dimensiones).
- **Paso 3 ✅ · frontend estático + motor de ranking:** sitio en `site/` (HTML + CSS + JS vanilla, sin frameworks) que carga `embeddings.json`, lista los 10 juegos y permite **buscar juegos similares** por similitud coseno client-side. Las funciones puras (`cosineSimilarity`, `topK`) viven en `site/js/search.mjs` y se testean con el runner nativo `node:test`.
- **Paso 4 ✅ · búsqueda por texto libre + equivalencia Python↔JS:** la caja de texto libre está **habilitada**. Al escribir una frase, el navegador la vectoriza con el **mismo `model.onnx`** del CI (vía **Transformers.js** = onnxruntime-web, que entra por un **import map → CDN**, sin npm install) y rankea el catálogo con la misma `topK`. La vectorización vive aislada en `site/js/vectorizer.mjs` para que `search.mjs` siga puro. Y el corazón del paso: un **test de equivalencia** (`tests/equivalence/embed.equiv.test.mjs`) prueba que el vector de JavaScript coincide con el de referencia de Python dentro de `1e-5` **y** que el ranking top-k es idéntico — la mitigación del riesgo #1 del ADR-001.

> **Detalle clave de la equivalencia:** el catálogo (Paso 2) se vectoriza con el tokenizer pad-eando a 128 tokens; el navegador vectoriza la query **sin padding** (solo los tokens reales). Como el modelo es int8, el largo de secuencia afecta la cuantización, así que la referencia de Python (`scripts/emit_reference_vectors.py`) también vectoriza las queries **sin padding** para reproducir EXACTO lo que hace el browser. Con eso el diff cae de ~3e-2 a ~4e-8.

### Validar el catálogo localmente

```bash
# Instalar dependencias mínimas (pyyaml + jsonschema + numpy + onnxruntime + ...)
pip install -e .

# Validar que TODOS los juegos cumplen el schema
python scripts/validate_catalog.py

# Probar que el validador RECHAZA un .md malformado (test negativo)
python scripts/validate_catalog.py --expect-fail tests/fixtures/invalid-game.md
```

El primer comando termina en verde (exit 0). El segundo **también** termina en verde, porque el archivo malo es rechazado tal como se espera.

### Probar el frontend localmente (Pasos 3-4)

```bash
# 1. Generar los embeddings (si todavía no los tenés)
python scripts/vectorize.py

# 2. Verificar que el sitio está completo y coherente
python scripts/check_site.py

# 3. Correr los tests de las funciones puras (sin npm)
node --test site/js/search.test.mjs

# 4. Servir la RAÍZ del repo y abrir el sitio en el navegador
python -m http.server 8000
#    → abrir http://localhost:8000/site/
```

El sitio fetchea `../dist/embeddings.json`, así que hay que servir la **raíz del repo** (no `site/`). En cada card, "Buscar similares" devuelve el top-5 por coseno descendente. En la caja de arriba, escribí una frase (ej. *"juego para jugar con amigos en el sillón"*) y dale **Buscar**: la primera vez baja el modelo (~23 MB) desde el CDN y después es instantáneo. **El sitio NO necesita `npm install`** — Transformers.js entra por el import map al CDN.

### Correr el gate de equivalencia Python↔JS (Paso 4)

```bash
# Esto SÍ necesita npm (solo para el test, no para el sitio):
npm install                                   # instala @huggingface/transformers (devDep)
python scripts/vectorize.py                   # catálogo vectorizado (con padding)
python scripts/emit_reference_vectors.py      # vectores de referencia Python (sin padding)
node --test tests/equivalence/embed.equiv.test.mjs   # diff < 1e-5 y ranking idéntico
```

`emit_reference_vectors.py` reusa el `embed()` de `vectorize.py` (DRY) y escribe `tests/fixtures/query-vectors.reference.json`. El test en Node vectoriza las mismas queries con Transformers.js y verifica equivalencia numérica + identidad de ranking.

---

## Estructura del repo (hasta el Paso 4)

```
.
├── schemas/
│   └── game.schema.yaml          # SDD Capa A · fuente de verdad estructural
├── specs/
│   └── search-expectations.yaml  # SDD Capa B · expectativas de búsqueda
├── catalog/                      # un .md por juego (frontmatter + sinopsis)
│   ├── hollow-knight.md
│   └── ...                       # 10 juegos
├── site/                         # frontend estático (Pasos 3-4)
│   ├── index.html                # estructura + import map (Transformers.js → CDN)
│   ├── css/
│   │   └── styles.css            # estilos propios, sin frameworks
│   └── js/
│       ├── search.mjs            # funciones puras: cosineSimilarity, topK (sin npm)
│       ├── vectorizer.mjs        # vectorización en el browser (Transformers.js) — Paso 4
│       ├── app.mjs               # wiring de DOM: fetch, render, similares + texto libre
│       └── search.test.mjs       # tests con el runner nativo node:test
├── scripts/
│   ├── catalog_io.py             # parsing compartido del catálogo (DRY)
│   ├── validate_catalog.py       # valida cada .md contra el schema
│   ├── vectorize.py              # genera dist/embeddings.json con ONNX (Paso 2)
│   ├── emit_reference_vectors.py # vectores de referencia Python para la equivalencia (Paso 4)
│   └── check_site.py             # chequeo estructural del sitio (Pasos 3-4)
├── tests/
│   ├── equivalence/
│   │   └── embed.equiv.test.mjs  # gate de equivalencia Python↔JS (Paso 4)
│   └── fixtures/
│       ├── invalid-game.md       # .md malformado para el test negativo
│       └── query-vectors.reference.json  # referencia dorada (la genera emit_reference_vectors.py)
├── dist/                         # output del build (gitignored) · embeddings.json
├── models/                       # model.onnx + tokenizer (gitignored)
├── node_modules/                 # devDep del equivalence test (gitignored)
├── package.json                  # devDependency @huggingface/transformers + scripts de test
├── pyproject.toml                # dependencias + config de ruff
└── README.md
```

> **Próximos pasos:** tests de regresión semántica autogenerados desde `search-expectations.yaml` (Paso 5), GitHub Actions con el deploy a Pages y el hosting del modelo en producción (Paso 6), Docker (Paso 7) y la presentación oral (Paso 8).
