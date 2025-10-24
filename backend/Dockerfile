FROM python:3.11-slim

# Best-practice Python runtime flags
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TZ=UTC

WORKDIR /app

# Install minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gnupg \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user FIRST (before copying files)
RUN useradd -r -u 10001 -g users appuser

# Install Python deps first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source with proper ownership
COPY --chown=appuser:users . .

# Create data directory with proper ownership and permissions
RUN mkdir -p /app/data \
    && chown -R appuser:users /app/data \
    && chmod 755 /app/data

# Make start script executable if it exists
RUN if [ -f start.sh ]; then chmod +x start.sh; fi

## Note: start.sh needs to run as root at container start to ensure mounted
## volumes (named volumes) have correct ownership and the DB file can be
## created/chowned. For development we run the start script as root which
## will create the DB file and optionally chown it. In production you may
## want to run as non-root or use an init container.

# Expose port
EXPOSE 5000

# Use the start script as the container entrypoint (runs as root)
CMD ["/bin/sh", "./start.sh"]