FROM python:3.12-slim

WORKDIR /app

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set uv environment variables
ENV UV_LINK_MODE=copy
ENV UV_PROJECT_ENVIRONMENT=/app/.venv

# Copy dependency files
COPY pyproject.toml ./
COPY uv.lock ./

# Install dependencies using uv with BuildKit cache mount
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

# Copy application code
COPY . .

# Run migrations and start Django on port 7860
# Use python directly since dependencies already installed in venv
CMD /app/.venv/bin/python manage.py migrate && \
    /app/.venv/bin/python manage.py runserver 0.0.0.0:7860
