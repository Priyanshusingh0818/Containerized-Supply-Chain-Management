#!/bin/sh

# Wait for the data directory to be mounted
while [ ! -d "/app/data" ]; do
    echo "Waiting for data directory to be mounted..."
    sleep 1
done

# Set proper permissions
chown -R appuser:users /app/data
chmod 777 /app/data

# Create empty database file
touch /app/data/inventory.db
chown appuser:users /app/data/inventory.db
chmod 600 /app/data/inventory.db

# Start the Flask application
python app.py