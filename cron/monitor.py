#!/usr/bin/env python3
"""
InvGuard Monitor Service
Monitoring and alerting utilities for the InvGuard system.
"""

import os
import sys
import json
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_URL = os.getenv('API_URL', 'http://backend:5000/api')
LOG_FILE = '/app/logs/monitor.log'
ALERT_THRESHOLDS = {
    'low_stock_percentage': 0.1,  # Alert if more than 10% of items are low stock
    'backup_failure_hours': 25,   # Alert if no backup in 25 hours
    'api_response_time_ms': 5000, # Alert if API response > 5 seconds
}

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class InvGuardMonitor:
    """Monitoring service for InvGuard system"""
    
    def __init__(self):
        self.api_url = API_URL
        self.thresholds = ALERT_THRESHOLDS
        logger.info("InvGuard Monitor initialized")
    
    def check_api_health(self) -> Dict:
        """Check API health and response time"""
        try:
            start_time = datetime.now()
            response = requests.get(f"{self.api_url}/health", timeout=10)
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            health_data = {
                'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                'response_time_ms': response_time,
                'status_code': response.status_code,
                'timestamp': datetime.now().isoformat()
            }
            
            if response_time > self.thresholds['api_response_time_ms']:
                health_data['alert'] = f"High response time: {response_time:.2f}ms"
            
            return health_data
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def check_low_stock_alerts(self) -> Dict:
        """Check for low stock items"""
        try:
            response = requests.get(f"{self.api_url}/analytics/low-stock", timeout=10)
            
            if response.status_code == 200:
                low_stock_items = response.json()
                total_items_response = requests.get(f"{self.api_url}/items", timeout=10)
                
                if total_items_response.status_code == 200:
                    total_items = len(total_items_response.json())
                    low_stock_percentage = len(low_stock_items) / total_items if total_items > 0 else 0
                    
                    alert_data = {
                        'low_stock_count': len(low_stock_items),
                        'total_items': total_items,
                        'low_stock_percentage': low_stock_percentage,
                        'items': low_stock_items,
                        'alert': low_stock_percentage > self.thresholds['low_stock_percentage'],
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    if alert_data['alert']:
                        alert_data['message'] = f"High percentage of low stock items: {low_stock_percentage:.1%}"
                    
                    return alert_data
                else:
                    return {'error': 'Failed to get total items count', 'timestamp': datetime.now().isoformat()}
            else:
                return {'error': f'API error: {response.status_code}', 'timestamp': datetime.now().isoformat()}
                
        except Exception as e:
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def check_backup_status(self) -> Dict:
        """Check backup status and age"""
        try:
            backup_dir = '/app/backups'
            if not os.path.exists(backup_dir):
                return {
                    'status': 'error',
                    'message': 'Backup directory not found',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Find the most recent backup
            backup_files = [f for f in os.listdir(backup_dir) if f.endswith('.gpg') or f.endswith('.db')]
            
            if not backup_files:
                return {
                    'status': 'error',
                    'message': 'No backup files found',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Get the most recent backup file
            latest_backup = max(
                [os.path.join(backup_dir, f) for f in backup_files],
                key=os.path.getctime
            )
            
            backup_age_hours = (datetime.now() - datetime.fromtimestamp(os.path.getctime(latest_backup))).total_seconds() / 3600
            
            backup_data = {
                'latest_backup': os.path.basename(latest_backup),
                'backup_age_hours': backup_age_hours,
                'backup_size_mb': os.path.getsize(latest_backup) / (1024 * 1024),
                'alert': backup_age_hours > self.thresholds['backup_failure_hours'],
                'timestamp': datetime.now().isoformat()
            }
            
            if backup_data['alert']:
                backup_data['message'] = f"Backup is {backup_age_hours:.1f} hours old"
            
            return backup_data
            
        except Exception as e:
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def check_disk_space(self) -> Dict:
        """Check available disk space"""
        try:
            import shutil
            total, used, free = shutil.disk_usage('/app')
            
            free_gb = free / (1024**3)
            used_percentage = (used / total) * 100
            
            disk_data = {
                'total_gb': total / (1024**3),
                'used_gb': used / (1024**3),
                'free_gb': free_gb,
                'used_percentage': used_percentage,
                'alert': free_gb < 1 or used_percentage > 90,
                'timestamp': datetime.now().isoformat()
            }
            
            if disk_data['alert']:
                disk_data['message'] = f"Low disk space: {free_gb:.1f}GB free ({used_percentage:.1f}% used)"
            
            return disk_data
            
        except Exception as e:
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def generate_health_report(self) -> Dict:
        """Generate comprehensive health report"""
        logger.info("Generating health report...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'checks': {}
        }
        
        # API Health Check
        report['checks']['api_health'] = self.check_api_health()
        
        # Low Stock Check
        report['checks']['low_stock'] = self.check_low_stock_alerts()
        
        # Backup Status Check
        report['checks']['backup_status'] = self.check_backup_status()
        
        # Disk Space Check
        report['checks']['disk_space'] = self.check_disk_space()
        
        # Overall health status
        alerts = []
        for check_name, check_data in report['checks'].items():
            if check_data.get('alert'):
                alerts.append(f"{check_name}: {check_data.get('message', 'Alert triggered')}")
        
        report['overall_status'] = 'healthy' if not alerts else 'unhealthy'
        report['alerts'] = alerts
        
        return report
    
    def send_alert(self, message: str, severity: str = "WARNING"):
        """Send alert notification"""
        logger.warning(f"ALERT [{severity}]: {message}")
        # TODO: Integrate with notification services (email, Slack, etc.)
    
    def run_monitoring_cycle(self):
        """Run a complete monitoring cycle"""
        logger.info("Starting monitoring cycle...")
        
        report = self.generate_health_report()
        
        # Log the report
        logger.info(f"Health report: {json.dumps(report, indent=2)}")
        
        # Send alerts if any
        for alert in report['alerts']:
            self.send_alert(alert)
        
        return report

def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "report":
        # Generate and print health report
        monitor = InvGuardMonitor()
        report = monitor.generate_health_report()
        print(json.dumps(report, indent=2))
    else:
        # Run monitoring cycle
        monitor = InvGuardMonitor()
        monitor.run_monitoring_cycle()

if __name__ == "__main__":
    main()
