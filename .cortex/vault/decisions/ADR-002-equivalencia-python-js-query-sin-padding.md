---
schema_version: 1
doc_type: adr
title: 'Equivalencia Python-JS: query sin padding'
created_at: '2026-06-02T20:10:46.098474Z'
updated_at: '2026-06-02T20:10:46.098474Z'
tags:
- adr
- ci-cd
- paso-4
- equivalence
- onnx
- int8
- tokenizer
- adr-001
status: accepted
links:
- .cortex/vault/sessions/2026-06-02_paso-4-vectorizacion-de-la-query-en-el-navegador-onnxruntime-web-via-transformersjs-busqueda-por-texto-libre-equivalencia-pythonjs_cierre-paso-4-equivalencia.md
- .cortex/vault/specs/2026-06-02_paso-4-vectorizacion-de-la-query-en-el-navegador-onnxruntime-web-via-transformersjs-busqueda-por-texto-libre-equivalencia-pythonjs.md
vault_scope: local
fingerprint: fc92751eda9593abeb066ebdd0ff2de710edc0184a5a9a926fcd6c5c50273b72
adr_number: 2
supersedes: []
superseded_by: null
alternatives_considered: []
acceptance_criteria_met: false
---

## Context

El catálogo se vectoriza en el CI (vectorize.py, Paso 2) con el tokenizer pad-eando a 128 tokens, así que el modelo corre sobre secuencias de 128. El navegador (Transformers.js / onnxruntime-web) NO pad-ea: corre el modelo sólo sobre los tokens reales de la query. En el modelo int8 (model_quantized.onnx) la cuantización dinámica depende del LARGO de la secuencia, así que padded≠unpadded — aunque el mean-pooling enmascare el padding por attention_mask (en fp32 padded y unpadded dan idéntico; en int8 NO). La equivalencia Python↔JS es el criterio de aceptación central del Paso 4 y la mitigación del riesgo #1 del ADR-001. La primera corrida daba max|diff| ~3e-2 con el ranking divergiendo en 2 de 6 queries. Se midió que `PY-padded vs PY-unpadded` da EXACTAMENTE el mismo diff que `PY-padded vs JS` (p.ej. 2.9605e-2 idéntico para la query 'hola'), probando que el padding era el 100% del diff (no el modelo: el model.onnx local y el que baja Transformers.js son byte-idénticos, md5 confirmado).

## Decision

Vectorizar la query SIN padding en ambos lados de la equivalencia. scripts/emit_reference_vectors.py llama tokenizer.no_padding() para emitir los vectores de referencia Python igual que el browser. NO se toca vectorize.py: el catálogo (dist/embeddings.json) sigue vectorizado con padding-128 (Paso 2 intacto, embeddings.json idéntico). La asimetría query-sin-padding / catálogo-con-padding NO es un bug: es la realidad de producción (la query se vectoriza en vivo en el browser, el catálogo se precomputa en CI batch) y se fija como invariante del sistema. Resultado: max|diff| = 4.47e-8 << 1e-5 (tolerancia objetivo cumplida SIN relajar) y ranking top-k idéntico como gate duro.

## Alternatives Considered

(none)

## Consequences

La equivalencia entra en 1e-5 sin necesidad de relajar la tolerancia. El gate (tests/equivalence/embed.equiv.test.mjs) compara query-unpadded-JS contra query-unpadded-Python de referencia, y verifica además que el ranking top-k contra el catálogo (padded) coincide. Como query y catálogo se comparan por coseno y ambos están L2-normalizados en el mismo espacio del modelo, el ranking es estable pese a la asimetría de padding. Riesgo asumido: si algún día se quiere simetría total (catálogo también sin padding) hay que re-vectorizar todo el catálogo y re-emitir el fixture. El test depende de poder bajar el modelo del HF Hub la primera vez (dependencia de red conocida).

