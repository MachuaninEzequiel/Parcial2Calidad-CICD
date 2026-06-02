---
schema_version: 1
doc_type: adr
title: Arquitectura 100% estática con modelo ONNX dual-runtime (CI + browser)
created_at: '2026-06-02T16:37:29.831940Z'
updated_at: '2026-06-02T16:37:29.831940Z'
tags:
- adr
- arquitectura
- onnx
- ci-cd
- sdd
- static-site
- genesis
status: accepted
links:
- 2026-06-02_paso-1-schema-spec-y-catalogo-inicial-buscador-semantico-de-videojuegos-con-cicd
vault_scope: local
fingerprint: 505f1fe289b1423a3066df9ae8dadc94e4cf9b1e1294812c1f697201f4daed3b
adr_number: 1
supersedes: []
superseded_by: null
alternatives_considered: []
acceptance_criteria_met: false
---

## Context

El proyecto es la 2da evaluación de Ingeniería y Calidad de Software: hay que demostrar un entorno de CI/CD funcionando, con build local, prueba automatizada y despliegue. Se eligió un proyecto que cumpliera la consigna y, además, tuviera un componente de IA real corriendo DENTRO del pipeline, para justificar de forma visible la utilidad del servidor de CI y habilitar una demo impactante en la defensa oral de 5 minutos.

Alternativas consideradas y rechazadas:
- **Backend Python (FastAPI) + hosting tipo Render**: rechazado por los cold starts del free tier y porque mantener un servidor de IA es menos impactante para el oral que la narrativa 'la IA corre en tu navegador, no hay backend'.
- **Node.js para el script de build/vectorización**: rechazado porque Python tiene mejor stack de ML y encaja mejor para procesar archivos.
- **SonarCloud para inspección de código**: rechazado por agregar complejidad sin ser central; `ruff` cubre la inspección de forma más simple.

## Decision

Sitio **100% estático** servido por GitHub Pages, sin backend. El catálogo (archivos `.md`) se **precomputa en CI** con Python + `onnxruntime`, generando `embeddings.json` con un vector de 384 dims por juego. El **mismo `model.onnx`** (all-MiniLM-L6-v2, ~22 MB) corre **dos veces**: en el runner del CI para vectorizar el catálogo, y en el **navegador** del usuario (vía `onnxruntime-web`) para vectorizar su query. La búsqueda es por **similitud coseno** client-side contra los embeddings precomputados. Misma vectorización → mismo espacio semántico → comparaciones válidas.

Principio rector transversal: **Spec Driven Development**. `schemas/` y `specs/` son la fuente de verdad; el código y los tests se derivan de ellos. El enum de géneros/plataformas vive solo en el schema.

**Consecuencias:**
- (+) Costo de infraestructura cero; el CI produce un artefacto necesario (`embeddings.json`), lo que justifica su existencia más allá de correr tests.
- (+) Demo potente: agregar un juego → push → pipeline → deploy → aparece en búsquedas semánticas.
- (−) El modelo de ~22 MB se descarga al cliente (mitigado: cachea tras la primera carga).
- (−/riesgo) La equivalencia de vectorización Python↔JS es delicada: mean pooling + normalización L2 deben ser idénticos en ambos lados o las comparaciones fallan. Riesgo a controlar en el Paso 4 (con un test de tolerancia 1e-5).

## Alternatives Considered

(none)

## Consequences



