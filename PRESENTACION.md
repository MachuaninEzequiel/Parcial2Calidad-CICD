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
