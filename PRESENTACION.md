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
