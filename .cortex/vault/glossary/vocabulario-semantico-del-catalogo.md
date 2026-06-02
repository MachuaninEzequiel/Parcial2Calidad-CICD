---
schema_version: 1
doc_type: glossary
title: Glosario del dominio — Buscador Semántico de Videojuegos
created_at: '2026-06-02T16:37:38.245016Z'
updated_at: '2026-06-02T16:37:38.245016Z'
tags:
- glossary
- domain
- cortex-context
status: canonical
links:
- 2026-06-02_paso-1-schema-spec-y-catalogo-inicial-buscador-semantico-de-videojuegos-con-cicd
vault_scope: local
fingerprint: 5d85c358145166a3b4e95f669b012eca8ee21dd14e7a5be5145de9f71712adde
term: Vocabulario semántico del catálogo
domain: null
related_terms: []
---

# Vocabulario semántico del catálogo


## Definition

Vocabulario canónico del dominio. Usar estos términos en specs y session notes (el CONTEXT.md estaba vacío al inicio del proyecto).

- **Catálogo / GameCatalogItem**: el conjunto de juegos; cada ítem es un `.md` con frontmatter (metadatos) + cuerpo (sinopsis). Su forma canónica la define `schemas/game.schema.yaml`.
- **Embedding**: vector de 384 dimensiones que representa el *significado* de un texto. Textos parecidos → vectores cercanos.
- **Vectorización**: convertir un texto en su embedding pasándolo por el modelo ONNX (all-MiniLM-L6-v2).
- **Mean pooling**: promediar los vectores de todos los tokens de una frase para obtener un único vector. NO se usa el token CLS ni max pooling.
- **Normalización L2**: escalar el vector a norma 1, de modo que la similitud coseno se reduzca a un producto punto.
- **Similitud coseno**: medida de cercanía semántica entre dos vectores (coseno del ángulo). 1 = idénticos, 0 = sin relación.
- **Expectativa de búsqueda (search-expectation)**: declaración `query → juegos esperados en top-K` en `specs/search-expectations.yaml`. Fuente de los tests de regresión.
- **Regresión semántica**: degradación del ranking de una query que antes funcionaba, provocada por agregar contenido nuevo. Los tests del Paso 5 la detectan.
- **SDD (3 capas)**: Capa A = schema estructural; Capa B = expectativas de búsqueda; Capa C = la postura de que la spec es la fuente de verdad de la que derivan código y tests.


