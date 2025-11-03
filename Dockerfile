FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

COPY . .
RUN uv sync

CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]