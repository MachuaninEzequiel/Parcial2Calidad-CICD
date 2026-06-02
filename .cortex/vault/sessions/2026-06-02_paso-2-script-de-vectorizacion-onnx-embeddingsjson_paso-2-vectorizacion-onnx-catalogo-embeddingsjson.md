---
schema_version: 1
doc_type: session
title: 'Paso 2 — Vectorización ONNX: catálogo → embeddings.json'
created_at: '2026-06-02T17:12:57.692274Z'
updated_at: '2026-06-02T17:12:57.692274Z'
tags:
- session
- sdd
- ci-cd
- paso-2
- onnx
- embeddings
- vectorize
- videojuegos
status: auto-draft
links:
- 2026-06-02_paso-2-script-de-vectorizacion-onnx-embeddingsjson
- ADR-001-arquitectura-100-estatica-con-modelo-onnx-dual-runtime-ci-browser
- 2026-06-02_paso-1-schema-spec-y-catalogo-inicial-buscador-semantico-de-videojuegos-con-cicd_paso-1-base-sdd-schema-spec-catalogo-y-validador
vault_scope: local
fingerprint: b825845cabc1e270dc78b8a20d71b4be5a3d6774e363e59d36a7aa9b8b3c63cf
session_id: 2026-06-02_paso-2-script-de-vectorizacion-onnx-embeddingsjson
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

Pipeline de vectorización: download_model.py baja el modelo quantized de Xenova + tokenizer; vectorize.py genera dist/embeddings.json (10 juegos × 384 dims, mean pooling + L2). Refactor DRY a catalog_io.py. Paso 2 de 8.

## Changes Made

(none)

## Files Touched

(none)

## Key Decisions

(none)

## Next Steps

- [ ] Revisar el enganche git ↔ Cortex: la sesión quedó gitless pese al git init + commit; entender por qué para que los próximos pasos tengan diff real en el vault.
- [ ] Commitear los 4 archivos nuevos + los 3 editados (NO los outputs de models/ ni dist/).
- [ ] Paso 3 — Frontend mínimo: site/index.html + site/app.js con búsqueda por substring sobre embeddings.json (sin ONNX). Esperar confirmación del usuario.
- [ ] La equivalencia Python↔JS (mean pooling + L2, tolerancia 1e-5) se valida recién en el Paso 4.

