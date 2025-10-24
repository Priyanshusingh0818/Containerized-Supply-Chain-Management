# InvGuard Cron Service Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV TZ=UTC

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gnupg2 \
    gpg \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy cron scripts
COPY backup_cron.py .
COPY backup_utils.py .
COPY monitor.py .
COPY config.py .
COPY start.sh .

# Copy crontab file
COPY crontab /etc/cron.d/invguard-cron

# Create necessary directories
RUN mkdir -p /app/logs /app/backups /app/data

# Set up cron permissions
RUN chmod 0644 /etc/cron.d/invguard-cron
RUN chmod +x backup_cron.py
RUN chmod +x start.sh

# Create a non-root user for security
RUN groupadd -r invguard && useradd -r -g invguard invguard
RUN chown -R invguard:invguard /app
RUN chown -R invguard:invguard /etc/cron.d/invguard-cron

# Switch to non-root user
USER invguard

# Health check
HEALTHCHECK --interval=5m --timeout=30s --start-period=30s --retries=3 \
    CMD python backup_cron.py health || exit 1

# Default command - run the backup scheduler
CMD ["python", "backup_cron.py"]
