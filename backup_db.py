#!/usr/bin/env python3
"""
Database Backup Script for HRMS
Automatically backs up the SQLite database with timestamp
"""

import shutil
import os
from datetime import datetime, timedelta
import sys


def backup_database(db_path="instance/hrms.db", backup_dir="backups"):
    """
    Create a timestamped backup of the database
    
    Args:
        db_path: Path to the database file
        backup_dir: Directory to store backups
    """
    # Create backup directory if it doesn't exist
    os.makedirs(backup_dir, exist_ok=True)
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"❌ Error: Database file not found at {db_path}")
        return False
    
    # Create timestamp for backup filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"hrms_backup_{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    try:
        # Copy database file
        shutil.copy2(db_path, backup_path)
        
        # Get file size
        file_size = os.path.getsize(backup_path)
        file_size_mb = file_size / (1024 * 1024)
        
        print(f"✅ Database backed up successfully!")
        print(f"   Location: {backup_path}")
        print(f"   Size: {file_size_mb:.2f} MB")
        print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during backup: {str(e)}")
        return False


def cleanup_old_backups(backup_dir="backups", retention_days=30):
    """
    Remove backups older than retention_days
    
    Args:
        backup_dir: Directory containing backups
        retention_days: Number of days to keep backups
    """
    if not os.path.exists(backup_dir):
        return
    
    cutoff_date = datetime.now() - timedelta(days=retention_days)
    removed_count = 0
    
    try:
        for filename in os.listdir(backup_dir):
            if filename.startswith("hrms_backup_") and filename.endswith(".db"):
                file_path = os.path.join(backup_dir, filename)
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                if file_time < cutoff_date:
                    os.remove(file_path)
                    removed_count += 1
                    print(f"🗑️  Removed old backup: {filename}")
        
        if removed_count > 0:
            print(f"✅ Cleaned up {removed_count} old backup(s)")
        else:
            print(f"✅ No old backups to clean up")
            
    except Exception as e:
        print(f"❌ Error during cleanup: {str(e)}")


def list_backups(backup_dir="backups"):
    """
    List all available backups
    
    Args:
        backup_dir: Directory containing backups
    """
    if not os.path.exists(backup_dir):
        print(f"❌ Backup directory not found: {backup_dir}")
        return
    
    backups = []
    for filename in os.listdir(backup_dir):
        if filename.startswith("hrms_backup_") and filename.endswith(".db"):
            file_path = os.path.join(backup_dir, filename)
            file_size = os.path.getsize(file_path) / (1024 * 1024)
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            backups.append({
                'filename': filename,
                'path': file_path,
                'size': file_size,
                'date': file_time
            })
    
    if not backups:
        print("📁 No backups found")
        return
    
    # Sort by date (newest first)
    backups.sort(key=lambda x: x['date'], reverse=True)
    
    print(f"\n📁 Available Backups ({len(backups)} total):")
    print("-" * 80)
    for backup in backups:
        print(f"  {backup['filename']}")
        print(f"    Date: {backup['date'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"    Size: {backup['size']:.2f} MB")
        print()


def restore_backup(backup_file, db_path="instance/hrms.db"):
    """
    Restore database from a backup file
    
    Args:
        backup_file: Path to backup file to restore
        db_path: Path where to restore the database
    """
    if not os.path.exists(backup_file):
        print(f"❌ Backup file not found: {backup_file}")
        return False
    
    # Create backup of current database before restoring
    if os.path.exists(db_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        current_backup = f"backups/before_restore_{timestamp}.db"
        shutil.copy2(db_path, current_backup)
        print(f"✅ Created backup of current database: {current_backup}")
    
    try:
        # Restore the backup
        shutil.copy2(backup_file, db_path)
        print(f"✅ Database restored successfully from {backup_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error during restore: {str(e)}")
        return False


def main():
    """Main function to handle command-line arguments"""
    import argparse
    
    parser = argparse.ArgumentParser(description='HRMS Database Backup Management')
    parser.add_argument('action', 
                       choices=['backup', 'cleanup', 'list', 'restore'],
                       help='Action to perform')
    parser.add_argument('--db-path', 
                       default='instance/hrms.db',
                       help='Path to database file')
    parser.add_argument('--backup-dir', 
                       default='backups',
                       help='Backup directory')
    parser.add_argument('--retention-days', 
                       type=int,
                       default=30,
                       help='Number of days to keep backups (for cleanup)')
    parser.add_argument('--backup-file',
                       help='Backup file to restore (for restore action)')
    
    args = parser.parse_args()
    
    if args.action == 'backup':
        backup_database(args.db_path, args.backup_dir)
        cleanup_old_backups(args.backup_dir, args.retention_days)
        
    elif args.action == 'cleanup':
        cleanup_old_backups(args.backup_dir, args.retention_days)
        
    elif args.action == 'list':
        list_backups(args.backup_dir)
        
    elif args.action == 'restore':
        if not args.backup_file:
            print("❌ Error: --backup-file is required for restore action")
            sys.exit(1)
        restore_backup(args.backup_file, args.db_path)


if __name__ == "__main__":
    # If run without arguments, perform backup
    if len(sys.argv) == 1:
        print("🔄 Starting automatic backup...")
        backup_database()
        cleanup_old_backups()
    else:
        main()


"""
USAGE EXAMPLES:

1. Create a backup (default):
   python backup_db.py

2. Create a backup with custom paths:
   python backup_db.py backup --db-path custom/path/hrms.db --backup-dir my_backups

3. List all backups:
   python backup_db.py list

4. Clean up old backups (older than 30 days):
   python backup_db.py cleanup

5. Clean up old backups (custom retention):
   python backup_db.py cleanup --retention-days 7

6. Restore from a backup:
   python backup_db.py restore --backup-file backups/hrms_backup_20260111_120000.db


SCHEDULING BACKUPS:

Windows (Task Scheduler):
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., Daily at 2:00 AM)
4. Action: Start a program
5. Program: python
6. Arguments: C:\path\to\backup_db.py backup
7. Start in: C:\path\to\project

Linux/Mac (Crontab):
1. Edit crontab: crontab -e
2. Add line: 0 2 * * * cd /path/to/project && python3 backup_db.py backup
   (This runs daily at 2:00 AM)
"""
