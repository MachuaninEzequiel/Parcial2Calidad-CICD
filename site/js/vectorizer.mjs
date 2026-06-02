// vectorizer.mjs — Vectorización de la query en el navegador (Paso 4).
//
// Acá vive —y SOLO acá— la dependencia pesada: Transformers.js, que por debajo
// es onnxruntime-web. Lo aislamos de search.mjs a propósito: search.mjs queda
// 100% puro (cero imports npm) para que `node --test site/js/search.test.mjs`
// siga corriendo sin instalar nada. Si vectorizeQuery() viviera en search.mjs,
// importar search.mjs en node:test arrastraría esta lib y rompería ese test.
//
// El mismo bare specifier '@huggingface/transformers' lo resuelven DOS mundos:
//   - En el navegador: el <script type="importmap"> de index.html → CDN ESM
//     (sin bundler, sin npm install).
//   - En Node (solo para el gate de equivalencia): la devDependency de
//     package.json.
// Por eso la versión del import map y la de package.json DEBEN coincidir EXACTO:
// browser y Node tienen que ejecutar el MISMO código para que la equivalencia
// Python↔JS (riesgo #1 del ADR-001) sea válida.
//
// Versión instalada/mapeada: @huggingface/transformers@4.2.0 (ver package.json
// e index.html). El knob de cuantización en v3/v4 es `dtype:'q8'` (la API vieja
// de v2 @xenova/transformers era `{quantized:true}`).

import { pipeline } from "@huggingface/transformers";

// Pipeline cacheado: el modelo (~23 MB) se baja/instancia UNA sola vez y se
// reutiliza en todas las queries. Guardamos la PROMESA (no el resultado) para
// que dos búsquedas disparadas casi a la vez compartan la misma descarga.
let _extractorPromise = null;

function getExtractor() {
  if (!_extractorPromise) {
    // dtype:'q8' → Transformers.js carga onnx/model_quantized.onnx (int8), que
    // es el MISMO artefacto que usa el lado Python (download_model.py baja el
    // quantized; models/model.onnx es int8, ~22 MB). Si cargáramos fp32, el diff
    // numérico contra Python explotaría y la equivalencia fallaría.
    //
    // Modelo: por defecto se baja del HF Hub (repo 'Xenova/all-MiniLM-L6-v2', el
    // mismo que download_model.py) y queda cacheado (browser cache / .cache en
    // Node). Fallback "mismo archivo local" opcional, no cableado por defecto:
    //   import { env } from '@huggingface/transformers';
    //   env.allowRemoteModels = false;        // no ir al CDN
    //   env.localModelPath = '/models/';      // servir models/ local
    // El spec solo pide DOCUMENTAR el fallback al CDN; lo dejamos en el camino
    // por defecto (CDN) para que el sitio ande sin configurar hosting de modelo.
    _extractorPromise = pipeline(
      "feature-extraction",
      "Xenova/all-MiniLM-L6-v2",
      { dtype: "q8" },
    );
  }
  return _extractorPromise;
}

/**
 * Convierte texto libre del usuario en un vector L2-normalizado de 384 dims,
 * usando el MISMO modelo que vectorizó el catálogo en el CI.
 *
 * {pooling:'mean', normalize:true} reproduce EXACTAMENTE el pipeline de
 * vectorize.py: mean pooling ponderado por attention_mask (mean_pooling) + L2
 * (l2_normalize). Mismo modelo + mismo tokenizer + mismo pooling/L2 en ambos
 * lados → mismo espacio semántico, así el coseno contra embeddings.json tiene
 * sentido (ADR-001). La equivalencia se prueba en tests/equivalence/.
 *
 * @param {string} text frase a vectorizar
 * @returns {Promise<number[]>} 384 floats, L2-normalizados
 */
export async function vectorizeQuery(text) {
  const extractor = await getExtractor();
  const output = await extractor(text, { pooling: "mean", normalize: true });
  return Array.from(output.data);
}
