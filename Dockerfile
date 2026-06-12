# Multi-stage build: build the React UI, install Python deps, then a slim,
# non-root runtime that serves both the API and the built UI.

# ---------- stage 1: build the frontend ----------
FROM node:22-slim AS frontend
WORKDIR /web
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# ---------- stage 2: install Python dependencies ----------
FROM python:3.11-slim AS builder
WORKDIR /app
ENV PIP_NO_CACHE_DIR=1
COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

# ---------- stage 3: runtime ----------
FROM python:3.11-slim AS runtime
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000
WORKDIR /app

# Run as a non-root user.
RUN useradd --create-home --uid 10001 appuser

# Copy installed packages and app code.
COPY --from=builder /install /usr/local
COPY agent/ ./agent/
COPY api/ ./api/
COPY --from=frontend /web/dist ./frontend/dist

USER appuser
EXPOSE 8000

# Read PORT from the environment (Railway/other platforms set it).
CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT}"]
