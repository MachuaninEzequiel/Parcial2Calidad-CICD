---
schema_version: 1
doc_type: spec
title: Paso 2 — Script de vectorización ONNX (embeddings.json)
created_at: '2026-06-02T16:53:19.288128Z'
updated_at: '2026-06-02T16:53:19.288128Z'
tags:
- spec
- sdd
- ci-cd
- paso-2
- onnx
- embeddings
- vectorize
- mean-pooling
- l2
- numpy
- videojuegos
status: draft
links: []
vault_scope: local
fingerprint: d20a25a54585bb52d266ad555fd2216ed62088be6547bd93df12c9f63d076ec8
verification_hooks:
- name: download-model
  command: python scripts/download_model.py
  required: true
  success_criteria: exit code 0 — models/model.onnx y models/tokenizer.json presentes
  timeout_seconds: 600
- name: vectorize
  command: python scripts/vectorize.py
  required: true
  success_criteria: exit code 0 — genera dist/embeddings.json con 10 items de 384
    dims normalizados
  timeout_seconds: 300
- name: pytest-vectorize
  command: pytest -q tests/test_vectorize.py
  required: true
  success_criteria: exit code 0 — funciones puras (pooling/L2) y estructura del JSON
    OK
  timeout_seconds: 180
- name: validate-catalog-still-green
  command: python scripts/validate_catalog.py
  required: true
  success_criteria: exit code 0 — el refactor a catalog_io.py no rompió el Paso 1
  timeout_seconds: 120
- name: ruff-lint
  command: ruff check .
  required: false
  success_criteria: exit code 0 — código limpio
  timeout_seconds: 180
goal: 'Implementar la vectorización del catálogo: bajar el modelo all-MiniLM-L6-v2
  QUANTIZED int8 (~23 MB) + su tokenizer desde el repo Xenova/all-MiniLM-L6-v2, y
  generar dist/embeddings.json con un vector de 384 dims normalizado L2 por juego,
  vía mean pooling (con attention_mask) sobre la salida del modelo ONNX. La lógica
  de pooling + L2 debe quedar documentada y ser trivialmente replicable en JS (Paso
  4) para que los vectores sean comparables (premisa central, ver ADR-001). Reutilizar
  el parsing del Paso 1 extrayéndolo a scripts/catalog_io.py compartido. Tests unitarios
  de las funciones puras + validación de estructura del JSON. El modelo y el tokenizer
  NO se commitean (gitignored).'
files_in_scope:
- pyproject.toml
- scripts/catalog_io.py
- scripts/validate_catalog.py
- scripts/download_model.py
- scripts/vectorize.py
- tests/test_vectorize.py
- PRESENTACION.md
constraints:
- 'Decisiones de arquitectura cerradas (sección 3 del brief + ADR-001) NO se re-discuten.
  La premisa clave: el MISMO model.onnx corre en CI (Python) y en el browser (JS).'
- 'Modelo: all-MiniLM-L6-v2 QUANTIZED int8 del repo Xenova/all-MiniLM-L6-v2. El MISMO
  model.onnx + tokenizer.json se servirán al browser en el Paso 4. NO exportar ni
  convertir otra variante (nada de full fp32, nada de optimum/torch).'
- 'mean pooling con attention_mask + normalización L2: la lógica debe quedar documentada
  y ser trivialmente portable a JS. La equivalencia Python↔JS (tolerancia 1e-5) se
  testea recién en el Paso 4, no en este.'
- 'NO implementar todavía: frontend (site/), .github/workflows/ci.yml, Docker. Eso
  es Paso 3 en adelante.'
- 'models/*.onnx y dist/ permanecen gitignored: ni el modelo ni embeddings.json se
  commitean.'
- 'Reuso DRY: parse_game vive en UN solo lugar (catalog_io.py); validate_catalog.py
  y vectorize.py lo importan. No duplicar la lógica de parsing.'
- 'Avanzar paso a paso: al terminar el Paso 2, pausar y esperar confirmación del usuario
  antes del Paso 3. Cerrar con /cortex-documenter; si algún hook required falla, cerrar
  como ''handoff''.'
acceptance_criteria:
- '`python scripts/download_model.py` deja models/model.onnx y models/tokenizer.json
  en disco (o confirma que ya estaban); exit 0.'
- '`python scripts/vectorize.py` genera dist/embeddings.json y termina con exit 0.'
- dist/embeddings.json tiene dimensions=384 y 10 items; cada item incluye id, title,
  year, genres, summary y un vector de 384 números.
- 'Cada vector está normalizado L2: norma euclidiana ≈ 1.0 con tolerancia 1e-5.'
- '`pytest -q tests/test_vectorize.py` pasa (funciones puras + estructura del JSON).'
- 'El refactor no rompió el Paso 1: `python scripts/validate_catalog.py` sigue exit
  0 y `python scripts/validate_catalog.py --expect-fail tests/fixtures/invalid-game.md`
  sigue exit 0.'
- '`ruff check .` y `ruff format --check .` pasan sobre el código nuevo y editado.'
- Ni el modelo (~23 MB) ni dist/embeddings.json quedan trackeados por git (cubierto
  por .gitignore).
---

## Goal

Implementar la vectorización del catálogo: bajar el modelo all-MiniLM-L6-v2 QUANTIZED int8 (~23 MB) + su tokenizer desde el repo Xenova/all-MiniLM-L6-v2, y generar dist/embeddings.json con un vector de 384 dims normalizado L2 por juego, vía mean pooling (con attention_mask) sobre la salida del modelo ONNX. La lógica de pooling + L2 debe quedar documentada y ser trivialmente replicable en JS (Paso 4) para que los vectores sean comparables (premisa central, ver ADR-001). Reutilizar el parsing del Paso 1 extrayéndolo a scripts/catalog_io.py compartido. Tests unitarios de las funciones puras + validación de estructura del JSON. El modelo y el tokenizer NO se commitean (gitignored).

## Requirements

- pyproject.toml: agregar dependencias onnxruntime, numpy, tokenizers, huggingface_hub (manteniendo pyyaml + jsonschema). Siguen siendo deps centrales, no superfluas.
- scripts/catalog_io.py (NUEVO): extraer desde validate_catalog.py la función parse_game(md_path), load_schema() y las constantes REPO_ROOT/SCHEMA_PATH/CATALOG_DIR/FRONTMATTER_DELIM. Queda como única fuente del parsing del catálogo (DRY).
- scripts/validate_catalog.py (EDITAR): importar parse_game/load_schema/constantes desde catalog_io en vez de definirlas inline. Mantener EXACTAMENTE el mismo comportamiento (flag --expect-fail, exit codes, mensajes, reconfiguración UTF-8). Los hooks del Paso 1 deben seguir verdes.
- scripts/download_model.py (NUEVO): usar huggingface_hub.hf_hub_download para traer 'onnx/model_quantized.onnx' y 'tokenizer.json' del repo Xenova/all-MiniLM-L6-v2 hacia models/ (como models/model.onnx y models/tokenizer.json). Idempotente: si ya están, no re-baja. Mensajes claros del progreso.
- scripts/vectorize.py (NUEVO): carga models/model.onnx con onnxruntime y models/tokenizer.json con la lib tokenizers. Para cada catalog/*.md: parse_game → arma el texto concatenando title + ' ' + summary + ' ' + genres (en ese orden) → tokeniza con padding y truncation (max_length=128) → corre el modelo ONNX (input_ids, attention_mask, token_type_ids) → mean pooling sobre los tokens ponderado por attention_mask (NO promediar padding, NO usar CLS) → normalización L2 → vector de 384 dims. Escribe dist/embeddings.json: {model, dimensions:384, generated_at:<ISO8601 UTC>, items:[{id,title,year,genres,summary,vector}]}. Exponer mean_pooling() y l2_normalize() como funciones puras (numpy) testeables.
- tests/test_vectorize.py (NUEVO): (a) test de mean_pooling con input sintético conocido que verifica que el attention_mask excluye el padding; (b) test de l2_normalize: norma resultante ≈ 1.0 y manejo seguro del vector cero (sin división por cero); (c) test de estructura: si dist/embeddings.json existe, valida claves (model, dimensions, items), que hay 10 items y que cada vector tiene 384 floats con norma ≈ 1 (tol 1e-5). Los tests NO deben requerir descargar el modelo: funciones puras + validación condicional del JSON.
- Tras el paso, producir un fragmento (~3 párrafos) para PRESENTACION.md cubriendo el Paso 2 (qué es un embedding, mean pooling, L2, y por qué el mismo model.onnx corre en CI y browser).

## Files in Scope

- `pyproject.toml`
- `scripts/catalog_io.py`
- `scripts/validate_catalog.py`
- `scripts/download_model.py`
- `scripts/vectorize.py`
- `tests/test_vectorize.py`
- `PRESENTACION.md`

## Constraints

- Decisiones de arquitectura cerradas (sección 3 del brief + ADR-001) NO se re-discuten. La premisa clave: el MISMO model.onnx corre en CI (Python) y en el browser (JS).
- Modelo: all-MiniLM-L6-v2 QUANTIZED int8 del repo Xenova/all-MiniLM-L6-v2. El MISMO model.onnx + tokenizer.json se servirán al browser en el Paso 4. NO exportar ni convertir otra variante (nada de full fp32, nada de optimum/torch).
- mean pooling con attention_mask + normalización L2: la lógica debe quedar documentada y ser trivialmente portable a JS. La equivalencia Python↔JS (tolerancia 1e-5) se testea recién en el Paso 4, no en este.
- NO implementar todavía: frontend (site/), .github/workflows/ci.yml, Docker. Eso es Paso 3 en adelante.
- models/*.onnx y dist/ permanecen gitignored: ni el modelo ni embeddings.json se commitean.
- Reuso DRY: parse_game vive en UN solo lugar (catalog_io.py); validate_catalog.py y vectorize.py lo importan. No duplicar la lógica de parsing.
- Avanzar paso a paso: al terminar el Paso 2, pausar y esperar confirmación del usuario antes del Paso 3. Cerrar con /cortex-documenter; si algún hook required falla, cerrar como 'handoff'.

## Acceptance Criteria

- [ ] `python scripts/download_model.py` deja models/model.onnx y models/tokenizer.json en disco (o confirma que ya estaban); exit 0.
- [ ] `python scripts/vectorize.py` genera dist/embeddings.json y termina con exit 0.
- [ ] dist/embeddings.json tiene dimensions=384 y 10 items; cada item incluye id, title, year, genres, summary y un vector de 384 números.
- [ ] Cada vector está normalizado L2: norma euclidiana ≈ 1.0 con tolerancia 1e-5.
- [ ] `pytest -q tests/test_vectorize.py` pasa (funciones puras + estructura del JSON).
- [ ] El refactor no rompió el Paso 1: `python scripts/validate_catalog.py` sigue exit 0 y `python scripts/validate_catalog.py --expect-fail tests/fixtures/invalid-game.md` sigue exit 0.
- [ ] `ruff check .` y `ruff format --check .` pasan sobre el código nuevo y editado.
- [ ] Ni el modelo (~23 MB) ni dist/embeddings.json quedan trackeados por git (cubierto por .gitignore).

## Verification Hooks

Commands that objectively prove the work is done. Run by
`cortex finish-session` (Pluggable Middle, Phase 01).

### download-model
```bash
python scripts/download_model.py
```

Success: exit code 0 — models/model.onnx y models/tokenizer.json presentes · Timeout: 600s
### vectorize
```bash
python scripts/vectorize.py
```

Success: exit code 0 — genera dist/embeddings.json con 10 items de 384 dims normalizados · Timeout: 300s
### pytest-vectorize
```bash
pytest -q tests/test_vectorize.py
```

Success: exit code 0 — funciones puras (pooling/L2) y estructura del JSON OK · Timeout: 180s
### validate-catalog-still-green
```bash
python scripts/validate_catalog.py
```

Success: exit code 0 — el refactor a catalog_io.py no rompió el Paso 1 · Timeout: 120s
### ruff-lint *(optional)*
```bash
ruff check .
```

Success: exit code 0 — código limpio · Timeout: 180s
