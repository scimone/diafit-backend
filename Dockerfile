FROM python:3.11-slim

WORKDIR /app

COPY . .
RUN uv sync

CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]