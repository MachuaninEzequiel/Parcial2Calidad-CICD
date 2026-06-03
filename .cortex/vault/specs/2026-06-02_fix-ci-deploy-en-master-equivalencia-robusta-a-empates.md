---
schema_version: 1
doc_type: spec
title: 'Fix CI: deploy en master + equivalencia robusta a empates'
created_at: '2026-06-02T23:34:20.103647Z'
updated_at: '2026-06-02T23:34:20.103647Z'
tags:
- spec
- spec
- sdd
- ci-cd
- fix
- bugfix
- deploy
- github-actions
- equivalence
- float-tie
- byo
status: draft
links: []
vault_scope: local
fingerprint: 906a7383cdbe6b7736b55a53880b378d318899edfb5f8b84c1e3e95f90970053
verification_hooks:
- name: deploy-on-master
  command: python -c "import yaml;d=yaml.safe_load(open('.github/workflows/ci.yml',encoding='utf-8'))['jobs']['deploy'];assert
    'master' in d['if'] and 'main' not in d['if'];print('deploy gateado en master
    OK')"
  required: true
  success_criteria: exit code 0 — el job deploy se dispara en master, no en main.
  timeout_seconds: 60
- name: equivalence-set-robust
  command: node --test tests/equivalence/embed.equiv.test.mjs
  required: true
  success_criteria: exit code 0 — la equivalencia pasa comparando el top-k como conjunto
    + max|diff| < tolerance. Requiere npm install + modelo accesible.
  timeout_seconds: 600
- name: pytest-suite
  command: python -m pytest tests/ -q
  required: true
  success_criteria: exit code 0 — units (Paso 2) + regresión semántica (Paso 5) siguen
    verdes; el fix no rompió nada.
  timeout_seconds: 300
goal: 'Registrar (spec retroactiva; el trabajo YA está implementado y commiteado por
  el usuario) un bugfix de CI/CD con dos arreglos surgidos al correr el pipeline real
  en GitHub Actions. (1) BRANCH: el job `deploy` (CD a Pages, agregado en la spec
  ''CD a GitHub Pages'') estaba gateado con `if: github.ref == ''refs/heads/main''`,
  pero la rama por defecto del repo es `master`, así que el deploy nunca se disparaba
  (quedaba ''skipped''). Se cambió el gate a `master` y se alinearon las menciones
  de rama en README/PRESENTACION. (2) EQUIVALENCIA FRÁGIL: el gate de equivalencia
  Python↔JS (tests/equivalence/embed.equiv.test.mjs) fallaba en el runner de CI —pero
  pasaba en local— por un empate de punto flotante (~1e-8) entre witcher-3 y hades
  para la query ''indie corto y emotivo con historia'': los MISMOS 5 juegos salían,
  pero el desempate de orden caía distinto entre la CPU/build de onnxruntime del runner
  y la local. El test comparaba el ranking top-k con orden EXACTO (deepEqual). Se
  cambió a comparar el top-k como CONJUNTO (sorted), manteniendo el chequeo numérico
  max|diff| < tolerancia (4.47e-8 << 1e-5) como gate duro. El orden exacto de dos
  juegos con score casi igual es ruido de float, no una diferencia semántica; la calidad
  semántica la cubre aparte el test de regresión del Paso 5.'
files_in_scope:
- .github/workflows/ci.yml
- tests/equivalence/embed.equiv.test.mjs
- README.md
- PRESENTACION.md
constraints:
- 'Bugfix retroactivo: el trabajo ya está implementado, verificado localmente (equivalencia
  7/7, pytest 10/10) y commiteado por el usuario. Esta spec lo REGISTRA en el vault;
  no hay implementación pendiente (flujo BYO → cerrar con /cortex-documenter).'
- El chequeo NUMÉRICO de equivalencia (max|diff| < tolerancia 1e-5) sigue siendo gate
  DURO. Solo se relaja la comparación de ORDEN del top-k (ahora conjunto), porque
  el orden de dos scores que difieren en ~1e-8 es ruido de punto flotante, no semántica.
- La calidad semántica (que aparezca el juego correcto por query) la sigue garantizando
  aparte el test de regresión del Paso 5 (must_include_any_of). Este fix NO la toca.
- 'No se cambió la lógica del catálogo, el modelo, ni los vectores: solo el gate del
  deploy (rama) y la forma de comparar el ranking en el test de equivalencia.'
acceptance_criteria:
- 'El job `deploy` de ci.yml se dispara en push a `master` (`if: github.ref == ''refs/heads/master''`),
  no en `main`.'
- tests/equivalence/embed.equiv.test.mjs compara el top-k como conjunto (sorted) y
  mantiene el assert numérico max|diff| < tolerance. `node --test tests/equivalence/embed.equiv.test.mjs`
  termina exit 0 de forma robusta (sin depender del desempate de float entre CPUs).
- README y PRESENTACION mencionan `master` (no `main`) para la rama de deploy.
- 'Los demás gates siguen verdes: `python -m pytest tests/` exit 0; el CI completo
  (incluido el equivalence) pasa en GitHub Actions y el job deploy ahora sí corre
  en master.'
- No se modificó el catálogo, el modelo, ni la lógica de vectorización/ranking del
  producto.
---

## Goal

Registrar (spec retroactiva; el trabajo YA está implementado y commiteado por el usuario) un bugfix de CI/CD con dos arreglos surgidos al correr el pipeline real en GitHub Actions. (1) BRANCH: el job `deploy` (CD a Pages, agregado en la spec 'CD a GitHub Pages') estaba gateado con `if: github.ref == 'refs/heads/main'`, pero la rama por defecto del repo es `master`, así que el deploy nunca se disparaba (quedaba 'skipped'). Se cambió el gate a `master` y se alinearon las menciones de rama en README/PRESENTACION. (2) EQUIVALENCIA FRÁGIL: el gate de equivalencia Python↔JS (tests/equivalence/embed.equiv.test.mjs) fallaba en el runner de CI —pero pasaba en local— por un empate de punto flotante (~1e-8) entre witcher-3 y hades para la query 'indie corto y emotivo con historia': los MISMOS 5 juegos salían, pero el desempate de orden caía distinto entre la CPU/build de onnxruntime del runner y la local. El test comparaba el ranking top-k con orden EXACTO (deepEqual). Se cambió a comparar el top-k como CONJUNTO (sorted), manteniendo el chequeo numérico max|diff| < tolerancia (4.47e-8 << 1e-5) como gate duro. El orden exacto de dos juegos con score casi igual es ruido de float, no una diferencia semántica; la calidad semántica la cubre aparte el test de regresión del Paso 5.

## Requirements

- .github/workflows/ci.yml (HECHO): cambiar el `if` del job `deploy` de `refs/heads/main` a `refs/heads/master` (+ comentarios del workflow alineados). El job `ci` y el resto del `deploy` sin cambios.
- tests/equivalence/embed.equiv.test.mjs (HECHO): en el chequeo (b), reemplazar `assert.deepEqual(jsIds, query.top_k_ids)` por `assert.deepEqual([...jsIds].sort(), [...query.top_k_ids].sort())` con un comentario que explique el desempate de float. El chequeo (a) numérico (max|diff| < tolerance) queda intacto como gate duro.
- README.md (HECHO): alinear las menciones de rama de `main` a `master` (tabla de mapeo, bullet de CD, sección CI, estado).
- PRESENTACION.md (HECHO): alinear `if: main` / 'push a main' a `master` en el fragmento de cierre (CD).

## Files in Scope

- `.github/workflows/ci.yml`
- `tests/equivalence/embed.equiv.test.mjs`
- `README.md`
- `PRESENTACION.md`

## Constraints

- Bugfix retroactivo: el trabajo ya está implementado, verificado localmente (equivalencia 7/7, pytest 10/10) y commiteado por el usuario. Esta spec lo REGISTRA en el vault; no hay implementación pendiente (flujo BYO → cerrar con /cortex-documenter).
- El chequeo NUMÉRICO de equivalencia (max|diff| < tolerancia 1e-5) sigue siendo gate DURO. Solo se relaja la comparación de ORDEN del top-k (ahora conjunto), porque el orden de dos scores que difieren en ~1e-8 es ruido de punto flotante, no semántica.
- La calidad semántica (que aparezca el juego correcto por query) la sigue garantizando aparte el test de regresión del Paso 5 (must_include_any_of). Este fix NO la toca.
- No se cambió la lógica del catálogo, el modelo, ni los vectores: solo el gate del deploy (rama) y la forma de comparar el ranking en el test de equivalencia.

## Acceptance Criteria

- [ ] El job `deploy` de ci.yml se dispara en push a `master` (`if: github.ref == 'refs/heads/master'`), no en `main`.
- [ ] tests/equivalence/embed.equiv.test.mjs compara el top-k como conjunto (sorted) y mantiene el assert numérico max|diff| < tolerance. `node --test tests/equivalence/embed.equiv.test.mjs` termina exit 0 de forma robusta (sin depender del desempate de float entre CPUs).
- [ ] README y PRESENTACION mencionan `master` (no `main`) para la rama de deploy.
- [ ] Los demás gates siguen verdes: `python -m pytest tests/` exit 0; el CI completo (incluido el equivalence) pasa en GitHub Actions y el job deploy ahora sí corre en master.
- [ ] No se modificó el catálogo, el modelo, ni la lógica de vectorización/ranking del producto.

## Verification Hooks

Commands that objectively prove the work is done. Run by
`cortex finish-session` (Pluggable Middle, Phase 01).

### deploy-on-master
```bash
python -c "import yaml;d=yaml.safe_load(open('.github/workflows/ci.yml',encoding='utf-8'))['jobs']['deploy'];assert 'master' in d['if'] and 'main' not in d['if'];print('deploy gateado en master OK')"
```

Success: exit code 0 — el job deploy se dispara en master, no en main. · Timeout: 60s
### equivalence-set-robust
```bash
node --test tests/equivalence/embed.equiv.test.mjs
```

Success: exit code 0 — la equivalencia pasa comparando el top-k como conjunto + max|diff| < tolerance. Requiere npm install + modelo accesible. · Timeout: 600s
### pytest-suite
```bash
python -m pytest tests/ -q
```

Success: exit code 0 — units (Paso 2) + regresión semántica (Paso 5) siguen verdes; el fix no rompió nada. · Timeout: 300s
