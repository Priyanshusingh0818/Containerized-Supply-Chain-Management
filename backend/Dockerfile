### Multi-stage Dockerfile: build the frontend, then build the backend image
###  - Stage `frontend-build` compiles the React app into /frontend/build
###  - Final Python image copies backend code and the frontend build into /app/frontend_build

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

# Best-practice Python runtime flags
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TZ=UTC

WORKDIR /app

# Install minimal system dependencies + curl for health checks + gosu for user switching
RUN apt-get update && apt-get install -y --no-install-recommends \
    gnupg \
    sqlite3 \
    curl \
    gosu \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user FIRST (before copying files)
RUN useradd -r -u 10001 -g users appuser

# Install Python deps first for better layer caching
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source with proper ownership
COPY --chown=appuser:users backend/ ./

# Copy built frontend from the frontend-build stage into the backend image
# The build artifacts will be placed at /app/frontend_build
COPY --from=frontend-build /frontend/build ./frontend_build

# RENDER SPECIFIC: Create data directory at /data (where Render mounts disk)
RUN mkdir -p /data \
    && chown -R appuser:users /data \
    && chmod 777 /data

# Also keep /app/data for compatibility
RUN mkdir -p /app/data \
    && chown -R appuser:users /app/data \
    && chmod 755 /app/data

# Make start script executable if it exists
RUN if [ -f start.sh ]; then chmod +x start.sh; fi

# Expose port
EXPOSE 5000

# Health check for Render - check backend health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Use start.sh which switches to non-root user and runs the app
CMD ["/bin/sh", "./start.sh"]
