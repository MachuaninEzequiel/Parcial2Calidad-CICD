---
schema_version: 1
doc_type: session
title: 'Paso 1 — Base SDD: schema, spec, catálogo y validador'
created_at: '2026-06-02T16:36:36.099630Z'
updated_at: '2026-06-02T16:36:36.099630Z'
tags:
- session
- sdd
- paso-1
- ci-cd
- videojuegos
- schema
- catalogo
status: auto-draft
links:
- 2026-06-02_paso-1-schema-spec-y-catalogo-inicial-buscador-semantico-de-videojuegos-con-cicd
vault_scope: local
fingerprint: 9a9fb4e864694778da838e6bd73b20345d60086665287933fee78adec5782f72
session_id: 2026-06-02_paso-1-schema-spec-y-catalogo-inicial-buscador-semantico-de-videojuegos-con-cicd
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

Base Spec-Driven del proyecto: game.schema.yaml (Capa A), search-expectations.yaml (Capa B), 10 juegos de catálogo y validate_catalog.py. Paso 1 de 8; sin ONNX/CI todavía.

## Changes Made

(none)

## Files Touched

(none)

## Key Decisions

(none)

## Next Steps

- [ ] Commitear (o descartar) los 18 archivos declared-only: el repo no es git aún; git init + primer commit deja trazabilidad.
- [ ] Paso 2 — Vectorización ONNX: scripts/download_model.py + scripts/vectorize.py (→ dist/embeddings.json) + tests/test_vectorize.py. Esperar confirmación del usuario.
- [ ] Al escribir el CI (Paso 6), confirmar la equivalencia check-jsonschema ↔ validador local.

