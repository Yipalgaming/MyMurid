"""
Database Restore Script
Restores a database backup created by backup_database.py
"""
import os
import subprocess
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_database_url():
    """Get database URL from environment"""
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("❌ ERROR: DATABASE_URL not found in environment variables")
        return None
    return db_url

def parse_db_url(db_url):
    """Parse PostgreSQL connection URL into components"""
    try:
        if db_url.startswith('postgresql://'):
            db_url = db_url.replace('postgresql://', '')
        elif db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', '')
        
        if '@' in db_url:
            auth, rest = db_url.split('@', 1)
            user, password = auth.split(':', 1)
        else:
            user = None
            password = None
            rest = db_url
        
        if '/' in rest:
            host_port, database = rest.rsplit('/', 1)
            if ':' in host_port:
                host, port = host_port.split(':', 1)
            else:
                host = host_port
                port = '5432'
        else:
            host = rest
            port = '5432'
            database = None
        
        return {
            'user': user,
            'password': password,
            'host': host,
            'port': port,
            'database': database
        }
    except Exception as e:
        print(f"❌ Error parsing database URL: {e}")
        return None

def restore_backup(backup_file, db_info):
    """Restore database from backup file"""
    if not os.path.exists(backup_file):
        print(f"❌ Backup file not found: {backup_file}")
        return False
    
    print("=" * 60)
    print("⚠️  WARNING: This will OVERWRITE your current database!")
    print("=" * 60)
    print(f"   Backup file: {backup_file}")
    print(f"   Database: {db_info['database']}")
    print(f"   Host: {db_info['host']}")
    print()
    
    confirm = input("Type 'YES' to confirm restore: ")
    if confirm != 'YES':
        print("❌ Restore cancelled.")
        return False
    
    # Check if backup is custom format (.sql) or plain SQL
    is_custom_format = backup_file.endswith('.sql') and os.path.getsize(backup_file) < 1000000
    
    env = os.environ.copy()
    if db_info['password']:
        env['PGPASSWORD'] = db_info['password']
    
    if is_custom_format or backup_file.endswith('.dump'):
        # Use pg_restore for custom format
        cmd = [
            'pg_restore',
            '-h', db_info['host'],
            '-p', str(db_info['port']),
            '-U', db_info['user'],
            '-d', db_info['database'],
            '--clean',  # Drop objects before recreating
            '--if-exists',  # Don't error if object doesn't exist
            '--verbose',
            backup_file
        ]
    else:
        # Use psql for plain SQL
        cmd = [
            'psql',
            '-h', db_info['host'],
            '-p', str(db_info['port']),
            '-U', db_info['user'],
            '-d', db_info['database'],
            '-f', backup_file
        ]
    
    print()
    print("🔄 Restoring database...")
    print("   This may take several minutes...")
    
    try:
        result = subprocess.run(cmd, env=env, check=True)
        print()
        print("=" * 60)
        print("✅ RESTORE COMPLETE!")
        print("=" * 60)
        print("Your database has been restored from the backup.")
        return True
    except subprocess.CalledProcessError as e:
        print()
        print("❌ Error restoring database:")
        print(f"   {e}")
        return False
    except FileNotFoundError:
        print("❌ pg_restore or psql not found.")
        print("   Please install PostgreSQL client tools.")
        return False

def list_backups():
    """List available backup files"""
    backups = [f for f in os.listdir('.') if f.startswith('database_backup_') and (f.endswith('.sql') or f.endswith('.dump'))]
    if not backups:
        print("No backup files found in current directory.")
        return None
    
    backups.sort(reverse=True)  # Most recent first
    print("Available backups:")
    for i, backup in enumerate(backups, 1):
        size = os.path.getsize(backup) / 1024 / 1024
        print(f"  {i}. {backup} ({size:.2f} MB)")
    return backups

def main():
    print("=" * 60)
    print("🔄 Database Restore Tool")
    print("=" * 60)
    print()
    
    # List available backups
    backups = list_backups()
    if not backups:
        print()
        print("Please create a backup first using backup_database.py")
        return
    
    print()
    choice = input("Enter backup number to restore (or filename): ").strip()
    
    # Try to parse as number
    try:
        backup_index = int(choice) - 1
        if 0 <= backup_index < len(backups):
            backup_file = backups[backup_index]
        else:
            print("❌ Invalid backup number")
            return
    except ValueError:
        # Assume it's a filename
        backup_file = choice
        if not os.path.exists(backup_file):
            print(f"❌ Backup file not found: {backup_file}")
            return
    
    db_url = get_database_url()
    if not db_url:
        return
    
    db_info = parse_db_url(db_url)
    if not db_info or not db_info['database']:
        print("❌ Could not parse database URL")
        return
    
    restore_backup(backup_file, db_info)

if __name__ == '__main__':
    main()

