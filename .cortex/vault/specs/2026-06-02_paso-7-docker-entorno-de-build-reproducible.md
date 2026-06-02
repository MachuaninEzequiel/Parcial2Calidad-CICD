---
schema_version: 1
doc_type: spec
title: 'Paso 7 — Docker: entorno de build reproducible'
created_at: '2026-06-02T21:37:10.634252Z'
updated_at: '2026-06-02T21:37:10.634252Z'
tags:
- spec
- spec
- sdd
- ci-cd
- paso-7
- docker
- dockerfile
- build-reproducible
- entorno-dev
- pipeline
status: draft
links: []
vault_scope: local
fingerprint: 1d049e2ab502f7cafe674efa8105e11718e400e8ff1a7e0ad98efb39c60bf0f6
verification_hooks:
- name: docker-artifacts
  command: python -c "import os;assert os.path.exists('Dockerfile') and os.path.exists('.dockerignore');s=open('docker/entrypoint.sh',encoding='utf-8').read();assert
    all(k in s for k in ['ci','vectorize','serve']);print('Dockerfile + entrypoint(ci/vectorize/serve)
    + .dockerignore OK')"
  required: true
  success_criteria: exit code 0 — existen Dockerfile, docker/entrypoint.sh (con los
    3 subcomandos ci/vectorize/serve) y .dockerignore.
  timeout_seconds: 60
- name: docker-build
  command: docker build -t buscador-semantico:test .
  required: false
  success_criteria: exit code 0 — la imagen buildea (instala deps, hornea el modelo).
    SOLO corre si Docker está disponible; es optional porque el entorno puede no tener
    Docker.
  timeout_seconds: 1200
- name: docker-run-ci
  command: docker run --rm buscador-semantico:test ci
  required: false
  success_criteria: exit code 0 — el pipeline completo (paridad con el CI) pasa dentro
    del contenedor. SOLO corre si Docker está disponible (optional). Requiere red
    al HF Hub para el equivalence test.
  timeout_seconds: 1200
goal: 'Empaquetar el entorno de build/dev del proyecto en una imagen Docker — la fila
  ''Entorno del dev con build local'' de la consigna de CI/CD. Un Dockerfile (Python
  3.13 + Node 22 + las dependencias) que corre el MISMO pipeline que GitHub Actions
  (download_model, ruff, validate_catalog, vectorize, pytest incl. regresión semántica,
  check_site, tests JS incl. el gate de equivalencia Python↔JS) dentro de un contenedor,
  sin instalar nada en la máquina del usuario, garantizando reproducibilidad (''en
  mi máquina anda'' se acaba). Un entrypoint con subcomandos cubre las 3 necesidades:
  `ci` (pipeline completo = paridad con el CI; default), `vectorize` (genera dist/embeddings.json
  en un volumen) y `serve` (sirve el sitio estático local en :8000). El entrypoint
  REUSA los scripts del repo tal cual (no reimplementa lógica). NO incluye el CD/deploy
  a GitHub Pages ni el hosting del modelo en producción: eso queda EXPLÍCITAMENTE
  para el cierre del proyecto. Español rioplatense, didáctico, para la defensa oral.'
files_in_scope:
- Dockerfile
- docker/entrypoint.sh
- .dockerignore
- README.md
- PRESENTACION.md
constraints:
- 'Docker = ENTORNO DE BUILD/DEV reproducible (fila ''Entorno del dev con build local''
  de la consigna). NO es el deploy/CD: NADA de nginx de producción ni publicar a GitHub
  Pages (diferido EXPLÍCITAMENTE al cierre del proyecto). El subcomando serve es solo
  para la demo local.'
- El contenedor corre los MISMOS comandos/gates que el CI (.github/workflows/ci.yml)
  y el dev local; el entrypoint REUSA los scripts tal cual (download_model, ruff,
  validate_catalog, vectorize, pytest, check_site, search.test.mjs, embed.equiv.test.mjs).
  NO reimplementar lógica de negocio.
- 'Imagen lo más chica razonable: base slim + `.dockerignore` para no copiar node_modules/models/dist/.git/.cortex
  al build context + limpiar apt lists. NO commitear nada pesado: models/, dist/,
  node_modules/ siguen gitignored en el repo (la imagen los genera/hornea/instala
  adentro).'
- 'El modelo: horneado en el build para el lado Python (offline). El equivalence test
  (Node/Transformers.js) y el browser bajan el modelo del HF CDN en runtime (necesitan
  red); documentarlo. No subir el modelo al repo.'
- 'Limitación conocida (igual que el Paso 6 con Actions): validar la imagen requiere
  Docker instalado. Si Docker NO está disponible en el entorno, entregar el Dockerfile/entrypoint/.dockerignore
  correctos + documentar que el build/run se valida donde haya Docker. Requiere los
  Pasos 4-6 commiteados para que el build context tenga todo (hoy gitless).'
- 'Avanzar paso a paso: al terminar el Paso 7, pausar y esperar confirmación del usuario
  antes del cierre (Paso 8 / CD). Cerrar con /cortex-documenter; si el build de Docker
  no se pudo validar o queda algo a medias, cerrar como ''handoff''.'
- Español rioplatense (voseo) en las docs, didáctico, pensado para la defensa oral
  de 5 min.
acceptance_criteria:
- Existe un Dockerfile válido (base python:3.13-slim + Node 22) que instala las deps
  (`pip install -e .[dev]` + `npm ci`), hornea el modelo (`download_model.py`) y define
  ENTRYPOINT al entrypoint con CMD por defecto `ci`; EXPOSE 8000.
- docker/entrypoint.sh soporta los subcomandos `ci`, `vectorize` y `serve`; `ci` corre
  el pipeline completo en el MISMO orden que ci.yml y falla con exit≠0 si un gate
  falla.
- .dockerignore excluye .git/.cortex/node_modules/models/dist/.venv/__pycache__/caches.
- El Dockerfile y el entrypoint REUSAN los scripts/comandos reales del repo (paridad
  con el CI), sin reimplementar lógica.
- README tiene la sección 'Correr todo en Docker' con los comandos build/run de los
  3 subcomandos; la tabla de mapeo marca 'Entorno del dev con build local = Docker
  ✅'; 'Estado actual' → Pasos 1-7; estructura del repo actualizada. PRESENTACION tiene
  el fragmento del Paso 7.
- 'Si hay Docker disponible: `docker build` termina OK y `docker run <img>` (subcomando
  ci) termina exit 0. Si NO hay Docker en el entorno, la limitación queda documentada
  y la estructura se valida por inspección.'
- 'Nada pesado commiteado: models/, dist/, node_modules/ siguen gitignored.'
---

## Goal

Empaquetar el entorno de build/dev del proyecto en una imagen Docker — la fila 'Entorno del dev con build local' de la consigna de CI/CD. Un Dockerfile (Python 3.13 + Node 22 + las dependencias) que corre el MISMO pipeline que GitHub Actions (download_model, ruff, validate_catalog, vectorize, pytest incl. regresión semántica, check_site, tests JS incl. el gate de equivalencia Python↔JS) dentro de un contenedor, sin instalar nada en la máquina del usuario, garantizando reproducibilidad ('en mi máquina anda' se acaba). Un entrypoint con subcomandos cubre las 3 necesidades: `ci` (pipeline completo = paridad con el CI; default), `vectorize` (genera dist/embeddings.json en un volumen) y `serve` (sirve el sitio estático local en :8000). El entrypoint REUSA los scripts del repo tal cual (no reimplementa lógica). NO incluye el CD/deploy a GitHub Pages ni el hosting del modelo en producción: eso queda EXPLÍCITAMENTE para el cierre del proyecto. Español rioplatense, didáctico, para la defensa oral.

## Requirements

- Dockerfile (NUEVO): base `python:3.13-slim`; instalar Node 22 (NodeSource o equivalente) y limpiar apt lists. WORKDIR /app. Para cachear capas de deps: copiar primero pyproject.toml + README.md + package.json + package-lock.json, correr `pip install -e .[dev]` y `npm ci`, y RECIÉN después copiar el resto del repo. Hornear el modelo en el build con `RUN python scripts/download_model.py` (deja models/ en la imagen → el lado Python anda offline). `ENTRYPOINT ["docker/entrypoint.sh"]` (o bash) y `CMD ["ci"]`. `EXPOSE 8000` para el subcomando serve. Imagen lo más chica razonable.
- docker/entrypoint.sh (NUEVO): script bash con `set -euo pipefail` y un dispatch por subcomando. `ci`: corre el pipeline completo en el MISMO orden que .github/workflows/ci.yml (download_model → ruff → validate_catalog [+ test negativo] → vectorize → pytest tests/ → check_site → node search.test.mjs → node equivalence) y falla con exit≠0 si un gate falla. `vectorize`: corre `python scripts/vectorize.py`. `serve`: `python -m http.server 8000` desde /app (→ http://localhost:8000/site/). Sin args o arg desconocido: corre `ci` (o imprime ayuda). REUSA los scripts/comandos reales, no reimplementa lógica.
- .dockerignore (NUEVO): excluir del build context lo pesado/innecesario — .git, .cortex, node_modules, models, dist, .venv, venv, __pycache__, *.pyc, .ruff_cache, .pytest_cache, .cache, .vscode, .idea. (El build regenera/instala/hornea estos adentro.)
- README.md (EDITAR): nueva sección 'Correr todo en Docker (Paso 7)' con los comandos: build (`docker build -t buscador-semantico .`), pipeline completo (`docker run --rm buscador-semantico`), vectorizar a un volumen (`docker run --rm -v "$PWD/dist:/app/dist" buscador-semantico vectorize`) y servir (`docker run --rm -p 8000:8000 buscador-semantico serve` → http://localhost:8000/site/). Actualizar la tabla de mapeo: 'Entorno del dev con build local = Docker ✅'. 'Estado actual' → Pasos 1-7. Agregar Dockerfile/.dockerignore/docker/ a la estructura. Aclarar que el equivalence test y el browser bajan el modelo del CDN en runtime (red), y que el CD a Pages sigue diferido al cierre.
- PRESENTACION.md (EDITAR/append): fragmento del Paso 7 (~3 párrafos, voseo): qué resuelve Docker (reproducibilidad: el contenedor corre el pipeline IGUAL que el CI, sin depender de lo que cada uno tenga instalado), los 3 subcomandos (ci/vectorize/serve) y la conexión con la consigna ('entorno del dev con build local'). Mencionar que el deploy a producción (CD) se muestra al final.

## Files in Scope

- `Dockerfile`
- `docker/entrypoint.sh`
- `.dockerignore`
- `README.md`
- `PRESENTACION.md`

## Constraints

- Docker = ENTORNO DE BUILD/DEV reproducible (fila 'Entorno del dev con build local' de la consigna). NO es el deploy/CD: NADA de nginx de producción ni publicar a GitHub Pages (diferido EXPLÍCITAMENTE al cierre del proyecto). El subcomando serve es solo para la demo local.
- El contenedor corre los MISMOS comandos/gates que el CI (.github/workflows/ci.yml) y el dev local; el entrypoint REUSA los scripts tal cual (download_model, ruff, validate_catalog, vectorize, pytest, check_site, search.test.mjs, embed.equiv.test.mjs). NO reimplementar lógica de negocio.
- Imagen lo más chica razonable: base slim + `.dockerignore` para no copiar node_modules/models/dist/.git/.cortex al build context + limpiar apt lists. NO commitear nada pesado: models/, dist/, node_modules/ siguen gitignored en el repo (la imagen los genera/hornea/instala adentro).
- El modelo: horneado en el build para el lado Python (offline). El equivalence test (Node/Transformers.js) y el browser bajan el modelo del HF CDN en runtime (necesitan red); documentarlo. No subir el modelo al repo.
- Limitación conocida (igual que el Paso 6 con Actions): validar la imagen requiere Docker instalado. Si Docker NO está disponible en el entorno, entregar el Dockerfile/entrypoint/.dockerignore correctos + documentar que el build/run se valida donde haya Docker. Requiere los Pasos 4-6 commiteados para que el build context tenga todo (hoy gitless).
- Avanzar paso a paso: al terminar el Paso 7, pausar y esperar confirmación del usuario antes del cierre (Paso 8 / CD). Cerrar con /cortex-documenter; si el build de Docker no se pudo validar o queda algo a medias, cerrar como 'handoff'.
- Español rioplatense (voseo) en las docs, didáctico, pensado para la defensa oral de 5 min.

## Acceptance Criteria

- [ ] Existe un Dockerfile válido (base python:3.13-slim + Node 22) que instala las deps (`pip install -e .[dev]` + `npm ci`), hornea el modelo (`download_model.py`) y define ENTRYPOINT al entrypoint con CMD por defecto `ci`; EXPOSE 8000.
- [ ] docker/entrypoint.sh soporta los subcomandos `ci`, `vectorize` y `serve`; `ci` corre el pipeline completo en el MISMO orden que ci.yml y falla con exit≠0 si un gate falla.
- [ ] .dockerignore excluye .git/.cortex/node_modules/models/dist/.venv/__pycache__/caches.
- [ ] El Dockerfile y el entrypoint REUSAN los scripts/comandos reales del repo (paridad con el CI), sin reimplementar lógica.
- [ ] README tiene la sección 'Correr todo en Docker' con los comandos build/run de los 3 subcomandos; la tabla de mapeo marca 'Entorno del dev con build local = Docker ✅'; 'Estado actual' → Pasos 1-7; estructura del repo actualizada. PRESENTACION tiene el fragmento del Paso 7.
- [ ] Si hay Docker disponible: `docker build` termina OK y `docker run <img>` (subcomando ci) termina exit 0. Si NO hay Docker en el entorno, la limitación queda documentada y la estructura se valida por inspección.
- [ ] Nada pesado commiteado: models/, dist/, node_modules/ siguen gitignored.

## Verification Hooks

Commands that objectively prove the work is done. Run by
`cortex finish-session` (Pluggable Middle, Phase 01).

### docker-artifacts
```bash
python -c "import os;assert os.path.exists('Dockerfile') and os.path.exists('.dockerignore');s=open('docker/entrypoint.sh',encoding='utf-8').read();assert all(k in s for k in ['ci','vectorize','serve']);print('Dockerfile + entrypoint(ci/vectorize/serve) + .dockerignore OK')"
```

Success: exit code 0 — existen Dockerfile, docker/entrypoint.sh (con los 3 subcomandos ci/vectorize/serve) y .dockerignore. · Timeout: 60s
### docker-build *(optional)*
```bash
docker build -t buscador-semantico:test .
```

Success: exit code 0 — la imagen buildea (instala deps, hornea el modelo). SOLO corre si Docker está disponible; es optional porque el entorno puede no tener Docker. · Timeout: 1200s
### docker-run-ci *(optional)*
```bash
docker run --rm buscador-semantico:test ci
```

Success: exit code 0 — el pipeline completo (paridad con el CI) pasa dentro del contenedor. SOLO corre si Docker está disponible (optional). Requiere red al HF Hub para el equivalence test. · Timeout: 1200s
