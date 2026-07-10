FROM python:3.12-slim AS base

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/production.txt

FROM base AS test
RUN pip install --no-cache-dir -r requirements/test.txt
COPY . .
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

FROM base AS production
COPY . .
RUN mkdir -p /app/logs /app/staticfiles && useradd -m appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
ENTRYPOINT ["./entrypoint.sh"]
