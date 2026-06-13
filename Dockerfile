# Backend-only image for Railway.
#
# Why a Dockerfile (not Railpack)? Railpack only auto-detects an entrypoint at
# the repo root (main.py/app.py/server.py); this app lives at api/main.py, and
# Railpack's Procfile support is deprecated — so its build can't resolve a start
# command. A Dockerfile makes the build deterministic and bakes in the start
# command, removing all of that guesswork.
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

WORKDIR /app

# Install dependencies first so this layer caches across code-only changes.
COPY requirements.txt .
RUN pip install -r requirements.txt

# App code (backend only — the React frontend is not built/served here).
COPY agent/ ./agent/
COPY api/ ./api/

# Run as a non-root user.
RUN useradd --create-home --uid 10001 appuser
USER appuser

EXPOSE 8000

# Railway injects $PORT at runtime; default to 8000 for local `docker run`.
CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT}"]
