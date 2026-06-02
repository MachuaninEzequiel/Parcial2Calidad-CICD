---
schema_version: 1
doc_type: spec
title: Paso 6 — CI con GitHub Actions
created_at: '2026-06-02T20:52:31.515435Z'
updated_at: '2026-06-02T20:52:31.515435Z'
tags:
- spec
- spec
- sdd
- ci-cd
- paso-6
- github-actions
- ci
- workflow
- pytest
- equivalence
- ruff
- ci-only
status: draft
links: []
vault_scope: local
fingerprint: 3144a9a8d501253564e80d0cdf1dd92e3948e42cff2fa4de2afaef52400c61dd
verification_hooks:
- name: ci-yaml-valid
  command: python -c "import yaml;w=yaml.safe_load(open('.github/workflows/ci.yml',encoding='utf-8'));assert
    'ci' in w['jobs'] and 'deploy' not in w['jobs'];print('ci.yml CI-only OK')"
  required: true
  success_criteria: exit code 0 — ci.yml es YAML válido, define el job 'ci' y NO define
    un job 'deploy' (confirma CI-only, sin CD).
  timeout_seconds: 60
- name: ruff-lint
  command: ruff check .
  required: false
  success_criteria: exit code 0 — código Python limpio (mismo gate que corre el CI).
  timeout_seconds: 180
- name: catalog-valid
  command: python scripts/validate_catalog.py
  required: true
  success_criteria: exit code 0 — el catálogo valida contra el schema (mismo gate
    que corre el CI).
  timeout_seconds: 120
- name: pytest-suite
  command: python -m pytest tests/ -q
  required: true
  success_criteria: exit code 0 — regresión semántica (Paso 5) + units (Paso 2) verdes;
    mismo gate que corre el CI. Requiere models/ + dist/embeddings.json.
  timeout_seconds: 300
- name: site-structure
  command: python scripts/check_site.py
  required: true
  success_criteria: exit code 0 — el sitio sigue coherente; mismo gate que corre el
    CI.
  timeout_seconds: 120
- name: js-pure-functions
  command: node --test site/js/search.test.mjs
  required: true
  success_criteria: exit code 0 — search.mjs puro; mismo gate que corre el CI.
  timeout_seconds: 180
- name: js-equivalence
  command: node --test tests/equivalence/embed.equiv.test.mjs
  required: true
  success_criteria: exit code 0 — equivalencia Python↔JS (<1e-5) + ranking idéntico;
    el gate central que el CI ahora corre en cada push. Requiere npm install + modelo
    accesible.
  timeout_seconds: 600
goal: 'Cablear Integración Continua con GitHub Actions: un workflow .github/workflows/ci.yml
  que, en cada push y pull_request, corra en el servidor los MISMOS gates que ya corremos
  localmente — ruff, validación del catálogo contra el schema, vectorización ONNX
  (baja el modelo + genera dist/embeddings.json), pytest (regresión semántica del
  Paso 5 + units del Paso 2), check_site, y los tests JS (search.mjs puro + el gate
  de equivalencia Python↔JS del Paso 4, riesgo #1 del ADR-001). El principio que demuestra:
  lo que valida tu máquina es exactamente lo que valida el CI. SOLO CI: el CD (deploy
  a GitHub Pages) y el hosting del modelo en producción quedan EXPLÍCITAMENTE diferidos
  al final del proyecto (decisión del usuario), y Docker es el Paso 7. Reusa los scripts/comandos
  tal cual (no reimplementa lógica en el YAML). Docs: badge de CI + ''Estado 1-6''.
  Español rioplatense, didáctico, para la defensa oral.'
files_in_scope:
- .github/workflows/ci.yml
- README.md
- PRESENTACION.md
constraints:
- 'SOLO CI en el Paso 6: NADA de deploy / GitHub Pages / CD (decisión explícita del
  usuario; se difiere al final del proyecto). NO crear build_site.py, NO tocar site/js/app.mjs,
  NO resolver el hosting del modelo en prod.'
- El workflow corre los MISMOS gates que ya existen localmente, reusando los scripts/comandos
  TAL CUAL (ruff, validate_catalog.py, vectorize.py, pytest tests/, check_site.py,
  search.test.mjs, embed.equiv.test.mjs). NO reimplementar lógica de negocio dentro
  del YAML.
- 'Orden de dependencias correcto: download_model ANTES de vectorize/pytest/equivalence;
  vectorize (genera dist/embeddings.json) ANTES de pytest/check_site/equivalence (lo
  necesitan). La fixture de equivalencia (tests/fixtures/query-vectors.reference.json)
  es la golden reference COMMITEADA y NO se re-emite en CI.'
- 'NO commitear nada pesado: models/, dist/, node_modules/ siguen gitignored; el CI
  los regenera en el runner. Cache de pip/npm/HF para acelerar; actions pineadas.'
- 'El gate de equivalencia Python↔JS se MANTIENE en CI (mitigación del riesgo #1 del
  ADR-001) pese a que baja ~23MB del HF Hub; se mitiga con cache del Hub.'
- 'Limitación conocida: un workflow de GitHub Actions NO se puede ''correr'' localmente;
  su validación efectiva ocurre al pushear al repo en GitHub (hoy gitless / sin remoto).
  El Paso 6 entrega el YAML correcto y bien formado + prueba que el pipeline que codifica
  pasa localmente. Requiere que los Pasos 4-5 estén commiteados para tener sentido
  en GitHub.'
- 'Avanzar paso a paso: al terminar el Paso 6, pausar y esperar confirmación del usuario
  antes del Paso 7 (Docker). Cerrar con /cortex-documenter.'
- Español rioplatense (voseo) en las docs, didáctico, pensado para la defensa oral
  de 5 min.
acceptance_criteria:
- 'Existe .github/workflows/ci.yml, es YAML válido y bien formado, dispara `on: push`
  y `on: pull_request`, y define UN job `ci` en ubuntu-latest. NO contiene job de
  deploy ni referencias a GitHub Pages.'
- 'El job corre, en orden de dependencias correcto: install (pip install -e .[dev]
  + npm ci) → download_model.py → ruff → validate_catalog.py → vectorize.py → pytest
  tests/ → check_site.py → node search.test.mjs → node equivalence test.'
- Cachea pip, npm y ~/.cache/huggingface; las actions están pineadas a major version.
- 'El pipeline que codifica el YAML pasa LOCALMENTE: ruff, validate_catalog, vectorize,
  pytest tests/, check_site, search.test.mjs y el equivalence test terminan todos
  exit 0 en este entorno.'
- README refleja Pasos 1-6 con badge de CI (placeholder owner/repo) y ACLARA que el
  CD/Pages + hosting del modelo en prod se hacen al final; la tabla de mapeo marca
  'GitHub Actions' como implementado. PRESENTACION tiene el fragmento del Paso 6.
- Los comandos del YAML coinciden 1:1 con los scripts/paths reales del repo (mismos
  que los hooks de Pasos 1-5). Nada pesado commiteado (models/, dist/, node_modules/
  gitignored).
---

## Goal

Cablear Integración Continua con GitHub Actions: un workflow .github/workflows/ci.yml que, en cada push y pull_request, corra en el servidor los MISMOS gates que ya corremos localmente — ruff, validación del catálogo contra el schema, vectorización ONNX (baja el modelo + genera dist/embeddings.json), pytest (regresión semántica del Paso 5 + units del Paso 2), check_site, y los tests JS (search.mjs puro + el gate de equivalencia Python↔JS del Paso 4, riesgo #1 del ADR-001). El principio que demuestra: lo que valida tu máquina es exactamente lo que valida el CI. SOLO CI: el CD (deploy a GitHub Pages) y el hosting del modelo en producción quedan EXPLÍCITAMENTE diferidos al final del proyecto (decisión del usuario), y Docker es el Paso 7. Reusa los scripts/comandos tal cual (no reimplementa lógica en el YAML). Docs: badge de CI + 'Estado 1-6'. Español rioplatense, didáctico, para la defensa oral.

## Requirements

- .github/workflows/ci.yml (NUEVO): workflow 'CI' con `on: [push, pull_request]`. UN job `ci` en `ubuntu-latest`. Pasos en ORDEN de dependencias: (1) actions/checkout@v4; (2) actions/setup-python@v5 (3.11+) con cache de pip; (3) actions/setup-node@v4 (Node 22) con cache de npm; (4) `pip install -e .[dev]`; (5) `npm ci`; (6) actions/cache@v4 de `~/.cache/huggingface` (para no re-bajar el modelo cada run); (7) `python scripts/download_model.py`; (8) `ruff check .`; (9) `python scripts/validate_catalog.py` (opcional: también el test negativo `--expect-fail tests/fixtures/invalid-game.md`); (10) `python scripts/vectorize.py` (genera dist/embeddings.json); (11) `python -m pytest tests/ -q`; (12) `python scripts/check_site.py`; (13) `node --test site/js/search.test.mjs`; (14) `node --test tests/equivalence/embed.equiv.test.mjs`. Actions pineadas a major version. Opcional: `concurrency` para cancelar runs viejos del mismo ref. NO usar `continue-on-error` en pasos required. NINGÚN job de deploy, NINGÚN uso de GitHub Pages.
- README.md (EDITAR): agregar badge del workflow de CI (placeholder con el path owner/repo de GitHub, a completar cuando se conozca); actualizar la tabla de mapeo a la consigna ('Servidor de Integración Continua = GitHub Actions' → implementado) y el 'Estado actual' a Pasos 1-6; listar qué corre el CI; ACLARAR explícitamente que el CD (deploy a GitHub Pages) y el hosting del modelo en producción se resuelven al FINAL del proyecto, no en el Paso 6, y que Docker es el Paso 7.
- PRESENTACION.md (EDITAR/append): fragmento del Paso 6 (~3 párrafos): qué es CI y cómo GitHub Actions corre los MISMOS gates que el dev local (lo que valida tu máquina = lo que valida el servidor); el orden del pipeline (schema → lint → tests → vectorización → equivalencia) y que el gate de equivalencia (riesgo #1) ahora corre en cada push; mencionar que el deploy continuo (CD) a GitHub Pages se muestra al final. Voseo rioplatense.

## Files in Scope

- `.github/workflows/ci.yml`
- `README.md`
- `PRESENTACION.md`

## Constraints

- SOLO CI en el Paso 6: NADA de deploy / GitHub Pages / CD (decisión explícita del usuario; se difiere al final del proyecto). NO crear build_site.py, NO tocar site/js/app.mjs, NO resolver el hosting del modelo en prod.
- El workflow corre los MISMOS gates que ya existen localmente, reusando los scripts/comandos TAL CUAL (ruff, validate_catalog.py, vectorize.py, pytest tests/, check_site.py, search.test.mjs, embed.equiv.test.mjs). NO reimplementar lógica de negocio dentro del YAML.
- Orden de dependencias correcto: download_model ANTES de vectorize/pytest/equivalence; vectorize (genera dist/embeddings.json) ANTES de pytest/check_site/equivalence (lo necesitan). La fixture de equivalencia (tests/fixtures/query-vectors.reference.json) es la golden reference COMMITEADA y NO se re-emite en CI.
- NO commitear nada pesado: models/, dist/, node_modules/ siguen gitignored; el CI los regenera en el runner. Cache de pip/npm/HF para acelerar; actions pineadas.
- El gate de equivalencia Python↔JS se MANTIENE en CI (mitigación del riesgo #1 del ADR-001) pese a que baja ~23MB del HF Hub; se mitiga con cache del Hub.
- Limitación conocida: un workflow de GitHub Actions NO se puede 'correr' localmente; su validación efectiva ocurre al pushear al repo en GitHub (hoy gitless / sin remoto). El Paso 6 entrega el YAML correcto y bien formado + prueba que el pipeline que codifica pasa localmente. Requiere que los Pasos 4-5 estén commiteados para tener sentido en GitHub.
- Avanzar paso a paso: al terminar el Paso 6, pausar y esperar confirmación del usuario antes del Paso 7 (Docker). Cerrar con /cortex-documenter.
- Español rioplatense (voseo) en las docs, didáctico, pensado para la defensa oral de 5 min.

## Acceptance Criteria

- [ ] Existe .github/workflows/ci.yml, es YAML válido y bien formado, dispara `on: push` y `on: pull_request`, y define UN job `ci` en ubuntu-latest. NO contiene job de deploy ni referencias a GitHub Pages.
- [ ] El job corre, en orden de dependencias correcto: install (pip install -e .[dev] + npm ci) → download_model.py → ruff → validate_catalog.py → vectorize.py → pytest tests/ → check_site.py → node search.test.mjs → node equivalence test.
- [ ] Cachea pip, npm y ~/.cache/huggingface; las actions están pineadas a major version.
- [ ] El pipeline que codifica el YAML pasa LOCALMENTE: ruff, validate_catalog, vectorize, pytest tests/, check_site, search.test.mjs y el equivalence test terminan todos exit 0 en este entorno.
- [ ] README refleja Pasos 1-6 con badge de CI (placeholder owner/repo) y ACLARA que el CD/Pages + hosting del modelo en prod se hacen al final; la tabla de mapeo marca 'GitHub Actions' como implementado. PRESENTACION tiene el fragmento del Paso 6.
- [ ] Los comandos del YAML coinciden 1:1 con los scripts/paths reales del repo (mismos que los hooks de Pasos 1-5). Nada pesado commiteado (models/, dist/, node_modules/ gitignored).

## Verification Hooks

Commands that objectively prove the work is done. Run by
`cortex finish-session` (Pluggable Middle, Phase 01).

### ci-yaml-valid
```bash
python -c "import yaml;w=yaml.safe_load(open('.github/workflows/ci.yml',encoding='utf-8'));assert 'ci' in w['jobs'] and 'deploy' not in w['jobs'];print('ci.yml CI-only OK')"
```

Success: exit code 0 — ci.yml es YAML válido, define el job 'ci' y NO define un job 'deploy' (confirma CI-only, sin CD). · Timeout: 60s
### ruff-lint *(optional)*
```bash
ruff check .
```

Success: exit code 0 — código Python limpio (mismo gate que corre el CI). · Timeout: 180s
### catalog-valid
```bash
python scripts/validate_catalog.py
```

Success: exit code 0 — el catálogo valida contra el schema (mismo gate que corre el CI). · Timeout: 120s
### pytest-suite
```bash
python -m pytest tests/ -q
```

Success: exit code 0 — regresión semántica (Paso 5) + units (Paso 2) verdes; mismo gate que corre el CI. Requiere models/ + dist/embeddings.json. · Timeout: 300s
### site-structure
```bash
python scripts/check_site.py
```

Success: exit code 0 — el sitio sigue coherente; mismo gate que corre el CI. · Timeout: 120s
### js-pure-functions
```bash
node --test site/js/search.test.mjs
```

Success: exit code 0 — search.mjs puro; mismo gate que corre el CI. · Timeout: 180s
### js-equivalence
```bash
node --test tests/equivalence/embed.equiv.test.mjs
```

Success: exit code 0 — equivalencia Python↔JS (<1e-5) + ranking idéntico; el gate central que el CI ahora corre en cada push. Requiere npm install + modelo accesible. · Timeout: 600s
