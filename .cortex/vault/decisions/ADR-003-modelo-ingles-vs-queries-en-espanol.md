---
schema_version: 1
doc_type: adr
title: Modelo ingles vs queries en espanol
created_at: '2026-06-02T20:11:15.579640Z'
updated_at: '2026-06-02T20:11:15.579640Z'
tags:
- adr
- ci-cd
- paso-4
- paso-5
- embeddings
- semantica
- modelo
- adr-001
status: accepted
links:
- .cortex/vault/sessions/2026-06-02_paso-4-vectorizacion-de-la-query-en-el-navegador-onnxruntime-web-via-transformersjs-busqueda-por-texto-libre-equivalencia-pythonjs_cierre-paso-4-equivalencia.md
- .cortex/vault/specs/2026-06-02_paso-4-vectorizacion-de-la-query-en-el-navegador-onnxruntime-web-via-transformersjs-busqueda-por-texto-libre-equivalencia-pythonjs.md
vault_scope: local
fingerprint: e048100570c624e8cd856efb4986e2e32b5784a45badaec42b89501c411363da
adr_number: 3
supersedes: []
superseded_by: null
alternatives_considered: []
acceptance_criteria_met: false
---

## Context

all-MiniLM-L6-v2 (el modelo fijado por el ADR-001: int8 quantized, ~23MB, mismo artefacto en CI y browser) es principalmente un modelo de INGLÉS. Al habilitar la búsqueda por texto libre real en el Paso 4 se descubrió que rinde flojo con queries CORTAS en ESPAÑOL: casi toda query devuelve el mismo cluster (gris / journey / disco-elysium / celeste / hades), y la demo estrella del proyecto — 'juego para jugar con amigos en el sillón' → Overcooked 2 — NO funciona en español (Overcooked 2 ni aparece en el top-5), aunque la MISMA query en inglés ('couch co-op party game with friends') sí devuelve Overcooked 2 en el puesto #1. El gate de equivalencia del Paso 4 no detecta esto: sólo prueba que Python y JS COINCIDEN, no que el resultado sea semánticamente bueno (la calidad semántica es gate del Paso 5). README línea 5 y el fragmento Paso 4 de PRESENTACION prometen esa demo.

## Decision

Mantener el modelo chico (all-MiniLM-L6-v2) y compensar afinando el CONTENIDO del catálogo en español, en vez de cambiar a un modelo multilingüe. Un experimento del orquestador lo confirmó: reescribir el summary de catalog/overcooked-2.md liderando con el marco 'jugar con amigos en el sillón / cooperativo / multijugador local' (en español natural, sin keyword-stuffing) sube a Overcooked 2 al puesto #1 con score 0.728 (el summary original mencionaba la frase una sola vez, diluida en texto largo sobre cocinas caóticas). La implementación — reescribir summaries del catálogo + re-vectorizar + re-emitir el fixture de referencia + alinear README/PRESENTACION — se DIFIERE al Paso 5 (editar catalog/*.md es Capa C, fuera del scope del Paso 4).

## Alternatives Considered

(none)

## Consequences

El proyecto sigue simple y liviano: sin modelo multilingüe pesado, sin tocar download_model.py ni el presupuesto de descarga del browser, sin cambiar el ADR-001. Sólo se garantiza que 'ese caso' (la demo) ande; otras queries en español pueden seguir flojas, lo cual es aceptable para el alcance académico (el usuario lo aceptó explícitamente: 'es irrelevante si funciona o no para todos los casos'). Trade-off asumido: la calidad de búsqueda queda ACOPLADA al contenido del catálogo (un summary mal escrito degrada el ranking). Hasta que el Paso 5 afine el catálogo, README/PRESENTACION quedan con un over-claim respecto a la demo.

