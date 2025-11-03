FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN uv sync

COPY . .

CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]