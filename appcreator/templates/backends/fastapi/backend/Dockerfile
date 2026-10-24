# Production image: database migrations on start (when Alembic is set up), then uvicorn.
# Local development uses Dockerfile.dev (see docker-compose.yml).
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Files that must survive a deploy (uploads etc.) go under /data (a persistent volume in production)
RUN mkdir -p /data

EXPOSE 8000

CMD ["sh", "-c", "if [ -f alembic.ini ]; then alembic upgrade head; fi && exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips=*"]
