# Plan de réalisation — ePortfolio Backend

> Règle : une phase = implémenter → tester → déployer → valider. Jamais deux phases en parallèle.

---

## Phase 0 — Fondation locale + Infra

### Backend local
- [x] Python 3.13, `.python-version`, `uv init`
- [x] Ajouter dépendances (`fastapi`, `uvicorn[standard]`, `asyncpg`, `pydantic-settings`, `python-dotenv`)
- [x] Ajouter dépendances dev (`pytest`, `pytest-asyncio`, `httpx`, `ruff`) + `asyncio_mode = "auto"`
- [x] Structure `app/` : `main.py`, `config.py`, `database.py`, `routers/`, `models/`, `services/`
- [x] `app/config.py` — `Settings` pydantic-settings + `database_url`
- [x] `app/database.py` — pool asyncpg (`get_pool`, `close_pool`)
- [x] `app/main.py` — lifespan + FastAPI + health router
- [x] `app/routers/health.py` — `GET /health` avec ping DB
- [x] `tests/test_health.py`
- [x] `.env` (copie de `.env.example`), `.gitignore` vérifié
- [x] `docker-compose.yml` (postgres 16, redis 7, api)
- [x] `backend/Dockerfile`
- [x] `Makefile` (dev, stop, logs, db-shell, test, lint)
- [x] `make dev` → 3 services up, `GET /health` → 200, `make test` passe

### VPS + k3s
- [ ] Provisionner VPS Hetzner CX21 (Ubuntu 22.04)
- [ ] DNS : `A steeve.dev → IP VPS` + wildcard `*.steeve.dev`
- [ ] SSH non-root, `apt update && upgrade`
- [ ] Installer k3s : `curl -sfL https://get.k3s.io | sh -`
- [ ] Copier kubeconfig en local, `kubectl get nodes` → Ready
- [ ] Installer Nginx Ingress Controller + cert-manager via Helm
- [ ] `ClusterIssuer` Let's Encrypt staging puis production
- [ ] Valider HTTPS sur un pod de test

### CI/CD + premier déploiement
- [ ] PAT GitHub `write:packages` → secret `GHCR_TOKEN`
- [ ] Secrets GitHub : `HETZNER_SSH_KEY`, `KUBE_CONFIG`
- [ ] `.github/workflows/ci.yaml` : lint → test → build → push GHCR → `kubectl set image`
- [ ] Manifests k8s initiaux : Secrets, ConfigMap, Deployment API, Service, Ingress (`api.steeve.dev`)
- [ ] Manifests k8s : PostgreSQL (Deployment + Service + PVC 5Gi) + Redis (Deployment + Service + PVC 1Gi)
- [ ] `kubectl apply -f k8s/` → `GET https://api.steeve.dev/health` → 200

**✓ Phase 0 validée :** API live sur HTTPS, CI/CD déploie sur push `main`.

---

## Phase 1 — Projects API

- [ ] `migrations/002_projects.sql`
- [ ] `models/project.py` — `ProjectCreate`, `ProjectUpdate`, `ProjectResponse`
- [ ] `services/project_service.py` — `get_all` (paginé), `get_by_slug`, `create`, `update`, `delete`
- [ ] `routers/projects.py` — `GET /api/v1/projects`, `GET /api/v1/projects/{slug}`, `POST`, `PATCH`, `DELETE`
- [ ] `tests/test_projects.py` — happy path + 404
- [ ] `make test` passe → push → déploiement automatique
- [ ] Valider les endpoints sur `api.steeve.dev`

**✓ Phase 1 validée :** CRUD Projects live en production.

---

## Phase 2 — Profile API (singleton)

- [ ] `migrations/003_profile.sql` + seed de la ligne initiale
- [ ] `models/profile.py` — `ProfileUpdate`, `ProfileResponse`
- [ ] `services/profile_service.py` — `get`, `update`
- [ ] `routers/profile.py` — `GET /api/v1/profile` (public), `PATCH /api/v1/profile` (admin temporairement libre)
- [ ] `tests/test_profile.py`
- [ ] `make test` passe → push → déploiement

**✓ Phase 2 validée :** profil accessible et modifiable live.

---

## Phase 3 — Auth + Messages

- [ ] Ajouter `pyjwt` ou `python-jose[cryptography]`
- [ ] `services/auth_service.py` — `create_token`, `verify_token`, dépendance `require_admin`
- [ ] `routers/auth.py` — `POST /api/v1/auth/login` → JWT
- [ ] Protéger `PATCH /api/v1/profile` + tous les futurs endpoints admin
- [ ] `migrations/004_messages.sql`
- [ ] `models/message.py`, `services/message_service.py`
- [ ] `routers/messages.py` — `POST /api/v1/messages` (public), `GET` + `PATCH /{id}/read` (admin)
- [ ] `tests/test_auth.py` + `tests/test_messages.py`
- [ ] `make test` passe → push → déploiement
- [ ] Valider : login → JWT → accès admin, sans token → 401

**✓ Phase 3 validée :** auth JWT + formulaire de contact live.

---

## Phase 4 — ML Models

- [ ] `migrations/005_ml_models.sql` (FK `projects(id) ON DELETE CASCADE`)
- [ ] `models/ml_model.py`, `services/ml_model_service.py`
- [ ] `routers/ml_models.py` — `POST /api/v1/projects/{id}/models` (admin), `GET /api/v1/projects/{id}/models` (public), `PATCH /api/v1/models/{id}` (toggle `is_active`)
- [ ] `tests/test_ml_models.py` — cascade DELETE vérifié
- [ ] `make test` passe → push → déploiement

**✓ Phase 4 validée :** ML Models CRUD live, cascade FK vérifiée.

---

## Phase 5 — Experience, Certifications, Learning

- [ ] `migrations/006_experience.sql` — tables `experience`, `certifications`, `learning_items`
- [ ] Modèles, services, routers pour chaque ressource (CRUD complet)
- [ ] `tests/test_experience.py`, `test_certifications.py`, `test_learning.py`
- [ ] `make test` passe → push → déploiement

**✓ Phase 5 validée :** 3 nouvelles ressources CRUD live.

---

## Phase 6 — Skills + Analytics

- [ ] `migrations/007_skills_visitors.sql` + index `visitors(page)`, `visitors(visited_at DESC)`
- [ ] `models/skill.py`, `services/skill_service.py`
- [ ] `routers/skills.py` — `GET /api/v1/skills` (public), `POST/PATCH/DELETE` (admin)
- [ ] `routers/analytics.py` — `POST /api/v1/analytics/track` (public), `GET /api/v1/admin/analytics` (admin)
- [ ] `tests/test_skills.py` + `tests/test_analytics.py`
- [ ] `make test` passe → push → déploiement

**✓ Phase 6 validée :** skills + tracking de visites live.

---

## Phase 7 — Optimisation backend

- [ ] Logging structuré JSON avec `structlog`
- [ ] Exception handlers globaux FastAPI (404, 422, 500)
- [ ] Enrichir `GET /health` : uptime, version, pool stats
- [ ] Cache Redis sur les endpoints GET publics fréquents (`/profile`, `/skills`, `/projects`)
- [ ] Headers CORS pour le domaine frontend
- [ ] Rate limiting sur `POST /api/v1/messages` et `POST /api/v1/analytics/track`
- [ ] Revue SQL : index manquants, requêtes N+1
- [ ] HPA k8s sur l'API (1 → 5 pods) dans `k8s/hpa.yaml`
- [ ] Push → déploiement

**✓ Phase 7 validée :** `make lint` propre, cache Redis actif, rate limiting en place.

---

## Phase 8 — Monitoring

- [ ] Ajouter `prometheus-fastapi-instrumentator` → expose `/metrics`
- [ ] Déployer `kube-prometheus-stack` via Helm (Prometheus + Grafana)
- [ ] Ingress Grafana sur `grafana.steeve.dev`
- [ ] Dashboard Grafana : req/s, latence p95, erreurs 5xx, pool asyncpg
- [ ] Déployer Loki + Promtail (logs structurés JSON des pods)
- [ ] Datasource Loki dans Grafana + panel de logs
- [ ] Déployer Plausible CE — Ingress `analytics.steeve.dev`

**✓ Phase 8 validée :** métriques, logs et analytics visibles en temps réel.

---

## À planifier (après backend stable)

- **Frontend** — Next.js 14 (App Router) + Tailwind + D3.js + GSAP
- **Backend R** — Plumber (graphiques ggplot2) + Shiny (dashboards interactifs)
- **Tests E2E** — Playwright
- **SEO + performance** — Core Web Vitals, sitemap, Open Graph
