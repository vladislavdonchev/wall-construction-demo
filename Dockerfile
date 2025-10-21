# Stage 1: Build React frontend
FROM node:22-alpine AS frontend-builder

WORKDIR /frontend

# Copy frontend package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy frontend source
COPY frontend/ ./

# Build React app
RUN npm run build

# Stage 2: Setup Python/Django backend
FROM python:3.12-alpine AS backend

WORKDIR /app

# Install build dependencies for Python packages
RUN apk add --no-cache gcc musl-dev linux-headers

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set uv environment variables
ENV UV_LINK_MODE=copy
ENV UV_PROJECT_ENVIRONMENT=/app/.venv

# Copy dependency files
COPY pyproject.toml ./
COPY uv.lock ./

# Install dependencies using uv
RUN uv sync --frozen

# Copy application code
COPY . .

# Stage 3: Final image with nginx
FROM nginx:alpine

# Install Python and supervisor
RUN apk add --no-cache python3 py3-pip supervisor

# Copy Python app and venv from backend stage
COPY --from=backend /app /app
COPY --from=backend /usr/local/bin/uv /usr/local/bin/uv

# Copy React build from frontend stage
COPY --from=frontend-builder /frontend/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Make startup script executable
RUN chmod +x /app/start-django.sh

# Create supervisor config directory and file
RUN mkdir -p /etc/supervisor/conf.d && \
    echo '[supervisord]' > /etc/supervisor/conf.d/supervisord.conf && \
    echo 'nodaemon=true' >> /etc/supervisor/conf.d/supervisord.conf && \
    echo '' >> /etc/supervisor/conf.d/supervisord.conf && \
    echo '[program:django]' >> /etc/supervisor/conf.d/supervisord.conf && \
    echo 'command=/app/start-django.sh' >> /etc/supervisor/conf.d/supervisord.conf && \
    echo 'directory=/app' >> /etc/supervisor/conf.d/supervisord.conf && \
    echo 'autostart=true' >> /etc/supervisor/conf.d/supervisord.conf && \
    echo 'autorestart=true' >> /etc/supervisor/conf.d/supervisord.conf && \
    echo 'stdout_logfile=/dev/stdout' >> /etc/supervisor/conf.d/supervisord.conf && \
    echo 'stdout_logfile_maxbytes=0' >> /etc/supervisor/conf.d/supervisord.conf && \
    echo 'stderr_logfile=/dev/stderr' >> /etc/supervisor/conf.d/supervisord.conf && \
    echo 'stderr_logfile_maxbytes=0' >> /etc/supervisor/conf.d/supervisord.conf && \
    echo '' >> /etc/supervisor/conf.d/supervisord.conf && \
    echo '[program:nginx]' >> /etc/supervisor/conf.d/supervisord.conf && \
    echo 'command=nginx -g "daemon off;"' >> /etc/supervisor/conf.d/supervisord.conf && \
    echo 'autostart=true' >> /etc/supervisor/conf.d/supervisord.conf && \
    echo 'autorestart=true' >> /etc/supervisor/conf.d/supervisord.conf

WORKDIR /app

EXPOSE 7860

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
