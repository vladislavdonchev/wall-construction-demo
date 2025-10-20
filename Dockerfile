FROM python:3.12-slim

WORKDIR /app

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set uv environment variables for non-root container execution
ENV UV_CACHE_DIR=/tmp/.uv-cache
ENV UV_PROJECT_ENVIRONMENT=/app/.venv

# Copy dependency files
COPY pyproject.toml ./
COPY uv.lock ./

# Install dependencies using uv
RUN uv sync --frozen

# Copy application code
COPY . .

# Run migrations and start Django on port 7860
CMD uv run python manage.py migrate && \
    uv run python manage.py runserver 0.0.0.0:7860
