// search.mjs — Motor de búsqueda semántica (funciones puras, CERO DOM).
//
// Este módulo es el corazón del ranking y NO toca el DOM ni hace fetch ni
// importa nada de npm: por eso se puede testear con el runner nativo de Node
// (node:test) sin un browser ni dependencias. La MISMA lógica la reutiliza la
// búsqueda por texto libre del Paso 4: solo cambia de dónde sale el queryVector
// (lo vectoriza site/js/vectorizer.mjs en el browser), el coseno y el ranking
// quedan igual (DRY). La vectorización vive en vectorizer.mjs justamente para no
// arrastrar Transformers.js acá y romper la pureza de este módulo.

/**
 * Similitud coseno entre dos vectores: dot(a, b) / (||a|| · ||b||).
 *
 * El coseno mide el ángulo entre dos vectores e ignora su magnitud: vale 1 si
 * apuntan al mismo lado, 0 si son ortogonales y -1 si son opuestos. Es la medida
 * de "cercanía semántica" del proyecto.
 *
 * Premisa del Paso 2: los vectores del catálogo (embeddings.json) vienen
 * L2-normalizados (longitud 1), así que para ELLOS el coseno se reduce a un
 * simple producto punto y el Paso 4 lo explota para evitar recalcular normas.
 * Aun así, esta implementación calcula las normas de verdad para ser correcta
 * con CUALQUIER input (vectores no normalizados incluidos), no solo los del JSON.
 *
 * Guarda anti-NaN: si alguna norma es 0 (vector nulo), devolvemos 0 en vez de
 * dividir por cero. Un vector sin dirección no tiene "parecido" con nada.
 *
 * @param {number[]} a
 * @param {number[]} b
 * @returns {number} similitud en [-1, 1] (0 si alguna norma es 0)
 */
export function cosineSimilarity(a, b) {
  if (!Array.isArray(a) || !Array.isArray(b) || a.length !== b.length) {
    throw new Error(
      `cosineSimilarity: se esperaban dos vectores de igual longitud ` +
        `(recibí ${a?.length} y ${b?.length}).`,
    );
  }

  let dot = 0;
  let normA = 0;
  let normB = 0;
  for (let i = 0; i < a.length; i++) {
    dot += a[i] * b[i];
    normA += a[i] * a[i];
    normB += b[i] * b[i];
  }

  if (normA === 0 || normB === 0) {
    return 0;
  }

  return dot / (Math.sqrt(normA) * Math.sqrt(normB));
}

/**
 * Rankea los items por similitud coseno contra queryVector y devuelve los k
 * mejores, de mayor a menor score.
 *
 * No muta el array de entrada (ordena sobre una copia). Si k es mayor que la
 * cantidad de items, devuelve todos los que haya.
 *
 * @param {number[]} queryVector
 * @param {Array<{vector: number[]}>} items items con un campo `vector`
 * @param {number} [k=5]
 * @returns {Array<{item: object, score: number}>} ordenado desc por score
 */
export function topK(queryVector, items, k = 5) {
  const scored = items.map((item) => ({
    item,
    score: cosineSimilarity(queryVector, item.vector),
  }));

  scored.sort((x, y) => y.score - x.score);

  return scored.slice(0, k);
}

// La vectorización de la query (texto libre → vector de 384 dims con el modelo
// ONNX en el navegador) vive en site/js/vectorizer.mjs, NO acá: importa
// Transformers.js y este módulo tiene que quedar puro y testeable sin npm.
