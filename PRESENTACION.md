# 🎤 Guion de presentación oral (5 minutos)

> Este archivo se arma de a fragmentos, uno por cada paso del desarrollo.
> Al final, juntos forman el guion completo para defender el proyecto oralmente.

---

## Fragmento · Paso 1 — Schema, Spec y Catálogo

**Qué mostrar:** los archivos `schemas/game.schema.yaml` y `specs/search-expectations.yaml`, un par de juegos en `catalog/`, y el validador corriendo en la terminal.

**Qué decir (la idea central):**

Arrancamos por la base de **Spec Driven Development**. Antes de escribir una sola línea de lógica, definimos la *fuente de verdad* del proyecto en dos archivos. El primero, `game.schema.yaml`, es un **JSON Schema** que describe qué es un juego válido: qué campos tiene, qué géneros existen, qué longitud mínima necesita la sinopsis. El segundo, `search-expectations.yaml`, declara qué resultados esperamos de ciertas búsquedas: es nuestra red de **regresión semántica**.

La gracia de SDD es la dirección de las dependencias: el código se deriva de la spec, nunca al revés. Por ejemplo, la lista de géneros válidos vive **solo** en el schema; ni el frontend ni los tests la repiten, la leen de ahí. Si mañana quiero agregar un campo, lo toco primero en el schema y el pipeline me obliga a que todo lo demás se acomode. Eso garantiza coherencia, que es justo uno de los criterios que se evalúan.

Para que esto no quede en una intención, escribimos `validate_catalog.py`: lee el schema y valida cada juego del catálogo contra él. Lo demostramos en vivo de dos formas: primero con el catálogo real, que pasa en verde; después con un archivo malformado a propósito, que el validador **rechaza**. Y el remate: ese mismo schema es el que GitHub Actions va a correr en el CI. Lo que valida tu máquina es exactamente lo que valida el servidor.

---

## Fragmento · Paso 2 — Vectorización ONNX

**Qué mostrar:** `scripts/vectorize.py` corriendo en la terminal y el `dist/embeddings.json` generado (abrir un item: id, título y el array de 384 números).

**Qué decir (la idea central):**

Acá entra la inteligencia artificial. Un **embedding** es convertir un texto en una lista de 384 números que captura su *significado*: textos parecidos quedan cerca en ese espacio. Para generarlos usamos un modelo liviano, **all-MiniLM-L6-v2**, en formato **ONNX** (~23 MB). El script `vectorize.py` recorre el catálogo, arma un texto con el título, la sinopsis y los géneros de cada juego, y lo pasa por el modelo.

El modelo no devuelve un vector por frase, sino uno por cada palabra (token). Para tener un único vector por juego aplicamos **mean pooling**: promediamos los vectores de todos los tokens reales (ignorando el relleno). Después **normalizamos a L2**, que es escalar el vector para que su longitud sea 1; eso hace que comparar dos juegos sea una simple multiplicación —la **similitud coseno**—. El resultado se guarda en `embeddings.json`: el catálogo ya vectorizado.

Y acá está el truco que le da coherencia a todo el proyecto: **este mismo `model.onnx` se va a usar de nuevo en el navegador** (Paso 4) para vectorizar lo que tipea el usuario. Mismo modelo, misma operación de pooling y de normalización en los dos lados. Por eso los vectores son comparables: el del catálogo lo calcula el servidor de CI, el de tu búsqueda lo calcula tu navegador, y ambos viven en el mismo espacio semántico.

---

## Fragmento · Paso 3 — Frontend estático y motor de ranking

**Qué mostrar:** el sitio en `site/` corriendo en el navegador (las cards de los 10 juegos), un click en "Buscar similares" mostrando el top-5 con su score, la caja de texto libre deshabilitada con la nota del Paso 4, y `node --test site/js/search.test.mjs` en verde.

**Qué decir (la idea central):**

Con el catálogo ya vectorizado, el Paso 3 arma la mitad visible del proyecto: un sitio **100% estático** —HTML, CSS y JavaScript vanilla, sin frameworks ni bundlers— que carga el `embeddings.json` y deja buscar por significado. El corazón es la **similitud coseno**: para comparar dos juegos no miramos las palabras, miramos el ángulo entre sus vectores. Si dos juegos apuntan en la misma dirección del espacio de 384 dimensiones, el coseno da cerca de 1 y son "parecidos"; si son ortogonales da 0; si apuntan a lados opuestos, -1. Es una medida de *cercanía de significado*, no de coincidencia textual.

Acá se ve por qué el Paso 2 se tomó el trabajo de **normalizar los vectores a L2** (longitud 1). El coseno general es `producto_punto / (norma_a · norma_b)`, pero si ambas normas valen 1, el denominador desaparece y el coseno se reduce a un simple **producto punto**: una suma de multiplicaciones, baratísima de calcular en el navegador. Nuestra función `cosineSimilarity` igual calcula las normas de verdad para ser correcta con cualquier entrada, pero la premisa de los vectores normalizados es la que hace que esto escale. Esa lógica vive en `search.mjs` como **funciones puras sin DOM**, y por eso la podemos testear con el runner nativo de Node (`node:test`) sin instalar un solo paquete npm.

¿Y la búsqueda por texto libre? Esa caja está **a propósito deshabilitada** y marcada como "Paso 4". El motivo es honesto: para buscar con una frase escrita hay que vectorizar esa frase con el **mismo `model.onnx`, pero ahora corriendo dentro del navegador** (onnxruntime-web), y eso es justo el desafío técnico del próximo paso —junto con el test de equivalencia que verifica que Python y JavaScript producen el mismo vector—. Para no prometer algo que todavía no anda, dejamos la función `vectorizeQuery()` como un *seam*: existe, pero lanza un error explícito de "Paso 4" en vez de devolver resultados vacíos en silencio. Mientras tanto, el Paso 3 ya demuestra el motor completo con la búsqueda de **juegos similares**: tomamos el vector de un juego del catálogo y rankeamos al resto contra él. Es la misma maquinaria de ranking que el Paso 4 va a reutilizar tal cual.

---

## Fragmento · Paso 4 — Vectorización en el navegador y equivalencia Python↔JS

**Qué mostrar:** la caja de texto libre ya habilitada; tipear cualquier frase y ver que devuelve un top-5 vectorizado en vivo en el navegador; abrir `site/js/vectorizer.mjs` y el import map de `index.html`; y `node --test tests/equivalence/embed.equiv.test.mjs` en verde.

**Qué decir (la idea central):**

Acá cerramos el círculo: la misma red neuronal que vectorizó el catálogo en el CI ahora corre **dentro de tu navegador**. Cuando escribís una frase y le das Buscar, no mandamos nada a ningún servidor: el `model.onnx` —el mismo archivo, byte por byte— se baja una vez desde un CDN y se ejecuta en JavaScript con **Transformers.js**, que por debajo es **onnxruntime-web**. Esa frase se convierte en un vector de 384 números con el mismo mean pooling y la misma normalización L2 que usó Python, y después la comparamos con la similitud coseno contra el catálogo ya vectorizado. Lo elegante es que reusamos **exactamente** la misma función `topK` del Paso 3: lo único que cambia es de dónde sale el vector de la query. Y para no contaminar las funciones puras, toda la parte pesada vive aislada en `vectorizer.mjs`; `search.mjs` sigue testeándose sin instalar un solo paquete.

Pero el corazón del paso —y lo que marcamos como **riesgo número uno** en nuestro ADR-001— es: ¿de verdad Python y JavaScript producen el **mismo** vector? Si no, la query y el catálogo vivirían en espacios distintos y la búsqueda sería basura disfrazada. Para no confiar en la fe, escribimos un **test de equivalencia**: Python emite los vectores de referencia de un set de queries fijas, y un test en Node los recalcula con Transformers.js y verifica dos cosas —que el vector coincida dentro de una tolerancia de `1e-5`, y que el ranking de los 5 mejores sea **idéntico**—. La primera vez no daba: el diff era de `3e-2`, mil veces más grande de lo aceptable. Investigando encontramos la causa fina: el tokenizer de Python rellena la frase hasta 128 tokens, y como el modelo está **cuantizado a enteros de 8 bits**, el largo de la secuencia cambia un poquito los números. El navegador no rellena. Igualamos los dos lados —que Python vectorice la query sin relleno, igual que el browser— y el diff se desplomó a `4e-8`. Eso no es un parche: es exactamente lo que pasa en producción, porque en vivo la query siempre la vectoriza el navegador sin padding. Ese test queda como **gate de CI**: si una futura versión del modelo o de la librería rompiera la equivalencia, el pipeline lo frena antes de que llegue a la gente.

Una aclaración honesta para no sobrevender: el test de equivalencia prueba que Python y JavaScript dan el **mismo** vector, no que el resultado sea **semánticamente bueno**. Y acá saltó algo: el modelo es chico y principalmente de inglés, así que con queries cortas en español rendía flojo —la propia demo del sillón → Overcooked 2 todavía no andaba en español al cerrar el Paso 4—. Decidir qué hacer con eso (¿cambiar de modelo o afinar el catálogo?) lo dejamos documentado en el ADR-003 y lo resolvimos en el Paso 5.

---

## Fragmento · Paso 5 — Regresión semántica y afinado del catálogo

**Qué mostrar:** `specs/search-expectations.yaml` (las 5 expectativas), `tests/test_search_regression.py` corriendo en verde, y en el navegador tipear *"juego para jugar con amigos en el sillón"* para que **Overcooked 2 aparezca primero** (y *"souls-like para principiantes"* → **Hollow Knight** arriba).

**Qué decir (la idea central):**

Acá cerramos el círculo de SDD. En el Paso 1 escribimos `search-expectations.yaml`, la Capa B: una lista declarativa de *"para esta query, al menos uno de estos juegos tiene que aparecer en el top-5"*. Hasta ahora era una intención; en el Paso 5 se convierte en **tests reales**. `test_search_regression.py` **lee ese YAML en tiempo de ejecución** y genera un caso de test por cada expectativa —no hardcodeamos nada—: vectoriza la query reusando el mismo `embed()` de `vectorize.py`, la rankea contra el catálogo por similitud coseno y verifica que el juego esperado caiga en el top-5. Es una **red de regresión semántica**: si mañana agrego un juego o reescribo una sinopsis y eso degrada una búsqueda que antes andaba, el CI me frena. Y un detalle fino de coherencia: el test vectoriza la query **sin padding**, igual que el navegador (ADR-002), así el ranking del gate es el mismo que ve el usuario.

El problema concreto era que dos demos no entraban: *"juego para jugar con amigos en el sillón"* no traía Overcooked 2 y *"souls-like para principiantes"* no traía Hollow Knight. Acá vino la decisión interesante, que quedó escrita en el **ADR-003**: el modelo es chico y principalmente de inglés, así que la tentación era cambiarlo por uno multilingüe. Pero eso rompía todo lo construido —el ADR-001, el presupuesto de descarga del navegador, la equivalencia del Paso 4—. Elegimos el camino barato y coherente: en vez de cambiar el modelo, **afinamos el contenido del catálogo en español**. Reescribimos los summaries de Overcooked 2 y Hollow Knight para que **lideren con el ángulo que la query busca** —el cooperativo en el sillón, el souls-like accesible—, sin keyword-stuffing ni repetir la query literal: prosa natural y honesta. Re-vectorizamos, re-emitimos el fixture de referencia y verificamos que la equivalencia Python↔JS **siguiera verde**.

El resultado es la demo en vivo que prometía el README desde la línea 5 y que ahora **es real**: escribís *"juego para jugar con amigos en el sillón"* y Overcooked 2 sale **primero**, sin que esa frase esté escrita textualmente en su ficha. Eso es exactamente lo que vende el proyecto —buscar por significado, no por palabras—, y ahora hay un test que lo defiende: si alguien rompe esa búsqueda, el pipeline lo cachea. Pasamos de una promesa aspiracional a una garantía verificada por el CI.

---

## Fragmento · Paso 6 — Integración Continua con GitHub Actions

**Qué mostrar:** el archivo `.github/workflows/ci.yml`, y —si el repo ya está en GitHub— la pestaña **Actions** con el workflow en verde y el **badge de CI** arriba del README.

**Qué decir (la idea central):**

Hasta acá todo lo probábamos a mano en nuestra máquina. El Paso 6 le delega ese trabajo a un servidor: **GitHub Actions**. Cada vez que alguien hace push o abre un Pull Request, el workflow `ci.yml` levanta una máquina limpia y corre **exactamente los mismos gates** que corremos localmente —ninguno reimplementado, son los mismos scripts—: primero el lint con ruff, después valida el catálogo contra el schema (y comprueba que un `.md` malformado a propósito sea **rechazado**), vectoriza el catálogo con el modelo ONNX, corre los tests de Python (los unitarios del Paso 2 y la regresión semántica del Paso 5), chequea la estructura del sitio, y termina con los tests de JavaScript: las funciones puras y —la joya— el **gate de equivalencia Python↔JS**. Ese es el sentido profundo de la Integración Continua: *lo que valida tu máquina es exactamente lo que valida el servidor*. Nadie puede mergear algo que rompa una búsqueda o desincronice la vectorización del navegador, porque el pipeline lo frena antes.

El orden de los pasos no es decorativo, refleja las dependencias reales: no se puede correr la regresión semántica sin antes haber bajado el modelo y vectorizado el catálogo. El modelo pesa ~23 MB, así que lo **cacheamos** entre corridas para no re-descargarlo cada vez. Y una honestidad de ingeniería que conviene anticipar: el gate de equivalencia baja el modelo de un CDN público, así que el CI necesita red —si ese servicio se cayera, el job falla, y eso queda documentado como una dependencia conocida—.

Una aclaración de alcance: el Paso 6 es **Integración Continua** (CI), todavía no Entrega Continua. La parte de **CD** —desplegar el sitio a GitHub Pages y resolver dónde vive el modelo en producción— la dejamos para el cierre del proyecto, para mostrarla toda junta y bien. Lo que ya queda blindado es lo más importante: ningún cambio entra a la rama principal sin pasar, automáticamente y en cada push, por la misma batería de pruebas que usamos los humanos.
