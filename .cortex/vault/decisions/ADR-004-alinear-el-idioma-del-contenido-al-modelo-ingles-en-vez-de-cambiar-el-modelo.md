---
schema_version: 1
doc_type: adr
title: Alinear el idioma del contenido al modelo (inglés) en vez de cambiar el modelo
created_at: '2026-06-03T02:08:14.161661Z'
updated_at: '2026-06-03T02:08:14.161661Z'
tags:
- adr
- ci-cd
- ingles
- modelo
- embeddings
- calidad-busqueda
- catalogo
- supersedes-adr-003
- adr-001
status: accepted
links:
- .cortex/vault/decisions/ADR-003-modelo-ingles-vs-queries-en-espanol.md
- .cortex/vault/decisions/ADR-001-arquitectura-100-estatica-con-modelo-onnx-dual-runtime-ci-browser.md
- .cortex/vault/specs/2026-06-03_migrar-el-contenido-del-modelo-a-ingles.md
- .cortex/vault/sessions/2026-06-03_migrar-el-contenido-del-modelo-a-ingles_cierre-migracion-del-contenido-a-ingles.md
vault_scope: local
fingerprint: 261c41635be0d548326aa65ed069c4d51898bda95f90414de340dbe414e708c4
adr_number: 4
supersedes:
- ADR-003
superseded_by: null
alternatives_considered: []
acceptance_criteria_met: false
---

## Context

El modelo de embeddings es all-MiniLM-L6-v2 (fijado por ADR-001: int8, ~23MB, mismo artefacto en CI y browser), que es principalmente de INGLÉS. El ADR-003 había decidido mantener el modelo y 'afinar el contenido del catálogo en español'. En la práctica eso sólo parcheaba las 5 queries declaradas en search-expectations.yaml (teaching-to-the-test): al probar la web con búsqueda por texto libre arbitraria en español, el modelo NO discriminaba — casi toda query devolvía el mismo cluster (disco-elysium / gris) y juegos obvios no aparecían (p.ej. 'relajante' no traía stardew-valley). Diagnóstico read-only: con las MISMAS queries en inglés el modelo sí discrimina ('relaxing farming game' → stardew-valley #1). O sea: el problema es el IDIOMA del contenido, no el modelo ni la falta de ejemplos.

## Decision

Alinear el IDIOMA DEL CONTENIDO al modelo: migrar a INGLÉS todo lo que el modelo LEE — las sinopsis de los 10 catalog/*.md, el enum de géneros del schema (Capa A) + el campo genres de los .md, las 5 queries de search-expectations.yaml, y el ejemplo/placeholder de la caja de búsqueda. NO se cambia el modelo, el pipeline (vectorize/equivalencia), download_model.py, vectorizer.mjs ni la arquitectura. README.md, PRESENTACION.md y el chrome de UI quedan en ESPAÑOL (la defensa oral es en español; esos textos no impactan al modelo). Esta decisión SUPERSEDE el ADR-003.

## Alternatives Considered

(none)

## Consequences

(+) La búsqueda por texto libre ahora discrimina bien, verificado: 'relaxing farming game' → stardew-valley #1, 'open world medieval rpg' → witcher-3 #1, y las 5 expectativas (ahora inglesas) entran fuerte. Ya no colapsa todo en disco-elysium/gris. (+) Se mantiene el modelo chico de 23MB: ADR-001 y el presupuesto de descarga del browser intactos; la equivalencia Python↔JS sigue verde (mismo modelo/pipeline, max|diff| 4.47e-8). (+) Cero cambio de arquitectura/lógica: es migración de CONTENIDO + el enum de Capa A. (−/trade-off) El repo queda con idiomas MEZCLADOS: contenido del modelo en inglés, UI-chrome + docs + defensa en español. Aceptado por el usuario. (−/limitación) El enum tiene 'horror' y 'shooter' pero ningún juego del catálogo los usa, así que esas queries no tienen ground-truth fuerte (devuelven el más cercano disponible). Mitigación futura: sumar juegos de esos géneros.

## Supersedes

- [[ADR-003]]
