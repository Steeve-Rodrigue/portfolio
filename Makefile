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

format:
	cd backend && uv run ruff format app/
