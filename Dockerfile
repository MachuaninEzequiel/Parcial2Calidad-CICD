# Entorno de build/dev reproducible (Paso 7) — la fila "Entorno del dev con
# build local" de la consigna de CI/CD. Esta imagen tiene Python + Node + todas
# las dependencias para correr el MISMO pipeline que GitHub Actions (.github/
# workflows/ci.yml) dentro de un contenedor, sin instalar nada en la máquina.
#
# Uso (ver README, sección "Correr todo en Docker"):
#   docker build -t buscador-semantico .
#   docker run --rm buscador-semantico                 # pipeline completo (= CI)
#   docker run --rm -p 8000:8000 buscador-semantico serve   # sitio en :8000
#
# NO es el deploy/CD: servir es solo para la demo local. El hosting del modelo
# en producción y el deploy a GitHub Pages se resuelven al cierre del proyecto.

FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HUB_DISABLE_SYMLINKS_WARNING=1

# Node 22 (NodeSource). curl/gnupg solo para instalarlo; limpiamos apt al final
# para que la imagen quede lo más chica razonable.
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl ca-certificates gnupg \
 && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
 && apt-get install -y --no-install-recommends nodejs \
 && apt-get purge -y --auto-remove gnupg \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1) Dependencias PRIMERO (capa cacheable): copiamos solo los manifiestos y
#    las instalamos. Mientras no cambien, Docker reusa esta capa entre builds.
COPY pyproject.toml README.md ./
COPY package.json package-lock.json ./
RUN pip install -e ".[dev]" \
 && npm ci

# 2) El resto del repo (catálogo, scripts, sitio, tests, schema, specs...).
COPY . .

# 3) Horneamos el modelo (~23 MB) y precomputamos los embeddings dentro de la
#    imagen: así `serve` anda out-of-the-box y el lado Python no depende de la
#    red en runtime. (El equivalence test de Node sí baja el modelo del CDN.)
RUN python scripts/download_model.py \
 && python scripts/vectorize.py \
 && chmod +x docker/entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["bash", "docker/entrypoint.sh"]
CMD ["ci"]
