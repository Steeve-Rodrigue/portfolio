.PHONY: dev stop logs db-shell test lint

dev:
	sudo docker compose up --build

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

restart:
	sudo docker compose restart api
