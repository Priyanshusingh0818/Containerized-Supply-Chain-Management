import os
import shutil
import subprocess
from datetime import datetime

def create_backup(db_path, backup_dir, encrypt=True, passphrase=None):
    """Create encrypted backup of database"""
    try:
        # Ensure backup directory exists
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f'inventory_backup_{timestamp}.db')
        
        # Copy database file
        shutil.copy2(db_path, backup_file)
        print(f"Backup created: {backup_file}")
        
        # Encrypt backup if requested
        if encrypt and passphrase:
            encrypted_file = f"{backup_file}.gpg"
            try:
                # Use GPG to encrypt the backup
                subprocess.run([
                    'gpg', '--batch', '--yes', '--passphrase', passphrase,
                    '--symmetric', '--cipher-algo', 'AES256',
                    '--output', encrypted_file, backup_file
                ], check=True, capture_output=True)
                
                # Remove unencrypted backup
                os.remove(backup_file)
                print(f"Encrypted backup created: {encrypted_file}")
                
                # Set secure permissions
                os.chmod(encrypted_file, 0o600)
                
                return encrypted_file
            except subprocess.CalledProcessError as e:
                print(f"Encryption failed: {e}")
                return backup_file
        
        # Set secure permissions
        os.chmod(backup_file, 0o600)
        return backup_file
        
    except Exception as e:
        print(f"Backup failed: {e}")
        return None

def restore_backup(backup_file, db_path, passphrase=None):
    """Restore database from encrypted backup"""
    try:
        if backup_file.endswith('.gpg'):
            # Decrypt first
            decrypted_file = backup_file.replace('.gpg', '')
            subprocess.run([
                'gpg', '--batch', '--yes', '--passphrase', passphrase,
                '--decrypt', '--output', decrypted_file, backup_file
            ], check=True, capture_output=True)
            
            shutil.copy2(decrypted_file, db_path)
            os.remove(decrypted_file)
        else:
            shutil.copy2(backup_file, db_path)
        
        print(f"Database restored from: {backup_file}")
        return True
    except Exception as e:
        print(f"Restore failed: {e}")
        return False