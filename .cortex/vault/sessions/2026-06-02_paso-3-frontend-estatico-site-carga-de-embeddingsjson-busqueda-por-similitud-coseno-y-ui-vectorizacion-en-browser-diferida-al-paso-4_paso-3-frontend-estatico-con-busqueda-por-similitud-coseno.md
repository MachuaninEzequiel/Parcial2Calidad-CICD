---
schema_version: 1
doc_type: session
title: Paso 3 — Frontend estático con búsqueda por similitud coseno
created_at: '2026-06-02T18:07:08.287405Z'
updated_at: '2026-06-02T18:07:08.287405Z'
tags:
- session
- sdd
- ci-cd
- paso-3
- frontend
- static-site
- cosine-similarity
- vanilla-js
- gitless
- videojuegos
status: auto-draft
links:
- 2026-06-02_paso-3-frontend-estatico-site-carga-de-embeddingsjson-busqueda-por-similitud-coseno-y-ui-vectorizacion-en-browser-diferida-al-paso-4
- ADR-001-arquitectura-100-estatica-con-modelo-onnx-dual-runtime-ci-browser
- 2026-06-02_paso-2-script-de-vectorizacion-onnx-embeddingsjson
- busqueda-por-similares-item-to-item
- vocabulario-semantico-del-catalogo
vault_scope: local
fingerprint: e64f84c5d589410695f46e91bc1d65a7be17dbf93529e6b9e9a56e7ed04c9c21
session_id: 2026-06-02_paso-3-frontend-estatico-site-carga-de-embeddingsjson-busqueda-por-similitud-coseno-y-ui-vectorizacion-en-browser-diferida-al-paso-4
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

Sitio 100% estático (site/, HTML+CSS+JS vanilla, cero npm) que carga dist/embeddings.json, lista los 10 juegos y busca por similitud coseno client-side. Feature demoable: 'buscar juegos similares' (item-to-item). vectorizeQuery() es un seam que lanza Error 'Paso 4'; el texto libre y onnxruntime-web en browser se difieren al Paso 4.

## Changes Made

(none)

## Files Touched

(none)

## Key Decisions

(none)

## Next Steps

(none)

