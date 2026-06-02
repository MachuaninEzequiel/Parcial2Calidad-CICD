# 🎮 Buscador Semántico de Videojuegos

> Catálogo de videojuegos en Markdown que se vectoriza con un modelo de IA dentro del pipeline de CI y se busca por **significado** —no por palabras clave— 100% en el navegador.

Escribís *"juego para jugar con amigos en el sillón"* y te devuelve **Overcooked 2**, aunque esa frase no aparezca escrita en ningún lado. Eso son **embeddings**: representar texto como vectores numéricos y comparar por cercanía semántica.

> Este proyecto sigue **Spec Driven Development**: los archivos `schemas/` y `specs/` son la **fuente de verdad**, y el código y los tests se derivan de ellos.

---

## ¿Cómo funciona? (flujo de punta a punta)

```
[Dev local]  edita un .md de un juego  ──git push──▶  [GitHub repo]
                                                            │ trigger
                                                            ▼
                                              [GitHub Actions = servidor de CI]
   1. Valida el schema (SDD)   check-jsonschema sobre cada .md
   2. Lint & tests             ruff + pytest
   3. Vectoriza                model.onnx → embeddings.json
   4. Build                    empaqueta el sitio estático
                                                            │ deploy (si es main)
                                                            ▼
                                              [GitHub Pages = producción]
                                                            │
                                                            ▼
[Browser]  el MISMO model.onnx vectoriza tu query
           → similitud coseno contra embeddings.json → top 5 resultados
```

La pieza central: **el mismo `model.onnx` corre en dos lugares**. En el CI (con Python) vectoriza el catálogo entero; en el navegador (con JavaScript) vectoriza tu búsqueda. Mismo modelo → mismo espacio semántico → las comparaciones son válidas.

---

## Cómo se mapea a la consigna de CI/CD

| Bloque del esquema teórico | Implementación concreta |
|---|---|
| Control de versiones | GitHub (`main` + feature branches + PRs) |
| Servidor de Integración Continua | GitHub Actions |
| Entorno del dev con build local | Docker + script de vectorización local |
| Prueba automatizada | pytest (unitarios) + tests semánticos desde la spec |
| Build que despliega | Job de deploy en Actions → GitHub Pages |
| Entornos de entrega | GitHub Pages (producción) |
| Mecanismo de feedback | Status checks en PRs + badges + notificaciones de GitHub |

> **CI (Integración Continua):** cada push se integra, valida y prueba automáticamente.
> **CD (Entrega Continua):** si todo pasa, se despliega solo a producción.

---

## Spec Driven Development — las tres capas

- **Capa A · Schema estructural** (`schemas/game.schema.yaml`): define qué campos tiene un juego y qué valores son válidos (géneros, plataformas, longitudes). El CI rechaza cualquier `.md` que no lo cumpla.
- **Capa B · Expectativas de búsqueda** (`specs/search-expectations.yaml`): declara qué juegos deberían aparecer para ciertas queries. De acá salen tests de **regresión semántica**: si un juego nuevo degrada una búsqueda que antes andaba, el CI avisa.
- **Capa C · La spec como postura**: la lista de géneros vive **solo** en el schema; el frontend y los tests la consumen de ahí. Un campo nuevo se agrega primero al schema, después a los `.md`, después al frontend. Nunca al revés.

---

## Estado actual — Paso 1 ✅

Ya está la **base SDD**: schema, expectativas, catálogo inicial (10 juegos) y el validador.

### Validar el catálogo localmente

```bash
# Instalar dependencias mínimas (pyyaml + jsonschema)
pip install -e .

# Validar que TODOS los juegos cumplen el schema
python scripts/validate_catalog.py

# Probar que el validador RECHAZA un .md malformado (test negativo)
python scripts/validate_catalog.py --expect-fail tests/fixtures/invalid-game.md
```

El primer comando termina en verde (exit 0). El segundo **también** termina en verde, porque el archivo malo es rechazado tal como se espera.

---

## Estructura del repo (hasta el Paso 1)

```
.
├── schemas/
│   └── game.schema.yaml          # SDD Capa A · fuente de verdad estructural
├── specs/
│   └── search-expectations.yaml  # SDD Capa B · expectativas de búsqueda
├── catalog/                      # un .md por juego (frontmatter + sinopsis)
│   ├── hollow-knight.md
│   └── ...                       # 10 juegos
├── scripts/
│   └── validate_catalog.py       # valida cada .md contra el schema
├── tests/
│   └── fixtures/
│       └── invalid-game.md       # .md malformado para el test negativo
├── pyproject.toml                # dependencias + config de ruff
└── README.md
```

> **Próximos pasos:** vectorización con ONNX (Paso 2), frontend (Pasos 3-4), tests semánticos (Paso 5), GitHub Actions (Paso 6), Docker (Paso 7) y la presentación oral (Paso 8).
