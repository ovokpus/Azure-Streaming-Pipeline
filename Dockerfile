# One image for the ingest API, the Cosmos writer worker and the replay producer.
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.8.4 /uv /usr/local/bin/uv
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH=/app:/app/azure-func PYTHONUNBUFFERED=1
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY azure-func/shared_code/ ./azure-func/shared_code/
COPY stream/ ./stream/
EXPOSE 8000
CMD ["uvicorn", "stream.api:app", "--host", "0.0.0.0", "--port", "8000"]
