---
schema_version: 1
doc_type: session
title: Cierre Paso 6 — CI con GitHub Actions
created_at: '2026-06-02T21:09:51.848988Z'
updated_at: '2026-06-02T21:09:51.848988Z'
tags:
- session
- ci-cd
- paso-6
- github-actions
- ci
- workflow
- pytest
- equivalence
- ci-only
status: auto-draft
links:
- .cortex/vault/specs/2026-06-02_paso-6-ci-con-github-actions.md
- .cortex/vault/decisions/ADR-002-equivalencia-python-js-query-sin-padding.md
- .cortex/vault/decisions/ADR-003-modelo-ingles-vs-queries-en-espanol.md
- .cortex/vault/sessions/2026-06-02_paso-5-tests-de-regresion-semantica-afinado-del-catalogo_cierre-paso-5-regresion-semantica.md
vault_scope: local
fingerprint: e57ba3ddb448277d68407b8a0c5e1df5509f2919516709a2890fc014fe8cc1c1
session_id: 2026-06-02_paso-6-ci-con-github-actions
pr: null
branch: null
commit: null
cortex_telemetry: null
---

## ⚠ Gitless Session

This session was opened in a workspace without a usable git repository.
The documenter was unable to compute a git diff at close time, so the
"Changes Made" and "Files Touched" sections below are reconstructed
**exclusively from agent checkpoints**. A checkpoint can claim a touch
the agent did not actually perform — there's no objective ground truth
to cross-check.

To restore full documenter fidelity in future sessions, run:

```
git init && git add -A && git commit -m "initial"
```

## Original Specification

Cablear Integración Continua con GitHub Actions: un workflow .github/workflows/ci.yml que en cada push y PR corre los MISMOS gates del proyecto (ruff, validate_catalog, vectorize, pytest incl. regresión semántica, check_site, search.test.mjs y el gate de equivalencia Python↔JS). SOLO CI: el CD a GitHub Pages y el hosting del modelo en prod se difieren al final del proyecto. Docker es el Paso 7.

## Changes Made

(none)

## Files Touched

(none)

## Key Decisions

(none)

## Next Steps

(none)

