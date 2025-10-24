"""
InvGuard Cron Service Configuration
Default configuration values for the cron service.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database Configuration
DATABASE_PATH = os.getenv('DATABASE_PATH', '/app/data/inventory.db')
BACKUP_PATH = os.getenv('BACKUP_PATH', '/app/backups')

# Security Configuration
GPG_PASSPHRASE = os.getenv('GPG_PASSPHRASE', 'default_passphrase')

# API Configuration
API_URL = os.getenv('API_URL', 'http://backend:5000/api')

# Backup Configuration
BACKUP_RETENTION_DAYS = int(os.getenv('BACKUP_RETENTION_DAYS', '30'))
HEALTH_CHECK_INTERVAL = int(os.getenv('HEALTH_CHECK_INTERVAL', '300'))

# Monitoring Configuration
ALERT_THRESHOLDS = {
    'low_stock_percentage': 0.1,  # Alert if more than 10% of items are low stock
    'backup_failure_hours': 25,   # Alert if no backup in 25 hours
    'api_response_time_ms': 5000, # Alert if API response > 5 seconds
    'disk_space_gb': 1,           # Alert if less than 1GB free
    'disk_usage_percentage': 90,  # Alert if more than 90% disk usage
}

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Schedule Configuration
SCHEDULE_CONFIG = {
    'daily_backup_time': '02:00',
    'weekly_maintenance_day': 'sunday',
    'weekly_maintenance_time': '03:00',
    'monthly_check_day': 1,
    'monthly_check_time': '04:00',
}
