### Multi-stage Dockerfile for root (builds frontend and backend)
### This mirrors the backend multi-stage Dockerfile so builds from the repo root
### will include the compiled frontend assets.

### Frontend build stage
FROM node:18-alpine AS frontend-build
WORKDIR /frontend

# Install frontend dependencies and build
COPY frontend/package*.json ./
RUN npm install --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

### Backend runtime stage
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TZ=UTC

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gnupg \
    sqlite3 \
    curl \
    gosu \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ ./

# Copy built frontend into backend image
COPY --from=frontend-build /frontend/build ./frontend_build

# Create data directory
RUN mkdir -p /app/data && chmod 755 /app/data

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Start the app using the backend start script (which switches to appuser)
CMD ["/bin/sh", "./start.sh"]
