# CLAUDE.md — ePortfolio Data Scientist

> Instructions de développement pour Claude. Ce fichier définit le contexte du projet, les conventions, l'architecture de la base de données et le workflow à suivre impérativement.

---

## 🎯 Vue d'ensemble du projet

Portfolio full-stack d'un Data Scientist. Ce n'est pas un site vitrine statique — c'est une **plateforme de démonstration de compétences** avec des modèles ML déployés en live, des APIs REST, et une architecture microservices entièrement self-hosted sur Kubernetes.

### Stack principale

| Couche | Technologie | Notes |
|---|---|---|
| Frontend | Next.js 14 (App Router) + TypeScript + Tailwind CSS | SSR/SSG |
| Backend Python | FastAPI + uv | API principale + modèles ML |
| Backend R | Plumber + Shiny | Graphiques R + dashboards |
| Base de données | PostgreSQL 16 | Pod k8s + PersistentVolume |
| Cache | Redis 7 | Pod k8s + PersistentVolume |
| Conteneurs | Docker | Un Dockerfile par service |
| Orchestration | Kubernetes k3s | Sur Hetzner VPS (~5€/mois) |
| Ingress | Nginx Ingress Controller | SSL + routage |
| SSL | cert-manager + Let's Encrypt | HTTPS automatique |
| CI/CD | GitHub Actions | Push → test → build → deploy |
| Registry | GitHub Container Registry (GHCR) | Images Docker |
| Monitoring | Prometheus + Grafana + Loki | Métriques + logs |
| Analytics | Plausible (self-hosted) | Privacy-first |
| Auth | JWT maison via FastAPI | Pas de service externe |

### Principe d'architecture
Tout est **self-hosted sur k8s**. Pas de services managés externes. PostgreSQL et Redis tournent comme des pods Kubernetes avec des PersistentVolumes sur le VPS Hetzner.

---

## 🗄️ Schéma de base de données

### Conventions globales
- Toutes les PK sont de type `uuid` générées par `gen_random_uuid()`
- Les champs narratifs longs sont stockés en **Markdown** (`text`) — le frontend Next.js convertit en HTML via `react-markdown`
- `jsonb` uniquement quand la structure de données varie selon les lignes
- `text[]` pour les tableaux de valeurs simples (tags, catégories)
- Les champs `display_order` (`int`) contrôlent l'ordre d'affichage sans modifier le code
- Les migrations sont des **fichiers SQL numérotés** dans `backend/migrations/` — jamais de modification rétroactive

---

### Table 1 — `profile` (singleton)

> Section §1 Identity Layer + §12 Personality + §14 Contact
> **Une seule ligne.** Toujours requêtée avec `LIMIT 1`

```sql
CREATE TABLE profile (
  lock                 boolean PRIMARY KEY DEFAULT true CHECK (lock = true),
  name                 text NOT NULL,
  title                text NOT NULL,
  tagline              text,
  availability_status  text,
  is_open_to_work      boolean DEFAULT false,
  location             text,
  email                text,
  github_url           text,
  linkedin_url         text,
  calendly_url         text,
  social_links         jsonb,
  ethics_statement     text,
  communication_style  text,
  work_preference      text,
  fun_fact             text,
  updated_at           timestamp DEFAULT now()
);
```

**Notes**
- `lock = true` + `CHECK (lock = true)` + `PRIMARY KEY` → impossible d'insérer une seconde ligne
- `social_links` (jsonb) : ex. `{"twitter": "...", "kaggle": "...", "huggingface": "..."}`
- `ethics_statement`, `communication_style`, `work_preference`, `fun_fact` couvrent la §12
- Depuis FastAPI : `SELECT * FROM profile LIMIT 1`

---

### Table 2 — `skills`

> Section §4 Skills & Expertise — bubble chart D3.js

```sql
CREATE TABLE skills (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name          text NOT NULL,
  category      text NOT NULL,
  cluster       text NOT NULL,
  icon_devicon  text,
  mastery_level int CHECK (mastery_level BETWEEN 1 AND 5),
  featured      boolean DEFAULT false,
  display_order int DEFAULT 0
);
```

**Notes**
- `cluster` : `'Data & Analytics'` | `'Machine Learning / AI'` | `'Infrastructure'` | `'Soft Skills'`
- `mastery_level` (1–5) : taille des bulles dans le D3.js bubble chart
- `icon_devicon` : ex. `"devicon-python-plain"`

---

### Table 3 — `projects`

> Section §5 Work / Projects ⭐ — table la plus importante du schéma

```sql
CREATE TABLE projects (
  id                 uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  slug               text UNIQUE NOT NULL,
  title              text NOT NULL,
  problem_statement  text,
  methodology        text,
  results_impact     text,
  metrics            jsonb,
  tech_stack         text[],
  categories         text[],
  github_url         text,
  demo_url           text,
  notebook_url       text,
  thumbnail_url      text,
  has_ml_demo        boolean DEFAULT false,
  ml_endpoint        text,
  featured           boolean DEFAULT false,
  display_order      int DEFAULT 0,
  created_at         timestamp DEFAULT now()
);
```

**Notes**
- `problem_statement`, `methodology`, `results_impact` : stockés en **Markdown**
- `metrics` (jsonb) : ex. `{"accuracy": 0.94, "f1_score": 0.91, "latency_ms": 120}`
- `categories` : `'NLP'` | `'Computer Vision'` | `'Time Series'` | `'Regression'` | `'MLOps'`
- `slug` : identifiant URL ex. `"sentiment-analysis-api"` → `/projects/sentiment-analysis-api`

---

### Table 4 — `experience`

> Section §7 Experience & Education — timeline GSAP

```sql
CREATE TABLE experience (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  type          text NOT NULL CHECK (type IN ('job', 'education')),
  company       text NOT NULL,
  role          text NOT NULL,
  description   text,
  impact_metric text,
  start_date    date NOT NULL,
  end_date      date,
  is_current    boolean DEFAULT false,
  logo_url      text,
  display_order int DEFAULT 0
);
```

**Notes**
- `type` : `'job'` | `'education'` — une seule table, une seule timeline GSAP
- `impact_metric` : métrique clé par poste ex. `"+23% de performance"`, `"50k utilisateurs"`
- `description` : stocké en **Markdown**

---

### Table 5 — `certifications`

> Section §7 — séparée d'`experience` (badge, émetteur, lien de vérification)

```sql
CREATE TABLE certifications (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name       text NOT NULL,
  issuer     text NOT NULL,
  url        text,
  issued_at  date,
  badge_url  text
);
```

---

### Table 6 — `learning_items`

> Section §11 Learning & Growth — table polymorphe

```sql
CREATE TABLE learning_items (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  type          text NOT NULL CHECK (type IN ('paper', 'course', 'competition', 'current')),
  title         text NOT NULL,
  source        text,
  url           text,
  progress_pct  int CHECK (progress_pct BETWEEN 0 AND 100),
  is_current    boolean DEFAULT false,
  status        text,
  started_at    date
);
```

**Notes**
- `type = 'paper'` : papers arXiv | `'course'` : Coursera, Udemy | `'competition'` : Kaggle | `'current'` : badge live
- `is_current = true` : badge live affiché en haut de la section §11

---

### Table 7 — `ml_models`

> Démos ML interactives — **seule FK réelle du schéma**

```sql
CREATE TABLE ml_models (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id   uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  name         text NOT NULL,
  endpoint     text NOT NULL,
  framework    text,
  description  text,
  accuracy     float,
  metrics      jsonb,
  is_active    boolean DEFAULT true,
  deployed_at  timestamp DEFAULT now()
);
```

**Notes**
- `project_id` → FK vers `projects.id` — 1 projet peut avoir N modèles (v1, v2…)
- `accuracy` : colonne dédiée (pas dans jsonb) — affichée directement sur la carte projet
- `is_active = false` : désactiver une démo sans supprimer la ligne
- `ON DELETE CASCADE` : suppression du projet → suppression des modèles associés

---

### Table 8 — `messages`

> Section §14 Contact — table autonome, aucune relation

```sql
CREATE TABLE messages (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name          text NOT NULL,
  email         text NOT NULL,
  project_type  text,
  message       text NOT NULL,
  is_read       boolean DEFAULT false,
  created_at    timestamp DEFAULT now()
);
```

**Notes**
- `project_type` : `'hiring'` | `'freelance'` | `'collaboration'`
- Aucune FK, aucune jointure

---

### Table 9 — `visitors`

> Analytics admin

```sql
CREATE TABLE visitors (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  page        text,
  referrer    text,
  country     text,
  city        text,
  device      text,
  browser     text,
  duration_s  int,
  visited_at  timestamp DEFAULT now()
);

CREATE INDEX idx_visitors_page       ON visitors(page);
CREATE INDEX idx_visitors_visited_at ON visitors(visited_at DESC);
```

**Notes**
- `POST /api/v1/analytics/track` (public) → alimente la table
- `GET /api/v1/admin/analytics` (JWT requis) → lit la table

---

## 🔗 Relations entre tables

| De | Vers | Cardinalité | Implémentation |
|---|---|---|---|
| `ml_models` | `projects` | N → 1 | FK réelle `project_id REFERENCES projects(id) ON DELETE CASCADE` |
| `profile` | toutes | conceptuelle | Singleton — pas de FK nécessaire |
| `messages` | — | aucune | Table autonome |
| `visitors` | — | aucune | Table autonome |

---

## 📏 Conventions de code

### Nommage Python / FastAPI

- Modèles Pydantic : `{Resource}Create`, `{Resource}Update`, `{Resource}Response` (ex. `ProjectCreate`, `ProjectResponse`)
- Routers : un fichier par ressource dans `routers/` — nom = nom de table (ex. `routers/projects.py`)
- Services : un fichier par ressource dans `services/` (ex. `services/project_service.py`)
- Toutes les fonctions I/O sont `async`

### Réponses API

- Succès GET/PATCH : objet direct — pas d'enveloppe `{"data": ...}`
- Listes paginées : `{"items": [...], "total": N, "page": N, "size": N}`
- Erreurs : format FastAPI standard `{"detail": "message"}`
- Codes HTTP : `200` (GET/PATCH), `201` (POST), `204` (DELETE), `404` (non trouvé), `422` (validation), `401`/`403` (auth)

### Base de données

- Toutes les requêtes passent par `asyncpg` directement — pas d'ORM
- Pool acquis via `pool.acquire()` en context manager
- Les UUIDs sont retournés comme `str` dans les réponses (sérialisation Pydantic)

### Pagination

Paramètres standards pour tous les endpoints de liste :
- `page: int = 1` (base 1), `size: int = 20` (max 100)

### Identifiants dans les URLs

- Ressources avec slug → **slug** (ex. `/projects/{slug}`)
- Ressources sans slug → **UUID** (ex. `/models/{id}`)

---

## 🔄 Workflow Git

### Branches

- `main` : branche stable, déployée en production
- `feat/<nom>` : nouvelle feature (ex. `feat/projects-api`)
- `fix/<nom>` : correction de bug (ex. `fix/health-check-timeout`)

### Commits

Format : `type: description courte`

| Préfixe | Usage |
|---|---|
| `feat:` | nouvelle fonctionnalité |
| `fix:` | correction de bug |
| `chore:` | maintenance (deps, config) |
| `test:` | ajout/modification de tests |
| `docs:` | documentation uniquement |

Un commit par tâche du workflow (ex. `feat: 0.3 — dépendances uv ajoutées`).

### Secrets CI/CD (GitHub Actions)

Les secrets sont définis dans **GitHub → Settings → Secrets and variables → Actions** :

| Secret | Contenu |
|---|---|
| `GHCR_TOKEN` | Personal Access Token pour pousser sur GHCR |
| `HETZNER_SSH_KEY` | Clé SSH privée pour le VPS |
| `KUBE_CONFIG` | kubeconfig du cluster k3s encodé en base64 |

Les variables d'env sensibles de l'app (mot de passe DB, JWT secret) vivent dans des **Kubernetes Secrets** — pas directement dans GitHub Actions.

---

## 🧪 Stratégie de tests

- **Tests d'intégration uniquement** — pas de mocks de la DB
- Chaque router a son fichier test : `tests/test_{resource}.py`
- Les tests utilisent une base PostgreSQL dédiée (`portfolio_test`) lancée via Docker Compose
- `make test` doit passer avant tout commit

Configuration `pyproject.toml` :
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

---

## 🗺️ Workflow de développement

### Règle absolue
**Ne jamais sauter de phase. Ne jamais implémenter plusieurs features à la fois.**

Chaque tâche suit ce cycle sans exception :
1. Implémenter la version minimale
2. Tester en local
3. Déployer
4. Valider
5. Passer à la tâche suivante

---

## Phase 0 — Setup (FONDATION)

**Objectif :** environnement de développement complet et backend minimal fonctionnel en local et dans Docker.

---

### 0.1 — Prérequis système

Outils à installer sur la machine de développement :

| Outil | Version cible | Commande d'installation |
|---|---|---|
| Python | 3.13+ | `pyenv install 3.13` |
| uv | latest | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Docker | latest | Docker Desktop (Mac/Win) — Docker Engine (Linux) |
| kubectl | latest | `brew install kubectl` (Mac) / `snap install kubectl --classic` (Linux) |
| Git | 2.40+ | `brew install git` (Mac) / `sudo apt install git` (Linux) |
| make | — | `brew install make` (Mac) / `sudo apt install make` (Linux) |

> **Linux (Debian/Ubuntu) :** `pyenv` recommandé pour gérer Python — `curl https://pyenv.run | bash`. Docker → installer Docker Engine via `apt`, pas Docker Desktop.

Vérification :
```bash
python --version   # 3.13+
uv --version       # 0.x.x
docker --version   # 24+
kubectl version    # client only en local
git --version      # 2.40+
```

---

### 0.2 — Structure du repo

```
eportfolio/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # Point d'entrée FastAPI
│   │   ├── config.py           # Settings via pydantic-settings
│   │   ├── database.py         # Pool asyncpg
│   │   ├── routers/
│   │   │   └── health.py
│   │   ├── models/             # Schémas Pydantic
│   │   └── services/           # Logique métier
│   ├── migrations/
│   │   └── 001_init.sql        # Tables de base
│   ├── tests/
│   │   └── test_health.py
│   ├── pyproject.toml
│   ├── uv.lock                 # Toujours commité
│   ├── Dockerfile
│   └── .env.example
├── k8s/                        # Manifests Kubernetes (Phase 8)
├── .github/
│   └── workflows/
│       └── ci.yaml             # GitHub Actions (Phase 1)
├── .env                        # Jamais commité
├── .gitignore
├── docker-compose.yml
├── Makefile
└── CLAUDE.md
```

---

### 0.3 — Initialisation uv

```bash
mkdir -p eportfolio/backend && cd eportfolio/backend
uv init --python 3.13

# Dépendances Phase 0
uv add fastapi uvicorn[standard] asyncpg pydantic-settings python-dotenv

# Dépendances de développement
uv add --dev pytest pytest-asyncio httpx ruff
```

`pyproject.toml` résultant :

```toml
[project]
name = "portfolio-api"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [
    "fastapi>=0.110.0",
    "uvicorn[standard]>=0.29.0",
    "asyncpg>=0.29.0",
    "pydantic-settings>=2.2.0",
    "python-dotenv>=1.0.0",
]

[tool.uv]
dev-dependencies = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "httpx>=0.27.0",
    "ruff>=0.4.0",
]

[tool.ruff]
line-length = 88
select = ["E", "F", "I"]
```

---

### 0.4 — Variables d'environnement

`.env.example` :
```env
# Application
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=true

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=portfolio
POSTGRES_USER=portfolio_user
POSTGRES_PASSWORD=portfolio_pass

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Auth JWT (Phase 3)
JWT_SECRET=changeme_in_production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440
ADMIN_EMAIL=ton@email.com
ADMIN_PASSWORD=changeme_in_production
```

`backend/app/config.py` :
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = False

    postgres_host: str
    postgres_port: int = 5432
    postgres_db: str
    postgres_user: str
    postgres_password: str

    redis_host: str = "localhost"
    redis_port: int = 6379

    jwt_secret: str = "changeme"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440
    admin_email: str = ""
    admin_password: str = ""

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    class Config:
        env_file = ".env"

settings = Settings()
```

---

### 0.5 — Connexion PostgreSQL (asyncpg)

`backend/app/database.py` :
```python
import asyncpg
from app.config import settings

_pool: asyncpg.Pool | None = None

async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            dsn=settings.database_url,
            min_size=2,
            max_size=10,
        )
    return _pool

async def close_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
```

---

### 0.6 — Application FastAPI minimale

`backend/app/main.py` :
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import get_pool, close_pool
from app.routers import health

@asynccontextmanager
async def lifespan(app: FastAPI):
    await get_pool()
    yield
    await close_pool()

app = FastAPI(
    title="Portfolio API",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health.router)
```

`backend/app/routers/health.py` :
```python
from fastapi import APIRouter
from app.database import get_pool

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check():
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.fetchval("SELECT 1")
    return {"status": "ok", "database": "connected"}
```

---

### 0.7 — Docker Compose (dev local)

`docker-compose.yml` :
```yaml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: portfolio
      POSTGRES_USER: portfolio_user
      POSTGRES_PASSWORD: portfolio_pass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend/migrations:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U portfolio_user -d portfolio"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  api:
    build: ./backend
    ports:
      - "8000:8000"
    env_file: .env
    environment:
      POSTGRES_HOST: db
      REDIS_HOST: redis
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./backend:/app
    command: uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

volumes:
  postgres_data:
  redis_data:
```

---

### 0.8 — Dockerfile backend

`backend/Dockerfile` :
```dockerfile
FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY app/ ./app/

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

### 0.9 — Makefile

`Makefile` :
```makefile
.PHONY: dev stop logs db-shell test lint

dev:
	docker compose up --build

stop:
	docker compose down

logs:
	docker compose logs -f api

db-shell:
	docker compose exec db psql -U portfolio_user -d portfolio

test:
	cd backend && uv run pytest tests/ -v

lint:
	cd backend && uv run ruff check app/
```

---

### 0.10 — Validation Phase 0

```bash
# 1. Lancer les services
make dev

# 2. Tester le health check
curl http://localhost:8000/health
# Attendu : {"status": "ok", "database": "connected"}

# 3. Vérifier la doc Swagger
open http://localhost:8000/docs

# 4. Vérifier la DB
make db-shell
# \dt → zéro table pour l'instant, connexion OK

# 5. Tests
make test
# Attendu : 1 passed
```

**Phase 0 validée quand :**
- `GET /health` → `{"status": "ok", "database": "connected"}`
- Swagger accessible sur `/docs`
- `make test` passe
- Docker Compose lance les 3 services sans erreur

---

## Phase 1 — Projects (FEATURE PRINCIPALE)

**Objectif :** première feature end-to-end avec migration, service et routes.

- [ ] `backend/migrations/002_projects.sql`
- [ ] Modèles Pydantic `ProjectCreate`, `ProjectResponse` dans `models/project.py`
- [ ] `services/project_service.py` — fonctions DB
- [ ] `routers/projects.py` — `POST /api/v1/projects` + `GET /api/v1/projects`
- [ ] `tests/test_projects.py`
- [ ] Build Docker + déploiement
- [ ] Validation curl / Swagger

**Livrable :** API Projects live avec POST et GET fonctionnels

---

## Phase 2 — Profile (SINGLETON)

- [ ] `backend/migrations/003_profile.sql`
- [ ] Seed initial (une ligne)
- [ ] `GET /api/v1/profile` (public)
- [ ] `PATCH /api/v1/profile` (admin — JWT requis)
- [ ] Déploiement + validation

**Livrable :** endpoint Profile live

---

## Phase 3 — Auth + Messages

**Objectif :** JWT maison + réception de messages de contact.

- [ ] `POST /api/v1/auth/login` → retourne un JWT signé
- [ ] Middleware `require_admin` qui vérifie le JWT
- [ ] `backend/migrations/004_messages.sql`
- [ ] `POST /api/v1/messages` (public)
- [ ] `GET /api/v1/messages` (admin)
- [ ] `PATCH /api/v1/messages/{id}/read` (admin)
- [ ] Déploiement + validation

**Livrable :** système de contact + auth JWT fonctionnels

---

## Phase 4 — ML Models

- [ ] `backend/migrations/005_ml_models.sql`
- [ ] `POST /api/v1/projects/{id}/models` (admin)
- [ ] `GET /api/v1/projects/{id}/models` (public)
- [ ] `PATCH /api/v1/models/{id}` (admin — toggle `is_active`)
- [ ] Déploiement + validation

---

## Phase 5 — Experience, Certifications & Learning

- [ ] `backend/migrations/006_experience.sql`
- [ ] Endpoints CRUD pour `experience`, `certifications`, `learning_items`
- [ ] Déploiement + validation

---

## Phase 6 — Skills + Visitors

- [ ] `backend/migrations/007_skills_visitors.sql`
- [ ] `GET /api/v1/skills` (public)
- [ ] `POST /api/v1/analytics/track` (public)
- [ ] `GET /api/v1/admin/analytics` (admin)
- [ ] Déploiement + validation

---

## Phase 7 — Optimisation

- [ ] Logging structuré JSON avec `structlog`
- [ ] Gestion cohérente des erreurs (exception handlers FastAPI)
- [ ] Health check enrichi (uptime, pool stats)
- [ ] Revue des requêtes SQL (index manquants, N+1)

---

## Phase 8 — Kubernetes

**Objectif :** déploiement complet sur k3s Hetzner.

- [ ] Secrets k8s pour les variables sensibles
- [ ] ConfigMap pour les variables non-sensibles
- [ ] Deployment + Service pour le pod API
- [ ] Deployment + Service + PersistentVolumeClaim pour PostgreSQL
- [ ] Deployment + Service pour Redis
- [ ] Ingress Nginx avec règles de routage
- [ ] cert-manager + Let's Encrypt (SSL)
- [ ] HorizontalPodAutoscaler sur l'API (1 → 5 pods)
- [ ] GitHub Actions : build → push GHCR → `kubectl apply`

---

## 📍 État courant

```
Phase actuelle  : 0 — Setup
Tâche actuelle  : 0.3 — Initialisation uv (dépendances à ajouter)
Prochaine tâche : 0.4 — Variables d'environnement
Fait            : pyproject.toml initialisé (uv init), .python-version = 3.13
```

> Claude doit mettre à jour cette section à chaque avancement.

---

## ⚠️ Contraintes et règles

- Ne **jamais** sauter de phase
- Ne **jamais** implémenter plusieurs features simultanément
- Toujours viser des **unités déployables minimales**
- `.env` ne doit **jamais** être commité — vérifier `.gitignore`
- `uv.lock` doit **toujours** être commité avec le code
- R (Plumber/Shiny) n'a **pas de tables dédiées** — il consomme `projects` et `ml_models` — **pas de phase dédiée pour l'instant**, à planifier après la Phase 6
- L'auth est **JWT maison via FastAPI** — pas de service externe
- PostgreSQL et Redis tournent en **pods k8s avec PersistentVolumes** — pas de services managés externes
- Les migrations SQL sont des **fichiers numérotés** — jamais de modification rétroactive