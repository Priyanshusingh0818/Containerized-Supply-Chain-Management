#!/bin/bash
# InvGuard Cron Service Startup Script

set -e

echo "Starting InvGuard Cron Service..."

# Create necessary directories
mkdir -p /app/logs /app/backups /app/data

# Set proper permissions
chmod 755 /app/logs /app/backups /app/data

# Wait for backend to be ready
echo "Waiting for backend API to be ready..."
until curl -f http://backend:5000/api/health > /dev/null 2>&1; do
    echo "Backend not ready, waiting..."
    sleep 5
done

echo "Backend API is ready!"

# Check if we should run cron daemon or direct execution
if [ "$1" = "cron" ]; then
    echo "Starting cron daemon..."
    # Start cron daemon
    cron -f
else
    echo "Starting backup scheduler directly..."
    # Run the backup scheduler directly
    exec python backup_cron.py
fi
