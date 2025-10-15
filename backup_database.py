#!/usr/bin/env python3
"""
Database backup utility for the Canteen Kiosk application.
"""

import os
import shutil
from datetime import datetime
import sqlite3
import psycopg2
from config import config

def backup_sqlite_database(db_path, backup_dir='backups'):
    """Backup SQLite database"""
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return False
    
    # Create backup directory
    os.makedirs(backup_dir, exist_ok=True)
    
    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"canteen_backup_{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    try:
        # Copy database file
        shutil.copy2(db_path, backup_path)
        print(f"✅ SQLite backup created: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ Backup failed: {str(e)}")
        return False

def backup_postgresql_database(database_url, backup_dir='backups'):
    """Backup PostgreSQL database using pg_dump"""
    try:
        import subprocess
        
        # Create backup directory
        os.makedirs(backup_dir, exist_ok=True)
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"canteen_postgres_backup_{timestamp}.sql"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Run pg_dump
        cmd = ['pg_dump', database_url]
        with open(backup_path, 'w') as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
        
        if result.returncode == 0:
            print(f"✅ PostgreSQL backup created: {backup_path}")
            return backup_path
        else:
            print(f"❌ PostgreSQL backup failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ PostgreSQL backup failed: {str(e)}")
        return False

def cleanup_old_backups(backup_dir='backups', keep_days=7):
    """Clean up old backup files"""
    if not os.path.exists(backup_dir):
        return
    
    current_time = datetime.now()
    cutoff_time = current_time.timestamp() - (keep_days * 24 * 60 * 60)
    
    deleted_count = 0
    for filename in os.listdir(backup_dir):
        file_path = os.path.join(backup_dir, filename)
        if os.path.isfile(file_path):
            file_time = os.path.getmtime(file_path)
            if file_time < cutoff_time:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                    print(f"🗑️ Deleted old backup: {filename}")
                except Exception as e:
                    print(f"❌ Failed to delete {filename}: {str(e)}")
    
    if deleted_count > 0:
        print(f"✅ Cleaned up {deleted_count} old backup files")

def main():
    """Main backup function"""
    print("🔄 STARTING DATABASE BACKUP")
    print("=" * 40)
    
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    # Determine database type and backup accordingly
    if database_url.startswith('sqlite'):
        # Extract file path from SQLite URL
        db_path = database_url.replace('sqlite:///', '')
        return backup_sqlite_database(db_path)
    elif database_url.startswith('postgresql'):
        return backup_postgresql_database(database_url)
    else:
        print(f"❌ Unsupported database type: {database_url}")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎉 BACKUP COMPLETED SUCCESSFULLY")
        cleanup_old_backups()
    else:
        print("\n⚠️ BACKUP FAILED")
        print("Please check your database configuration and try again.")
