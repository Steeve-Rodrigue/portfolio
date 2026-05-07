.PHONY: build stop logs db-shell test lint

build:
	sudo docker compose up -d --build

stop:
	sudo docker compose down

logs:
	sudo docker compose logs -f api

db-shell:
	sudo docker compose exec db psql -U portfolio_user -d portfolio

test:
	cd backend && uv run pytest tests/ -v

lint:
	cd backend && uv run ruff check app/

format:
	cd backend && uv run ruff format app/

uvicorn:
	cd backend && uv run uvicorn app.main:app

coverage:
	cd backend && uv run pytest --cov=app tests/

restart:
	sudo docker compose restart api

sql-migrate:
	cd backend && sudo docker compose exec db psql -U portfolio_user -d portfolio -f /docker-entrypoint-initdb.d/${file}
