# syntax=docker/dockerfile:1.7

FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

FROM base AS web
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY alembic.ini main.py ./
COPY app ./app
COPY migrations ./migrations
COPY templates ./templates
COPY static ./static
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM base AS worker
COPY requirements.txt requirements-worker.txt ./
RUN pip install --upgrade pip && pip install -r requirements-worker.txt
COPY alembic.ini main.py ./
COPY app ./app
COPY migrations ./migrations
COPY templates ./templates
COPY static ./static
CMD ["python", "-m", "app.workers.run"]
