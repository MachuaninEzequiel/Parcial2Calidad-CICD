// search.test.mjs — Tests de las funciones puras con el runner NATIVO de Node.
//
// Corre con `node --test site/js/search.test.mjs`. Cero npm, cero browser: las
// funciones de search.mjs no tocan el DOM, así que se prueban como código común.
// El test del JSON real es CONDICIONAL: dist/embeddings.json es gitignored (lo
// genera el Paso 2), así que si no está, se saltea con un mensaje en vez de
// fallar el CI por algo que no es responsabilidad del Paso 3.

import { test } from "node:test";
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";

import { cosineSimilarity, topK } from "./search.mjs";

const EPS = 1e-9;
const close = (got, want) => Math.abs(got - want) < EPS;

test("cosineSimilarity: vectores idénticos → 1", () => {
  const v = [1, 2, 3, 4];
  assert.ok(close(cosineSimilarity(v, v), 1), "idénticos deberían dar ≈1");
});

test("cosineSimilarity: vectores ortogonales → 0", () => {
  assert.ok(close(cosineSimilarity([1, 0], [0, 1]), 0), "ortogonales → 0");
});

test("cosineSimilarity: vectores opuestos → -1", () => {
  assert.ok(close(cosineSimilarity([1, 2, 3], [-1, -2, -3]), -1), "opuestos → -1");
});

test("cosineSimilarity: norma 0 → 0 (sin NaN ni división por cero)", () => {
  const r = cosineSimilarity([0, 0, 0], [1, 2, 3]);
  assert.ok(!Number.isNaN(r), "no debe ser NaN");
  assert.equal(r, 0, "vector nulo no tiene parecido con nada → 0");
});

test("cosineSimilarity: correcta con vectores NO normalizados", () => {
  // [3,0] y [0,5] son ortogonales aunque sus magnitudes difieran → coseno 0.
  assert.ok(close(cosineSimilarity([3, 0], [0, 5]), 0));
  // [2,2] y [5,5] apuntan al mismo lado (misma dirección) → coseno 1.
  assert.ok(close(cosineSimilarity([2, 2], [5, 5]), 1));
});

test("cosineSimilarity: distinta longitud lanza Error", () => {
  assert.throws(() => cosineSimilarity([1, 2], [1, 2, 3]), /igual longitud/);
});

test("topK: devuelve exactamente k items ordenados desc por score", () => {
  // query alineada con el eje x; rankeamos por cuánto apuntan hacia +x.
  const query = [1, 0];
  const items = [
    { id: "casi-ortogonal", vector: [1, 5] },
    { id: "exacto", vector: [1, 0] },
    { id: "opuesto", vector: [-1, 0] },
    { id: "diagonal", vector: [1, 1] },
  ];

  const res = topK(query, items, 2);
  assert.equal(res.length, 2, "devuelve exactamente k");
  assert.equal(res[0].item.id, "exacto", "el más parecido va primero");
  assert.equal(res[1].item.id, "diagonal", "el segundo es la diagonal");
  assert.ok(res[0].score >= res[1].score, "ordenado descendente");
});

test("topK: k > items.length devuelve todos", () => {
  const items = [
    { id: "a", vector: [1, 0] },
    { id: "b", vector: [0, 1] },
  ];
  const res = topK([1, 0], items, 10);
  assert.equal(res.length, 2, "no inventa items: devuelve los que hay");
});

test("topK: no muta el array de items de entrada", () => {
  const items = [
    { id: "a", vector: [0, 1] },
    { id: "b", vector: [1, 0] },
  ];
  const orden = items.map((i) => i.id);
  topK([1, 0], items, 2);
  assert.deepEqual(
    items.map((i) => i.id),
    orden,
    "topK no debe reordenar el array original",
  );
});

// La vectorización de la query se mudó a site/js/vectorizer.mjs (Paso 4) para no
// arrastrar Transformers.js a este test puro. Su equivalencia Python↔JS se prueba
// en tests/equivalence/embed.equiv.test.mjs (gate aparte, ese sí con la lib).

// --- Test CONDICIONAL del embeddings.json real ------------------------------
// Ruta robusta relativa a ESTE archivo (no al cwd): site/js/ → ../../dist/.
const embeddingsPath = new URL("../../dist/embeddings.json", import.meta.url);

test("embeddings.json: contrato y auto-similitud (condicional si existe)", (t) => {
  if (!existsSync(embeddingsPath)) {
    t.skip(
      "dist/embeddings.json no está (es gitignored). Generalo con " +
        "`python scripts/vectorize.py` para correr este test.",
    );
    return;
  }

  const data = JSON.parse(readFileSync(embeddingsPath, "utf8"));
  assert.equal(data.dimensions, 384, "dimensions debe ser 384");
  assert.equal(data.items.length, 10, "el catálogo tiene 10 juegos");
  assert.equal(
    data.items[0].vector.length,
    384,
    "cada item tiene un vector de 384",
  );

  // La auto-similitud de un juego consigo mismo debe rankearlo primero (≈1).
  const res = topK(data.items[0].vector, data.items, 5);
  assert.equal(res.length, 5, "topK devuelve 5 resultados");
  assert.equal(
    res[0].item.id,
    data.items[0].id,
    "el propio juego es el más parecido a sí mismo",
  );
  assert.ok(
    Math.abs(res[0].score - 1) < 1e-5,
    "auto-similitud ≈ 1 (vectores L2-normalizados del Paso 2)",
  );
});
