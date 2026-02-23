# ---------- Stage 1: Builder ----------
FROM python:3.11-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---------- Stage 2: Runtime ----------
FROM python:3.11-slim AS runtime

# Non-root user for security
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY . /app/src/api/
# Create proper package structure
RUN mkdir -p /app/src && touch /app/src/__init__.py

ENV PYTHONUNBUFFERED=1
ENV PORT=8080

EXPOSE 8080

# Switch to non-root user
USER appuser

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen(f'http://localhost:{__import__(\"os\").environ.get(\"PORT\",\"8080\")}/health')" || exit 1

# Use shell form so $PORT is expanded at runtime (Cloud Run sets PORT=8080)
CMD uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
