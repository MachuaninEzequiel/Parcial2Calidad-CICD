---
schema_version: 1
doc_type: session
title: Cierre fix CI — deploy master + equivalencia
created_at: '2026-06-02T23:49:28.915183Z'
updated_at: '2026-06-02T23:49:28.915183Z'
tags:
- session
- ci-cd
- fix
- bugfix
- deploy
- github-actions
- equivalence
- float-tie
- byo
status: auto-draft
links:
- .cortex/vault/specs/2026-06-02_fix-ci-deploy-en-master-equivalencia-robusta-a-empates.md
- .cortex/vault/decisions/ADR-002-equivalencia-python-js-query-sin-padding.md
- .cortex/vault/sessions/2026-06-02_cd-a-github-pages-cierre-cicd_cierre-cicd-cd-a-github-pages.md
vault_scope: local
fingerprint: 7e41eadc04acbac7c188612490fb275abc8e18a9fa2a9038ba1700f12beda9b6
session_id: 2026-06-02_fix-ci-deploy-en-master-equivalencia-robusta-a-empates
pr: null
branch: null
commit: null
cortex_telemetry: null
---

## Original Specification

Bugfix retroactivo (BYO) de dos problemas que destapó el CI real en GitHub Actions: (1) el job deploy estaba gateado en refs/heads/main pero la rama es master → nunca deplegó; (2) el gate de equivalencia Python↔JS fallaba en el runner por un empate de float (~1e-8) que flipeaba el orden de dos juegos → se cambió a comparar el top-k como conjunto, manteniendo max|diff|<tolerancia como gate duro.

## Changes Made

(none)

## Files Touched

(none)

## Key Decisions

(none)

## Next Steps

(none)

