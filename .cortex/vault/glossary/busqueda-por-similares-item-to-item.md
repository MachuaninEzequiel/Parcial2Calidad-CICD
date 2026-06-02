---
schema_version: 1
doc_type: glossary
title: Búsqueda por similares (item-to-item)
created_at: '2026-06-02T18:05:21.275802Z'
updated_at: '2026-06-02T18:05:21.275802Z'
tags:
- glossary
- domain
- frontend
- busqueda
- coseno
- paso-3
status: canonical
links:
- vocabulario-semantico-del-catalogo
- 2026-06-02_paso-3-frontend-estatico-site-carga-de-embeddingsjson-busqueda-por-similitud-coseno-y-ui-vectorizacion-en-browser-diferida-al-paso-4
vault_scope: local
fingerprint: afc80c7562c3eb83f85696b8efdcd20d16e0c6657021a912a43f09101be3746c
term: Búsqueda por similares (item-to-item)
domain: null
related_terms: []
---

# Búsqueda por similares (item-to-item)


## Definition

Modo de búsqueda semántica que rankea el catálogo por similitud coseno contra el vector YA precomputado de un juego del propio catálogo, en lugar de contra una query de texto libre. No necesita vectorizar nada nuevo en el navegador, así que es la feature demoable del Paso 3 mientras la vectorización de texto libre (el mismo model.onnx corriendo en el browser vía onnxruntime-web) llega en el Paso 4. Implementación: site/js/app.mjs llama topK(vectorDelJuego, items, k=6), excluye al propio juego por id y muestra el top-5. Se apoya en cosineSimilarity/topK de site/js/search.mjs (funciones puras reutilizables tal cual por el Paso 4). Contrasta con 'Expectativa de búsqueda', que sí parte de una query de texto.


