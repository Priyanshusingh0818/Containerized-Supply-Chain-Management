#!/bin/bash
# InvGuard Setup Script

echo "🚀 Setting up InvGuard Inventory Management System..."

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# InvGuard Environment Variables
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
GPG_PASSPHRASE=your-secure-gpg-passphrase
DATABASE_PATH=/app/data/inventory.db
BACKUP_PATH=/app/backups
BACKUP_RETENTION_DAYS=30
API_URL=http://localhost:5000/api
HEALTH_CHECK_INTERVAL=300
REACT_APP_API_URL=http://localhost:5000/api
EOF
    echo "✅ .env file created. Please update the values before running the application."
else
    echo "✅ .env file already exists."
fi

# Create logs directory for cron service
mkdir -p cron/logs

# Set proper permissions
chmod +x cron/start.sh

echo "🔧 Building Docker containers..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

echo "⏳ Waiting for services to start..."
sleep 10

echo "🔍 Checking service status..."
docker-compose ps

echo ""
echo "🎉 InvGuard is now running!"
echo ""
echo "📱 Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:5000/api"
echo ""
echo "🔑 Default credentials:"
echo "   Admin: admin / admin"
echo "   Viewer: viewer / viewer123"
echo ""
echo "📊 Check logs with: docker-compose logs -f"
echo "🛑 Stop with: docker-compose down"
