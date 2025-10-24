@echo off
echo 🚀 Setting up InvGuard Inventory Management System...

REM Create .env file if it doesn't exist
if not exist .env (
    echo 📝 Creating .env file...
    (
        echo # InvGuard Environment Variables
        echo JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
        echo GPG_PASSPHRASE=your-secure-gpg-passphrase
        echo DATABASE_PATH=/app/data/inventory.db
        echo BACKUP_PATH=/app/backups
        echo BACKUP_RETENTION_DAYS=30
        echo API_URL=http://localhost:5000/api
        echo HEALTH_CHECK_INTERVAL=300
        echo REACT_APP_API_URL=http://localhost:5000/api
    ) > .env
    echo ✅ .env file created. Please update the values before running the application.
) else (
    echo ✅ .env file already exists.
)

REM Create logs directory for cron service
if not exist cron\logs mkdir cron\logs

echo 🔧 Building Docker containers...
docker-compose build

echo 🚀 Starting services...
docker-compose up -d

echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak > nul

echo 🔍 Checking service status...
docker-compose ps

echo.
echo 🎉 InvGuard is now running!
echo.
echo 📱 Access the application:
echo    Frontend: http://localhost:3000
echo    Backend API: http://localhost:5000/api
echo.
echo 🔑 Default credentials:
echo    Admin: admin / admin
echo    Viewer: viewer / viewer123
echo.
echo 📊 Check logs with: docker-compose logs -f
echo 🛑 Stop with: docker-compose down
pause
