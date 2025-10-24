#!/usr/bin/env python3
"""
InvGuard Backup Cron Service
Automated backup and maintenance tasks for the InvGuard inventory management system.
"""

import os
import sys
import time
import logging
import schedule
import requests
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv

# Import backup utilities directly (standalone implementation)
from backup_utils import create_backup, restore_backup

# Load environment variables
load_dotenv()

# Configuration
DATABASE_PATH = os.getenv('DATABASE_PATH', '/app/data/inventory.db')
BACKUP_PATH = os.getenv('BACKUP_PATH', '/app/backups')
GPG_PASSPHRASE = os.getenv('GPG_PASSPHRASE', 'default_passphrase')
API_URL = os.getenv('API_URL', 'http://backend:5000/api')
BACKUP_RETENTION_DAYS = int(os.getenv('BACKUP_RETENTION_DAYS', '30'))
HEALTH_CHECK_INTERVAL = int(os.getenv('HEALTH_CHECK_INTERVAL', '300'))  # 5 minutes

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/backup_cron.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class InvGuardBackupService:
    """Main backup service class for InvGuard system"""
    
    def __init__(self):
        self.api_url = API_URL
        self.db_path = DATABASE_PATH
        self.backup_path = BACKUP_PATH
        self.gpg_passphrase = GPG_PASSPHRASE
        self.retention_days = BACKUP_RETENTION_DAYS
        
        # Ensure directories exist
        os.makedirs(self.backup_path, exist_ok=True)
        os.makedirs('/app/logs', exist_ok=True)
        
        logger.info("InvGuard Backup Service initialized")
    
    def health_check(self) -> bool:
        """Check if the backend API is healthy"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            if response.status_code == 200:
                logger.info("Backend API health check passed")
                return True
            else:
                logger.warning(f"Backend API health check failed: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Backend API health check error: {e}")
            return False
    
    def create_database_backup(self) -> Optional[str]:
        """Create an encrypted backup of the database"""
        try:
            logger.info("Starting database backup...")
            
            # Check if database exists
            if not os.path.exists(self.db_path):
                logger.error(f"Database file not found: {self.db_path}")
                return None
            
            # Create backup
            backup_file = create_backup(
                self.db_path,
                self.backup_path,
                encrypt=True,
                passphrase=self.gpg_passphrase
            )
            
            if backup_file:
                logger.info(f"Database backup created successfully: {backup_file}")
                return backup_file
            else:
                logger.error("Database backup failed")
                return None
                
        except Exception as e:
            logger.error(f"Error creating database backup: {e}")
            return None
    
    def cleanup_old_backups(self):
        """Remove backup files older than retention period"""
        try:
            logger.info(f"Cleaning up backups older than {self.retention_days} days...")
            
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            removed_count = 0
            
            for filename in os.listdir(self.backup_path):
                file_path = os.path.join(self.backup_path, filename)
                
                if os.path.isfile(file_path):
                    file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    
                    if file_time < cutoff_date:
                        os.remove(file_path)
                        removed_count += 1
                        logger.info(f"Removed old backup: {filename}")
            
            logger.info(f"Cleanup completed. Removed {removed_count} old backup files")
            
        except Exception as e:
            logger.error(f"Error during backup cleanup: {e}")
    
    def verify_backup_integrity(self, backup_file: str) -> bool:
        """Verify the integrity of a backup file"""
        try:
            if not os.path.exists(backup_file):
                logger.error(f"Backup file not found: {backup_file}")
                return False
            
            # Check file size (should be > 0)
            file_size = os.path.getsize(backup_file)
            if file_size == 0:
                logger.error(f"Backup file is empty: {backup_file}")
                return False
            
            # For encrypted files, try to decrypt to verify
            if backup_file.endswith('.gpg'):
                try:
                    # Test decryption without actually decrypting
                    import subprocess
                    result = subprocess.run([
                        'gpg', '--batch', '--yes', '--passphrase', self.gpg_passphrase,
                        '--list-only', backup_file
                    ], capture_output=True, text=True, timeout=30)
                    
                    if result.returncode == 0:
                        logger.info(f"Backup file integrity verified: {backup_file}")
                        return True
                    else:
                        logger.error(f"Backup file integrity check failed: {backup_file}")
                        return False
                        
                except subprocess.TimeoutExpired:
                    logger.error(f"Backup integrity check timed out: {backup_file}")
                    return False
                except Exception as e:
                    logger.error(f"Error verifying backup integrity: {e}")
                    return False
            else:
                # For unencrypted files, just check if it's a valid SQLite file
                try:
                    import sqlite3
                    conn = sqlite3.connect(backup_file)
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = cursor.fetchall()
                    conn.close()
                    
                    if len(tables) > 0:
                        logger.info(f"Backup file integrity verified: {backup_file}")
                        return True
                    else:
                        logger.error(f"Backup file appears to be empty or corrupted: {backup_file}")
                        return False
                        
                except Exception as e:
                    logger.error(f"Error verifying backup file: {e}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error during backup verification: {e}")
            return False
    
    def send_notification(self, message: str, level: str = "INFO"):
        """Send notification (placeholder for future integration with notification services)"""
        logger.info(f"NOTIFICATION [{level}]: {message}")
        # TODO: Integrate with email, Slack, or other notification services
    
    def daily_backup_job(self):
        """Daily backup job"""
        logger.info("Starting daily backup job...")
        
        # Health check before backup
        if not self.health_check():
            self.send_notification("Backup skipped: Backend API is not healthy", "WARNING")
            return
        
        # Create backup
        backup_file = self.create_database_backup()
        
        if backup_file:
            # Verify backup integrity
            if self.verify_backup_integrity(backup_file):
                self.send_notification(f"Daily backup completed successfully: {backup_file}", "INFO")
            else:
                self.send_notification(f"Daily backup created but integrity check failed: {backup_file}", "ERROR")
        else:
            self.send_notification("Daily backup failed", "ERROR")
        
        # Cleanup old backups
        self.cleanup_old_backups()
    
    def hourly_health_check_job(self):
        """Hourly health check job"""
        logger.info("Starting hourly health check...")
        
        if not self.health_check():
            self.send_notification("Backend API health check failed", "ERROR")
        else:
            logger.info("Hourly health check passed")
    
    def weekly_maintenance_job(self):
        """Weekly maintenance job"""
        logger.info("Starting weekly maintenance job...")
        
        # Cleanup old backups
        self.cleanup_old_backups()
        
        # Check disk space
        try:
            import shutil
            total, used, free = shutil.disk_usage(self.backup_path)
            free_gb = free // (1024**3)
            
            if free_gb < 1:  # Less than 1GB free
                self.send_notification(f"Low disk space warning: {free_gb}GB free", "WARNING")
            else:
                logger.info(f"Disk space check passed: {free_gb}GB free")
                
        except Exception as e:
            logger.error(f"Error checking disk space: {e}")
        
        self.send_notification("Weekly maintenance completed", "INFO")
    
    def run_scheduler(self):
        """Run the backup scheduler"""
        logger.info("Starting InvGuard Backup Scheduler...")
        
        # Schedule jobs
        schedule.every().day.at("02:00").do(self.daily_backup_job)
        schedule.every().hour.do(self.hourly_health_check_job)
        schedule.every().sunday.at("03:00").do(self.weekly_maintenance_job)
        
        # Initial health check
        self.health_check()
        
        logger.info("Scheduler started. Jobs scheduled:")
        logger.info("- Daily backup: 02:00")
        logger.info("- Hourly health check: Every hour")
        logger.info("- Weekly maintenance: Sunday 03:00")
        
        # Run scheduler
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                logger.info("Scheduler stopped by user")
                break
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(60)  # Wait before retrying

def main():
    """Main entry point"""
    logger.info("InvGuard Backup Cron Service starting...")
    
    # Create backup service
    backup_service = InvGuardBackupService()
    
    # Check if running as a one-time backup
    if len(sys.argv) > 1 and sys.argv[1] == "backup":
        logger.info("Running one-time backup...")
        backup_service.daily_backup_job()
    elif len(sys.argv) > 1 and sys.argv[1] == "cleanup":
        logger.info("Running cleanup...")
        backup_service.cleanup_old_backups()
    elif len(sys.argv) > 1 and sys.argv[1] == "health":
        logger.info("Running health check...")
        if backup_service.health_check():
            print("Health check passed")
            sys.exit(0)
        else:
            print("Health check failed")
            sys.exit(1)
    else:
        # Run scheduler
        backup_service.run_scheduler()

if __name__ == "__main__":
    main()
