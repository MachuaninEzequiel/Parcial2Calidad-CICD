---
schema_version: 1
doc_type: decision
title: 'Equivalencia Python-JS: comparar el top-k como conjunto (empates de float)'
created_at: '2026-06-02T23:49:58.293879Z'
updated_at: '2026-06-02T23:49:58.293879Z'
tags:
- decision
- ci-cd
- equivalence
- float-tie
- testing
- onnx
status: active
links:
- .cortex/vault/specs/2026-06-02_fix-ci-deploy-en-master-equivalencia-robusta-a-empates.md
- .cortex/vault/decisions/ADR-002-equivalencia-python-js-query-sin-padding.md
- .cortex/vault/sessions/2026-06-02_fix-ci-deploy-en-master-equivalencia-robusta-a-empates_cierre-fix-ci-deploy-master-equivalencia.md
vault_scope: local
fingerprint: ca0ae3045b8f5b3b1b74ab85e382d280ed1b71f82c5b322ab95229f7b84ed9fe
reversible_within_days: 0
---

## Context

El gate de equivalencia Python↔JS (tests/equivalence/embed.equiv.test.mjs, Paso 4) verifica dos cosas por query: (a) max|diff| del vector JS vs la referencia Python < tolerancia, y (b) que el ranking top-k coincida. (b) estaba implementado como orden EXACTO (assert.deepEqual del array ordenado). En el runner de GitHub Actions, la query 'indie corto y emotivo con historia' falló: witcher-3 y hades (puestos 4 y 5) salían SWAPEADOS respecto de la referencia. Causa: sus scores de coseno difieren en ~1e-8 (empate numérico), y el desempate del orden cae distinto entre la CPU/build de onnxruntime del runner y la de la máquina local (donde el test pasaba 7/7). Los vectores son idénticos: max|diff| = 4.47e-8 << 1e-5. O sea: mismos resultados, distinto orden de dos casi-empatados — ruido de punto flotante, no semántica.

## Decision

En el chequeo (b) del gate de equivalencia, comparar el top-k como CONJUNTO (ambos lados ordenados con .sort() antes del deepEqual), NO por orden exacto. El chequeo (a) numérico (max|diff| < tolerancia) se mantiene como gate DURO. Así la equivalencia prueba 'mismos vectores (a 1e-8) + mismos juegos en el top-k', sin asertar el orden de near-ties, que es no determinista entre runtimes/CPUs.

## Alternative Rejected



## Reason



