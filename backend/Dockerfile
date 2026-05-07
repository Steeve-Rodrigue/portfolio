FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

ARG INSTALL_DEV=false
COPY pyproject.toml uv.lock ./
RUN if [ "$INSTALL_DEV" = "true" ]; then \
        uv sync --frozen; \
    else \
        uv sync --frozen --no-dev; \
    fi

COPY app/ ./app/

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
