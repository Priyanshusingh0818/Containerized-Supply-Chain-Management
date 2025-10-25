#!/bin/sh
set -e

echo "=== InvGuard Backend Startup ==="

# Determine data directory (Render uses /data, local uses /app/data)
DATA_DIR="${DATABASE_PATH%/*}"
echo "Data directory: $DATA_DIR"

# Ensure data directory exists and has correct permissions
if [ -d "$DATA_DIR" ]; then
    echo "Setting permissions on $DATA_DIR"
    chown -R appuser:users "$DATA_DIR" 2>/dev/null || true
    chmod -R 755 "$DATA_DIR" 2>/dev/null || true
fi

# If database file exists, set its permissions
if [ -f "$DATABASE_PATH" ]; then
    echo "Database file exists at $DATABASE_PATH"
    chown appuser:users "$DATABASE_PATH" 2>/dev/null || true
    chmod 644 "$DATABASE_PATH" 2>/dev/null || true
fi

echo "Environment: ${FLASK_ENV:-development}"
echo "Database path: ${DATABASE_PATH:-/app/data/inventory.db}"
echo "Port: ${PORT:-5000}"

# Start the application as appuser
echo "Starting Flask application..."
exec gosu appuser python app.py
