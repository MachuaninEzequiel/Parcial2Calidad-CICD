---
schema_version: 1
doc_type: spec
title: CD a GitHub Pages (cierre CI/CD)
created_at: '2026-06-02T22:47:51.429178Z'
updated_at: '2026-06-02T22:47:51.429178Z'
tags:
- spec
- spec
- sdd
- ci-cd
- cd
- github-pages
- deploy
- actions
- gitignore
- badge
- cierre
status: draft
links: []
vault_scope: local
fingerprint: f6f716fc5e2fab2a0ea4c90e53897dc064f7f53d293de362ef715d4f752c8e2f
verification_hooks:
- name: cd-yaml-valid
  command: python -c "import yaml;w=yaml.safe_load(open('.github/workflows/ci.yml',encoding='utf-8'));j=w['jobs'];assert
    'ci' in j and 'deploy' in j;assert 'ci' in str(j['deploy'].get('needs'));assert
    'deploy-pages' in open('.github/workflows/ci.yml',encoding='utf-8').read();print('ci+deploy(Pages)
    OK')"
  required: true
  success_criteria: exit code 0 — ci.yml válido con los jobs 'ci' y 'deploy' (deploy
    needs ci) y usa actions/deploy-pages.
  timeout_seconds: 60
- name: gitignore-models
  command: python -c "lines=[l.strip() for l in open('.gitignore',encoding='utf-8').read().splitlines()];assert
    'models/' in lines, 'falta models/ en .gitignore';print('gitignore ignora models/
    entero')"
  required: true
  success_criteria: exit code 0 — .gitignore ignora el directorio models/ completo
    (no solo *.onnx).
  timeout_seconds: 60
- name: badge-real
  command: python -c "s=open('README.md',encoding='utf-8').read();assert 'OWNER/REPO'
    not in s;assert 'MachuaninEzequiel/Parcial2Calidad-CICD' in s;print('badge real
    OK')"
  required: true
  success_criteria: exit code 0 — el README ya no tiene el placeholder OWNER/REPO
    y referencia el repo real.
  timeout_seconds: 60
goal: 'Cerrar el ciclo CI/CD del proyecto implementando la Entrega Continua (CD) a
  GitHub Pages, más dos arreglos de cierre. (1) Agregar un job `deploy` a .github/workflows/ci.yml
  que, SOLO en push a main y DESPUÉS de que el job `ci` pase (needs: ci), construye
  el artefacto del sitio (site/ + dist/embeddings.json) y lo publica en GitHub Pages
  con actions/deploy-pages. (2) Arreglar .gitignore para ignorar models/ entero (hoy
  ignora solo models/*.onnx, así que models/tokenizer.json ~711KB se versionaría).
  (3) Reemplazar el placeholder OWNER/REPO del badge de CI en el README por el path
  real MachuaninEzequiel/Parcial2Calidad-CICD. El modelo en producción lo baja el
  navegador del HF CDN (Transformers.js) — cero hosting extra. La ruta de embeddings.json
  en prod se resuelve SIN tocar app.mjs: el artefacto preserva site/+dist/ y un index.html
  raíz redirige a ./site/, así `../dist/embeddings.json` resuelve igual en Pages y
  en el preview local. Cierra el CI/CD que se venía difiriendo (Pasos 6-7 eran solo
  CI y Docker). Español rioplatense, didáctico, para la defensa oral.'
files_in_scope:
- .github/workflows/ci.yml
- .gitignore
- README.md
- PRESENTACION.md
constraints:
- 'El job `ci` existente NO se rompe ni se reescribe: el `deploy` se AGREGA como job
  aparte (needs: ci, if main). El CI sigue corriendo en push + PR como hasta ahora.'
- 'Modelo en producción = HF CDN (Transformers.js lo baja en el browser). NO hostear
  el modelo en Pages: el artefacto lleva SOLO site/ + dist/embeddings.json. Documentarlo.'
- 'Resolver la ruta de embeddings.json en prod SIN tocar site/js/app.mjs: el artefacto
  preserva site/+dist/ y un index.html raíz redirige a ./site/, así `../dist/embeddings.json`
  resuelve igual en Pages (OWNER.github.io/REPO/site/ → OWNER.github.io/REPO/dist/embeddings.json)
  y en el preview local. app.mjs NO se modifica.'
- 'OWNER/REPO = MachuaninEzequiel/Parcial2Calidad-CICD (confirmado por el usuario;
  el repo ya está en GitHub y commiteado). URL pública: https://machuaninezequiel.github.io/Parcial2Calidad-CICD/.'
- 'NO commitear nada pesado: con .gitignore = `models/`, ni el .onnx ni el tokenizer.json
  se trackean; dist/ y node_modules/ siguen gitignored. El deploy regenera embeddings.json
  en el runner.'
- 'Limitación: GitHub Pages debe habilitarse UNA vez en Settings → Pages → Source
  = ''GitHub Actions'' (paso manual del usuario, fuera del YAML). Un workflow de Actions
  no se corre localmente: la validación efectiva del deploy ocurre al pushear a main.
  El Paso entrega el YAML correcto + valida estructura/sintaxis localmente.'
- 'Avanzar paso a paso: al terminar, pausar y esperar confirmación. Cerrar con /cortex-documenter.'
- Español rioplatense (voseo) en las docs, didáctico, para la defensa oral de 5 min.
acceptance_criteria:
- '.github/workflows/ci.yml es YAML válido y define DOS jobs: `ci` (intacto, on push+PR)
  y `deploy` (needs: ci, if main, permisos pages:write+id-token:write, environment
  github-pages) que ensambla el artefacto y publica con actions/deploy-pages.'
- El job deploy arma un `_site/` que preserva site/ + dist/embeddings.json + un index.html
  raíz que redirige a ./site/ (+ .nojekyll), de modo que `../dist/embeddings.json`
  resuelve en producción. app.mjs NO fue modificado.
- .gitignore ignora `models/` entero (ya no aparece `models/*.onnx`; tokenizer.json
  deja de trackearse).
- El badge del README apunta a github.com/MachuaninEzequiel/Parcial2Calidad-CICD (sin
  el placeholder OWNER/REPO); la tabla de mapeo marca el CD a Pages como implementado;
  el README documenta la URL pública y el hosting del modelo vía HF CDN.
- PRESENTACION tiene el fragmento de cierre (CD).
- Los comandos del job deploy reusan los scripts reales del repo (download_model.py,
  vectorize.py) y actions pineadas a major version.
---

## Goal

Cerrar el ciclo CI/CD del proyecto implementando la Entrega Continua (CD) a GitHub Pages, más dos arreglos de cierre. (1) Agregar un job `deploy` a .github/workflows/ci.yml que, SOLO en push a main y DESPUÉS de que el job `ci` pase (needs: ci), construye el artefacto del sitio (site/ + dist/embeddings.json) y lo publica en GitHub Pages con actions/deploy-pages. (2) Arreglar .gitignore para ignorar models/ entero (hoy ignora solo models/*.onnx, así que models/tokenizer.json ~711KB se versionaría). (3) Reemplazar el placeholder OWNER/REPO del badge de CI en el README por el path real MachuaninEzequiel/Parcial2Calidad-CICD. El modelo en producción lo baja el navegador del HF CDN (Transformers.js) — cero hosting extra. La ruta de embeddings.json en prod se resuelve SIN tocar app.mjs: el artefacto preserva site/+dist/ y un index.html raíz redirige a ./site/, así `../dist/embeddings.json` resuelve igual en Pages y en el preview local. Cierra el CI/CD que se venía difiriendo (Pasos 6-7 eran solo CI y Docker). Español rioplatense, didáctico, para la defensa oral.

## Requirements

- .github/workflows/ci.yml (EDITAR): agregar un job `deploy` ADEMÁS del job `ci` (que queda INTACTO). El job deploy: `needs: ci`, `if: github.ref == 'refs/heads/main'`, `runs-on: ubuntu-latest`, `permissions: pages: write + id-token: write` (y contents: read para el checkout), `environment: { name: github-pages, url: ${{ steps.deployment.outputs.page_url }} }`. Pasos: actions/checkout@v4 → actions/setup-python@v5 (cache pip) → `pip install -e .` (solo runtime deps; vectorize no necesita dev) → actions/cache@v4 de ~/.cache/huggingface → `python scripts/download_model.py` → `python scripts/vectorize.py` (genera dist/embeddings.json) → ensamblar el artefacto `_site/`: `mkdir -p _site/dist && cp -r site _site/site && cp dist/embeddings.json _site/dist/embeddings.json`, escribir `_site/index.html` con un redirect (meta refresh) a `./site/` y un `_site/.nojekyll` vacío → actions/configure-pages@v5 → actions/upload-pages-artifact@v3 (path: _site) → actions/deploy-pages@v4 (id: deployment). Actions pineadas a major. NO romper el job ci (sigue on push + PR).
- .gitignore (EDITAR): cambiar la línea `models/*.onnx` por `models/` (ignorar el directorio entero, así tokenizer.json tampoco se trackea). Conservar el comentario explicativo y el resto del archivo.
- README.md (EDITAR): reemplazar las DOS ocurrencias de `OWNER/REPO` del badge por `MachuaninEzequiel/Parcial2Calidad-CICD`. Tabla de mapeo: marcar 'Build que despliega' y 'Entornos de entrega' como GitHub Pages ✅ (CD implementado). Estado actual: reflejar que el CD a Pages ya está. Documentar la URL pública https://machuaninezequiel.github.io/Parcial2Calidad-CICD/ (con el redirect cae en /site/) y que en prod el modelo lo baja el navegador del HF CDN (el catálogo y 'similares' andan con el embeddings.json del artefacto; la búsqueda por texto libre necesita el CDN). Nota: habilitar Pages una vez en Settings → Pages → Source = GitHub Actions.
- PRESENTACION.md (EDITAR/append): fragmento de cierre — la Entrega Continua (CD): push a main → CI verde → deploy automático a GitHub Pages, el sitio público andando, el modelo del CDN, y el ciclo CI/CD completo de la consigna cerrado (build local con Docker + CI con Actions + CD a Pages). Voseo rioplatense.

## Files in Scope

- `.github/workflows/ci.yml`
- `.gitignore`
- `README.md`
- `PRESENTACION.md`

## Constraints

- El job `ci` existente NO se rompe ni se reescribe: el `deploy` se AGREGA como job aparte (needs: ci, if main). El CI sigue corriendo en push + PR como hasta ahora.
- Modelo en producción = HF CDN (Transformers.js lo baja en el browser). NO hostear el modelo en Pages: el artefacto lleva SOLO site/ + dist/embeddings.json. Documentarlo.
- Resolver la ruta de embeddings.json en prod SIN tocar site/js/app.mjs: el artefacto preserva site/+dist/ y un index.html raíz redirige a ./site/, así `../dist/embeddings.json` resuelve igual en Pages (OWNER.github.io/REPO/site/ → OWNER.github.io/REPO/dist/embeddings.json) y en el preview local. app.mjs NO se modifica.
- OWNER/REPO = MachuaninEzequiel/Parcial2Calidad-CICD (confirmado por el usuario; el repo ya está en GitHub y commiteado). URL pública: https://machuaninezequiel.github.io/Parcial2Calidad-CICD/.
- NO commitear nada pesado: con .gitignore = `models/`, ni el .onnx ni el tokenizer.json se trackean; dist/ y node_modules/ siguen gitignored. El deploy regenera embeddings.json en el runner.
- Limitación: GitHub Pages debe habilitarse UNA vez en Settings → Pages → Source = 'GitHub Actions' (paso manual del usuario, fuera del YAML). Un workflow de Actions no se corre localmente: la validación efectiva del deploy ocurre al pushear a main. El Paso entrega el YAML correcto + valida estructura/sintaxis localmente.
- Avanzar paso a paso: al terminar, pausar y esperar confirmación. Cerrar con /cortex-documenter.
- Español rioplatense (voseo) en las docs, didáctico, para la defensa oral de 5 min.

## Acceptance Criteria

- [ ] .github/workflows/ci.yml es YAML válido y define DOS jobs: `ci` (intacto, on push+PR) y `deploy` (needs: ci, if main, permisos pages:write+id-token:write, environment github-pages) que ensambla el artefacto y publica con actions/deploy-pages.
- [ ] El job deploy arma un `_site/` que preserva site/ + dist/embeddings.json + un index.html raíz que redirige a ./site/ (+ .nojekyll), de modo que `../dist/embeddings.json` resuelve en producción. app.mjs NO fue modificado.
- [ ] .gitignore ignora `models/` entero (ya no aparece `models/*.onnx`; tokenizer.json deja de trackearse).
- [ ] El badge del README apunta a github.com/MachuaninEzequiel/Parcial2Calidad-CICD (sin el placeholder OWNER/REPO); la tabla de mapeo marca el CD a Pages como implementado; el README documenta la URL pública y el hosting del modelo vía HF CDN.
- [ ] PRESENTACION tiene el fragmento de cierre (CD).
- [ ] Los comandos del job deploy reusan los scripts reales del repo (download_model.py, vectorize.py) y actions pineadas a major version.

## Verification Hooks

Commands that objectively prove the work is done. Run by
`cortex finish-session` (Pluggable Middle, Phase 01).

### cd-yaml-valid
```bash
python -c "import yaml;w=yaml.safe_load(open('.github/workflows/ci.yml',encoding='utf-8'));j=w['jobs'];assert 'ci' in j and 'deploy' in j;assert 'ci' in str(j['deploy'].get('needs'));assert 'deploy-pages' in open('.github/workflows/ci.yml',encoding='utf-8').read();print('ci+deploy(Pages) OK')"
```

Success: exit code 0 — ci.yml válido con los jobs 'ci' y 'deploy' (deploy needs ci) y usa actions/deploy-pages. · Timeout: 60s
### gitignore-models
```bash
python -c "lines=[l.strip() for l in open('.gitignore',encoding='utf-8').read().splitlines()];assert 'models/' in lines, 'falta models/ en .gitignore';print('gitignore ignora models/ entero')"
```

Success: exit code 0 — .gitignore ignora el directorio models/ completo (no solo *.onnx). · Timeout: 60s
### badge-real
```bash
python -c "s=open('README.md',encoding='utf-8').read();assert 'OWNER/REPO' not in s;assert 'MachuaninEzequiel/Parcial2Calidad-CICD' in s;print('badge real OK')"
```

Success: exit code 0 — el README ya no tiene el placeholder OWNER/REPO y referencia el repo real. · Timeout: 60s
