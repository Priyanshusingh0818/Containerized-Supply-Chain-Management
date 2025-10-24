# InvGuard Cron Service

This service provides automated backup, monitoring, and maintenance tasks for the InvGuard inventory management system.

## Features

- **Automated Database Backups**: Daily encrypted backups of the SQLite database
- **Health Monitoring**: Continuous monitoring of the backend API and system health
- **Backup Management**: Automatic cleanup of old backup files
- **Alert System**: Notifications for system issues and low stock alerts
- **Flexible Scheduling**: Configurable backup and maintenance schedules

## Files

- `backup_cron.py` - Main backup and scheduling service
- `monitor.py` - Health monitoring and alerting service
- `requirements.txt` - Python dependencies
- `Dockerfile` - Container configuration
- `crontab` - Cron job definitions
- `start.sh` - Startup script

## Configuration

The service uses environment variables for configuration:

```bash
# Database configuration
DATABASE_PATH=/app/data/inventory.db
BACKUP_PATH=/app/backups

# Security
GPG_PASSPHRASE=your_secure_passphrase

# API configuration
API_URL=http://backend:5000/api

# Backup settings
BACKUP_RETENTION_DAYS=30
HEALTH_CHECK_INTERVAL=300
```

## Usage

### Running with Docker Compose

The cron service is automatically started with the main InvGuard stack:

```bash
docker-compose up -d
```

### Manual Execution

#### Run backup scheduler:
```bash
python backup_cron.py
```

#### Run one-time backup:
```bash
python backup_cron.py backup
```

#### Run cleanup:
```bash
python backup_cron.py cleanup
```

#### Check health:
```bash
python backup_cron.py health
```

#### Generate monitoring report:
```bash
python monitor.py report
```

## Scheduled Jobs

- **Daily Backup**: 02:00 AM - Creates encrypted database backup
- **Hourly Health Check**: Every hour - Monitors API health
- **Weekly Maintenance**: Sunday 03:00 AM - Cleans up old backups
- **Monthly Full Check**: 1st of month 04:00 AM - Complete system check

## Monitoring

The service provides comprehensive monitoring:

- **API Health**: Response time and availability
- **Low Stock Alerts**: Monitors inventory levels
- **Backup Status**: Tracks backup age and integrity
- **Disk Space**: Monitors available storage

## Backup Features

- **Encryption**: All backups are encrypted using GPG
- **Integrity Verification**: Automatic verification of backup files
- **Retention Policy**: Configurable retention period for old backups
- **Compression**: Efficient storage of backup files

## Logs

Logs are written to `/app/logs/`:
- `backup_cron.log` - Backup service logs
- `monitor.log` - Monitoring service logs
- `cron.log` - Cron job execution logs

## Security

- Runs as non-root user
- Encrypted backups with secure passphrase
- Proper file permissions (600 for sensitive files)
- Health checks to prevent unauthorized access

## Troubleshooting

### Check service status:
```bash
docker logs invguard_cron
```

### Manual backup verification:
```bash
gpg --list-only /app/backups/inventory_backup_*.gpg
```

### Check disk space:
```bash
df -h /app
```

### View recent logs:
```bash
tail -f /app/logs/backup_cron.log
```

## Development

### Install dependencies:
```bash
pip install -r requirements.txt
```

### Run tests:
```bash
python -m pytest
```

### Code formatting:
```bash
black *.py
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_PATH` | `/app/data/inventory.db` | Path to SQLite database |
| `BACKUP_PATH` | `/app/backups` | Backup storage directory |
| `GPG_PASSPHRASE` | `default_passphrase` | GPG encryption passphrase |
| `API_URL` | `http://backend:5000/api` | Backend API URL |
| `BACKUP_RETENTION_DAYS` | `30` | Days to keep backups |
| `HEALTH_CHECK_INTERVAL` | `300` | Health check interval (seconds) |
