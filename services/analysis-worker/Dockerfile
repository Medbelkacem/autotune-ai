FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VERSION=1.8.3

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential libpq-dev curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install "poetry==${POETRY_VERSION}"

WORKDIR /app
COPY services/analysis-worker/pyproject.toml services/analysis-worker/poetry.lock* /app/
COPY packages/shared-schemas/python /packages/shared-schemas/python
RUN poetry install --no-root --no-interaction --no-ansi

COPY services/analysis-worker /app

CMD ["celery", "-A", "worker.celery_app", "worker", "-l", "INFO", "-Q", "analysis,embedding,simulation"]
