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

# Stage 2: Final image with nginx and Python
FROM nginx:alpine

# Cache buster to force rebuild on HuggingFace (increment when needed)
ARG CACHEBUST=2

# Install Python, pip, supervisor, and curl for healthcheck
RUN apk add --no-cache \
    python3 \
    py3-pip \
    supervisor \
    curl \
    gcc \
    python3-dev \
    musl-dev \
    linux-headers

# Install Python dependencies system-wide
RUN pip3 install --no-cache-dir --break-system-packages \
    Django==5.2.7 \
    djangorestframework==3.16.0 \
    django-filter==24.3 \
    pydantic==2.10.6 \
    gunicorn==23.0.0 \
    loguru==0.7.3

# Copy React build from frontend stage
COPY --from=frontend-builder /frontend/dist /usr/share/nginx/html

# Copy application code
COPY . /app

# Copy configuration files
COPY nginx.conf /etc/nginx/nginx.conf
COPY supervisord.conf /etc/supervisor/supervisord.conf

# Make startup script executable
RUN chmod +x /app/start-django.sh

# Create /app marker for container detection
RUN mkdir -p /app && touch /app/.container

WORKDIR /app

EXPOSE 7860

# Healthcheck to verify services are running
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:7860/api/ || exit 1

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
