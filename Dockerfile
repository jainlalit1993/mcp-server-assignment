# Multi-stage build: compile the React UI, then a slim Python runtime that
# serves BOTH the FastAPI API and the built UI at "/" on the same origin.
#
# Why a Dockerfile (not Railpack)? Railpack only auto-detects an entrypoint at
# the repo root (main.py/app.py/server.py); this app lives at api/main.py, and
# Railpack's Procfile support is deprecated — so its build can't resolve a start
# command. A Dockerfile makes the build deterministic and bakes in the start
# command, removing all of that guesswork.

# ---------- stage 1: build the React frontend ----------
FROM node:22-slim AS frontend
WORKDIR /web
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# ---------- stage 2: Python runtime ----------
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

WORKDIR /app

# Install dependencies first so this layer caches across code-only changes.
COPY requirements.txt .
RUN pip install -r requirements.txt

# App code.
COPY agent/ ./agent/
COPY api/ ./api/
# Built React UI — FastAPI mounts this at "/" (see api/main.py).
COPY --from=frontend /web/dist ./frontend/dist

# Run as a non-root user.
RUN useradd --create-home --uid 10001 appuser
USER appuser

EXPOSE 8000

# Railway injects $PORT at runtime; default to 8000 for local `docker run`.
CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT}"]
