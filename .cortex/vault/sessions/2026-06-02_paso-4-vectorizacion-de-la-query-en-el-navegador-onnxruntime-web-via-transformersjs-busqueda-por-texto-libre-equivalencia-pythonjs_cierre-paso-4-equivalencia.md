---
schema_version: 1
doc_type: session
title: Cierre Paso 4 — equivalencia
created_at: '2026-06-02T20:09:47.248414Z'
updated_at: '2026-06-02T20:09:47.248414Z'
tags:
- session
- ci-cd
- paso-4
- frontend
- onnxruntime-web
- transformers-js
- embeddings
- equivalence
- browser-vectorization
status: auto-draft
links:
- .cortex/vault/specs/2026-06-02_paso-4-vectorizacion-de-la-query-en-el-navegador-onnxruntime-web-via-transformersjs-busqueda-por-texto-libre-equivalencia-pythonjs.md
- .cortex/vault/designs/2026-06-02_paso-4-vectorizacion-de-la-query-en-el-navegador-onnxruntime-web-via-transformersjs-busqueda-por-texto-libre-equivalencia-pythonjs.md
vault_scope: local
fingerprint: 696d3c8f87fd62977e818d614d05cd4254b844272c2b1e4878fcbc37e49f746a
session_id: 2026-06-02_paso-4-vectorizacion-de-la-query-en-el-navegador-onnxruntime-web-via-transformersjs-busqueda-por-texto-libre-equivalencia-pythonjs
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

Vectorizar la query del usuario en el navegador con el mismo modelo del CI (Xenova/all-MiniLM-L6-v2 quantized, vía Transformers.js/onnxruntime-web), habilitar la búsqueda por texto libre reusando topK/cosineSimilarity, y probar la equivalencia Python↔JS (riesgo #1 del ADR-001) con un golden test: diff numérico < tolerancia objetivo 1e-5 + ranking top-k idéntico. search.mjs queda puro; la vectorización vive en vectorizer.mjs.

## Changes Made

(none)

## Files Touched

(none)

## Key Decisions

(none)

## Next Steps

(none)

