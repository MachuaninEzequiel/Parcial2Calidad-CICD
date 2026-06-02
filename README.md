# 🎮 Buscador Semántico de Videojuegos

[![CI](https://github.com/MachuaninEzequiel/Parcial2Calidad-CICD/actions/workflows/ci.yml/badge.svg)](https://github.com/MachuaninEzequiel/Parcial2Calidad-CICD/actions/workflows/ci.yml)

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
| Servidor de Integración Continua | GitHub Actions ✅ — `.github/workflows/ci.yml` (Paso 6) |
| Entorno del dev con build local | Docker ✅ — `Dockerfile` + `docker/entrypoint.sh` (Paso 7) |
| Prueba automatizada | pytest (unitarios + regresión semántica) + gate de equivalencia ✅ |
| Build que despliega | GitHub Actions ✅ — job `deploy` → GitHub Pages (CD, en push a `main`) |
| Entornos de entrega | GitHub Pages ✅ — [sitio público](https://machuaninezequiel.github.io/Parcial2Calidad-CICD/) |
| Mecanismo de feedback | Status checks en PRs + badges + notificaciones de GitHub |

> **CI (Integración Continua):** cada push se integra, valida y prueba automáticamente.
> **CD (Entrega Continua):** si todo pasa, se despliega solo a producción.

---

## Spec Driven Development — las tres capas

- **Capa A · Schema estructural** (`schemas/game.schema.yaml`): define qué campos tiene un juego y qué valores son válidos (géneros, plataformas, longitudes). El CI rechaza cualquier `.md` que no lo cumpla.
- **Capa B · Expectativas de búsqueda** (`specs/search-expectations.yaml`): declara qué juegos deberían aparecer para ciertas queries. De acá salen tests de **regresión semántica**: si un juego nuevo degrada una búsqueda que antes andaba, el CI avisa.
- **Capa C · La spec como postura**: la lista de géneros vive **solo** en el schema; el frontend y los tests la consumen de ahí. Un campo nuevo se agrega primero al schema, después a los `.md`, después al frontend. Nunca al revés.

---

## Estado actual — Pasos 1-8 ✅ (CI/CD completo)

- **Paso 1 ✅ · base SDD:** schema, expectativas, catálogo inicial (10 juegos) y el validador.
- **Paso 2 ✅ · vectorización ONNX:** `scripts/vectorize.py` recorre el catálogo, lo pasa por **all-MiniLM-L6-v2** (ONNX), aplica mean pooling + normalización L2 y genera `dist/embeddings.json` (10 items, vectores de 384 dimensiones).
- **Paso 3 ✅ · frontend estático + motor de ranking:** sitio en `site/` (HTML + CSS + JS vanilla, sin frameworks) que carga `embeddings.json`, lista los 10 juegos y permite **buscar juegos similares** por similitud coseno client-side. Las funciones puras (`cosineSimilarity`, `topK`) viven en `site/js/search.mjs` y se testean con el runner nativo `node:test`.
- **Paso 4 ✅ · búsqueda por texto libre + equivalencia Python↔JS:** la caja de texto libre está **habilitada**. Al escribir una frase, el navegador la vectoriza con el **mismo `model.onnx`** del CI (vía **Transformers.js** = onnxruntime-web, que entra por un **import map → CDN**, sin npm install) y rankea el catálogo con la misma `topK`. La vectorización vive aislada en `site/js/vectorizer.mjs` para que `search.mjs` siga puro. Y el corazón del paso: un **test de equivalencia** (`tests/equivalence/embed.equiv.test.mjs`) prueba que el vector de JavaScript coincide con el de referencia de Python dentro de `1e-5` **y** que el ranking top-k es idéntico — la mitigación del riesgo #1 del ADR-001.

- **Paso 5 ✅ · regresión semántica + catálogo afinado:** el loop SDD se cierra. `tests/test_search_regression.py` lee `specs/search-expectations.yaml` **en runtime** y genera un test parametrizado por expectativa (Capa B → tests): vectoriza cada query reusando el `embed()` de `vectorize.py` **sin padding** (régimen browser, ADR-002), rankea contra `dist/embeddings.json` por coseno y exige que `must_include_any_of` caiga en el top-k. Para que el ranking sea bueno con el modelo chico de inglés, se afinó el **contenido del catálogo en español** (ADR-003) en vez de cambiar de modelo: ahora *"juego para jugar con amigos en el sillón"* devuelve **Overcooked 2 en el puesto #1** y *"souls-like para principiantes"* devuelve **Hollow Knight en el #1**, ambas reales. La demo de la línea 5 ya no es aspiracional. En el CI (Paso 6), estos tests corren como gate junto al resto.

- **Paso 6 ✅ · Integración Continua (GitHub Actions):** `.github/workflows/ci.yml` corre en **cada push y cada PR** los MISMOS gates que probás localmente (ver más abajo). Es **Integración Continua**: la Entrega Continua (CD a GitHub Pages) llegó en el cierre (ver el bullet de CD); Docker es el Paso 7.

- **Paso 7 ✅ · Docker (entorno de build reproducible):** un `Dockerfile` (Python + Node + deps) empaqueta TODO el pipeline en una imagen. `docker run` corre los mismos gates que el CI sin instalar nada en tu máquina — el clásico *"en mi máquina anda"* deja de ser un problema. El `docker/entrypoint.sh` tiene 3 subcomandos: `ci` (pipeline completo), `vectorize` y `serve` (sitio en `:8000`). Ver **"Correr todo en Docker"** más abajo. (Es el entorno de build local de la consigna.)

- **Cierre ✅ · Entrega Continua (CD) a GitHub Pages:** el job `deploy` de `.github/workflows/ci.yml` se dispara en **push a `main`** (solo si el job `ci` pasó) y publica el sitio en **GitHub Pages** con `actions/deploy-pages`. Con esto el ciclo **CI/CD queda completo**: build local con Docker + CI con Actions + CD a Pages. El sitio público vive en **https://machuaninezequiel.github.io/Parcial2Calidad-CICD/**. En producción el navegador baja el modelo del **HF CDN** (Transformers.js), así que no hace falta hostearlo; el `embeddings.json` viaja en el artefacto de Pages. (Pages se habilita una vez en *Settings → Pages → Source = GitHub Actions*.)

> **Detalle clave de la equivalencia:** el catálogo (Paso 2) se vectoriza con el tokenizer pad-eando a 128 tokens; el navegador vectoriza la query **sin padding** (solo los tokens reales). Como el modelo es int8, el largo de secuencia afecta la cuantización, así que la referencia de Python (`scripts/emit_reference_vectors.py`) también vectoriza las queries **sin padding** para reproducir EXACTO lo que hace el browser. Con eso el diff cae de ~3e-2 a ~4e-8. El test de regresión del Paso 5 vectoriza la query con el MISMO régimen sin padding, así el ranking del gate coincide con el del navegador.

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

### Integración Continua — GitHub Actions (Paso 6)

`.github/workflows/ci.yml` corre en **cada push y cada PR** los MISMOS gates que probás localmente, en orden de dependencias:

1. `ruff check .` — lint del código Python.
2. `python scripts/validate_catalog.py` (+ el test negativo) — el catálogo cumple el schema (Capa A).
3. `python scripts/vectorize.py` — regenera `dist/embeddings.json` con el modelo ONNX.
4. `python -m pytest tests/` — unitarios (Paso 2) + **regresión semántica** (Paso 5).
5. `python scripts/check_site.py` — estructura del sitio.
6. `node --test site/js/search.test.mjs` — funciones puras (sin npm).
7. `node --test tests/equivalence/embed.equiv.test.mjs` — **equivalencia Python↔JS** (riesgo #1 del ADR-001).

El modelo (~23 MB) se baja una vez y se **cachea** entre runs. El principio: *lo que valida tu máquina es exactamente lo que valida el servidor*. El mismo workflow tiene además el job **`deploy`** (CD) que publica el sitio en GitHub Pages en cada push a `main`, pero **solo si el job `ci` pasó** (ver el bullet de CD más arriba). El badge refleja el último run del CI.

### Correr todo en Docker (Paso 7)

Docker empaqueta el **entorno de build local** de la consigna: la misma imagen corre el pipeline igual que el CI, sin que instales Python, Node ni las dependencias en tu máquina.

```bash
# 1. Construir la imagen (instala deps + hornea el modelo + precomputa embeddings)
docker build -t buscador-semantico .

# 2. Correr el PIPELINE COMPLETO (paridad con GitHub Actions): ruff + validación +
#    vectorización + pytest (regresión semántica) + tests JS + equivalencia
docker run --rm buscador-semantico

# 3. Solo vectorizar el catálogo, dejando el embeddings.json en tu host
docker run --rm -v "$PWD/dist:/app/dist" buscador-semantico vectorize

# 4. Servir el sitio en http://localhost:8000/site/
docker run --rm -p 8000:8000 buscador-semantico serve
```

El subcomando por defecto es `ci` (el pipeline completo). El `docker/entrypoint.sh` **reusa los mismos scripts** que el CI y el dev local — no reimplementa nada. El modelo se hornea en el build (el lado Python anda offline), pero el **test de equivalencia** (Node/Transformers.js) y el **navegador** bajan el modelo del CDN en runtime, así que para esos hace falta red. **Es el entorno de build/dev**: el deploy a producción (CD) se resuelve al cierre del proyecto.

---

## Estructura del repo (hasta el Paso 7)

```
.
├── Dockerfile                    # entorno de build reproducible (Paso 7)
├── .dockerignore                 # qué NO entra al build context
├── docker/
│   └── entrypoint.sh             # subcomandos del contenedor: ci | vectorize | serve
├── .github/
│   └── workflows/
│       └── ci.yml                # CI (gates, Paso 6) + CD (job deploy → Pages en main)
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
│   ├── test_vectorize.py         # unitarios del Paso 2: mean_pooling, l2_normalize, estructura
│   ├── test_search_regression.py # regresión semántica desde la spec (Capa B → tests) — Paso 5
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

> **Estado:** el ciclo **CI/CD está completo** — CI (GitHub Actions) + entorno de build reproducible (Docker) + CD (deploy a GitHub Pages en `main`). Lo único que queda es la **presentación oral** del proyecto (el guion está en `PRESENTACION.md`).
