// app.mjs — Wiring del DOM. Carga embeddings.json, renderiza el catálogo y
// maneja la búsqueda de "juegos similares". Importa el motor de search.mjs (la
// lógica pura) y se queda solo con lo que tiene que ver con la página.

import { topK } from "./search.mjs";

// Ruta al JSON de embeddings (gitignored, lo genera el Paso 2).
//
// Preview local: servir la RAÍZ del repo (`python -m http.server 8000`) y abrir
// http://localhost:8000/site/ ; así esta ruta relativa resuelve a
// /dist/embeddings.json. El build del Paso 6 ajustará esta ruta para producción.
// NO copiar embeddings.json dentro de site/: site/ NO está gitignored y se
// commitearía por error (el JSON debe seguir viviendo en dist/).
const EMBEDDINGS_URL = "../dist/embeddings.json";

// Cuántos similares mostramos. Pedimos uno de más (K_FETCH) para poder excluir
// al propio juego y aun así mostrar K_SHOW resultados.
const K_SHOW = 5;
const K_FETCH = K_SHOW + 1;

// Referencias al DOM (las resolvemos al cargar el documento).
let catalogEl;
let resultsEl;
let formEl;
let queryEl;
let searchBtnEl;
let statusEl;

// Los items del catálogo, guardados a nivel módulo: el catálogo los renderiza y
// el handler de búsqueda por texto libre los rankea (DRY: la misma maquinaria que
// "buscar similares"). Antes vivían solo dentro de init() y se perdían.
let catalogItems = [];

document.addEventListener("DOMContentLoaded", () => {
  catalogEl = document.getElementById("catalogo");
  resultsEl = document.getElementById("resultados");
  formEl = document.getElementById("search-form");
  queryEl = document.getElementById("free-query");
  searchBtnEl = document.getElementById("search-btn");
  statusEl = document.getElementById("search-status");
  if (formEl) {
    formEl.addEventListener("submit", onFreeQuerySubmit);
  }
  init();
});

async function init() {
  let data;
  try {
    const resp = await fetch(EMBEDDINGS_URL);
    if (!resp.ok) {
      throw new Error(`HTTP ${resp.status} al pedir ${EMBEDDINGS_URL}`);
    }
    data = await resp.json();
  } catch (err) {
    renderLoadError(err);
    return;
  }

  const items = data.items ?? [];
  if (items.length === 0) {
    renderLoadError(new Error("embeddings.json no tiene items."));
    return;
  }

  catalogItems = items;
  renderCatalog(items);
}

/** Mensaje de error claro y accionable si no se pudo cargar el JSON. */
function renderLoadError(err) {
  catalogEl.innerHTML = "";
  const box = document.createElement("div");
  box.className = "error";
  box.innerHTML =
    "<strong>No se pudo cargar <code>embeddings.json</code>.</strong>" +
    "<p>Generalo con <code>python scripts/vectorize.py</code> y serví la " +
    "<em>raíz del repo</em> (por ejemplo <code>python -m http.server 8000</code>), " +
    "después abrí <code>http://localhost:8000/site/</code>.</p>";
  const detail = document.createElement("p");
  detail.className = "error-detail";
  detail.textContent = `Detalle: ${err.message}`;
  box.appendChild(detail);
  catalogEl.appendChild(box);
}

/** Renderiza una card por cada juego del catálogo. */
function renderCatalog(items) {
  catalogEl.innerHTML = "";
  const frag = document.createDocumentFragment();

  for (const item of items) {
    frag.appendChild(buildCard(item, items));
  }

  catalogEl.appendChild(frag);
}

/**
 * Construye la card de un juego. `allItems` se pasa para que el botón
 * "buscar similares" pueda rankear contra todo el catálogo.
 */
function buildCard(item, allItems) {
  const card = document.createElement("article");
  card.className = "card";

  const h3 = document.createElement("h3");
  h3.textContent = item.title;

  const year = document.createElement("span");
  year.className = "year";
  year.textContent = String(item.year);
  h3.appendChild(year);
  card.appendChild(h3);

  // Géneros: los leemos del DATO (Capa C de SDD), no de un enum hardcodeado.
  const genres = document.createElement("div");
  genres.className = "genres";
  for (const g of item.genres ?? []) {
    const chip = document.createElement("span");
    chip.className = "chip";
    chip.textContent = g;
    genres.appendChild(chip);
  }
  card.appendChild(genres);

  const summary = document.createElement("p");
  summary.className = "summary";
  summary.textContent = item.summary ?? "";
  card.appendChild(summary);

  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "similar-btn";
  btn.textContent = "Buscar similares";
  btn.addEventListener("click", () => showSimilar(item, allItems));
  card.appendChild(btn);

  return card;
}

/**
 * Muestra los K_SHOW juegos más parecidos a `selected`, excluyéndolo del
 * resultado. Pedimos K_FETCH a topK y filtramos al propio juego por id.
 */
function showSimilar(selected, allItems) {
  const ranked = topK(selected.vector, allItems, K_FETCH)
    .filter(({ item }) => item.id !== selected.id)
    .slice(0, K_SHOW);

  renderResults(`Juegos similares a ${selected.title}`, ranked);
}

/**
 * Render compartido del top-N (DRY): lo usan TANTO "buscar similares" COMO la
 * búsqueda por texto libre. Recibe el título y la lista ya rankeada de topK
 * ([{item, score}, ...]) y arma la <ol> de resultados.
 */
function renderResults(headingText, ranked) {
  resultsEl.innerHTML = "";

  const heading = document.createElement("h2");
  heading.textContent = headingText;
  resultsEl.appendChild(heading);

  const list = document.createElement("ol");
  list.className = "result-list";

  for (const { item, score } of ranked) {
    const li = document.createElement("li");
    li.className = "result-item";

    const title = document.createElement("span");
    title.className = "result-title";
    title.textContent = item.title;

    const scoreEl = document.createElement("span");
    scoreEl.className = "result-score";
    // Score formateado a 3 decimales para la demo.
    scoreEl.textContent = `coseno ${score.toFixed(3)}`;

    li.appendChild(title);
    li.appendChild(scoreEl);
    list.appendChild(li);
  }

  resultsEl.appendChild(list);

  // Llevamos el foco/scroll a los resultados para que la demo se vea clara.
  resultsEl.scrollIntoView({ behavior: "smooth", block: "start" });
}

/**
 * Handler de la búsqueda por texto libre (Paso 4). Al enviar el form:
 *   1. valida que haya texto y muestra estado de carga.
 *   2. importa vectorizer.mjs PEREZOSAMENTE (`await import`): así el catálogo y
 *      "buscar similares" funcionan aunque el CDN de Transformers.js falle o
 *      tarde — la lib pesada solo se baja cuando el usuario realmente busca.
 *   3. vectoriza la query con el MISMO modelo del catálogo (vectorizeQuery).
 *   4. rankea con topK (la MISMA maquinaria que "buscar similares") y renderiza.
 *   5. rehabilita el form; si algo falla, muestra un error claro.
 */
async function onFreeQuerySubmit(event) {
  event.preventDefault();
  const text = queryEl.value.trim();
  if (!text) {
    return;
  }

  setSearchBusy(true);
  setStatus(
    "Vectorizando tu búsqueda… la PRIMERA vez se baja el modelo (~23 MB), " +
      "después es instantáneo.",
  );

  try {
    // Lazy import: la dependencia pesada (Transformers.js) entra recién acá.
    const { vectorizeQuery } = await import("./vectorizer.mjs");
    const queryVector = await vectorizeQuery(text);
    const ranked = topK(queryVector, catalogItems, K_SHOW);
    renderResults(`Resultados para “${text}”`, ranked);
    setStatus("");
  } catch (err) {
    setStatus("");
    renderSearchError(err);
  } finally {
    setSearchBusy(false);
  }
}

/** Deshabilita/rehabilita el input y el botón mientras se busca. */
function setSearchBusy(busy) {
  if (queryEl) queryEl.disabled = busy;
  if (searchBtnEl) {
    searchBtnEl.disabled = busy;
    searchBtnEl.textContent = busy ? "Buscando…" : "Buscar";
  }
}

/** Mensaje de estado (carga) debajo de la caja. Vacío = oculto. */
function setStatus(message) {
  if (!statusEl) return;
  statusEl.textContent = message;
  statusEl.hidden = message === "";
}

/** Error claro si el modelo no carga (CDN caído, sin red, etc.). */
function renderSearchError(err) {
  resultsEl.innerHTML = "";
  const box = document.createElement("div");
  box.className = "error";
  box.innerHTML =
    "<strong>No se pudo vectorizar la búsqueda.</strong>" +
    "<p>El modelo se baja una vez desde el CDN de Hugging Face; revisá tu " +
    "conexión y volvé a intentar. Mientras tanto, “Buscar similares” en cada " +
    "card sigue andando (no necesita el modelo).</p>";
  const detail = document.createElement("p");
  detail.className = "error-detail";
  detail.textContent = `Detalle: ${err.message}`;
  box.appendChild(detail);
  resultsEl.appendChild(box);
}
