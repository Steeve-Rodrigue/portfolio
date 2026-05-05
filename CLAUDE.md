# CLAUDE.md — ePortfolio (racine)

> Ce fichier est le point d'entrée pour Claude au niveau du repo. Les instructions complètes (stack, schéma DB, conventions, workflow par phases) se trouvent dans le fichier spécifique à chaque service.

## Structure du repo

```
portfolio/
├── backend/          # FastAPI + asyncpg + uv — Python 3.13
│   └── CLAUDE.md     # ← Instructions complètes du backend
├── k8s/              # Manifests Kubernetes (Phase 8)
├── .github/
│   └── workflows/    # GitHub Actions CI/CD
├── docker-compose.yml
├── Makefile
└── CLAUDE.md         # ← ce fichier
```

## Règle fondamentale

Toujours lire `backend/CLAUDE.md` avant d'intervenir sur le backend.  
Le frontend (Next.js) et le backend R (Plumber/Shiny) n'ont pas encore de CLAUDE.md — à créer lors de leur phase respective.

## Principes transversaux

- Tout est **self-hosted sur k3s** (Hetzner VPS) — pas de services cloud managés
- Un seul environnement de déploiement : production (pas de staging pour l'instant)
- `.env` ne doit **jamais** être commité
- `uv.lock` doit **toujours** être commité
