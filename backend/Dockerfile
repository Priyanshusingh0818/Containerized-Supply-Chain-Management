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
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source with proper ownership
COPY --chown=appuser:users . .

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

# Health check for Render
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# RENDER SPECIFIC: Run as root to handle volume permissions, then switch to appuser in start.sh
CMD ["/bin/sh", "./start.sh"]
