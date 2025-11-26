"""
Database Backup Script
Creates a full backup of the PostgreSQL database before upgrades.
"""
import os
import subprocess
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_database_url():
    """Get database URL from environment"""
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("❌ ERROR: DATABASE_URL not found in environment variables")
        print("Please make sure your .env file contains DATABASE_URL")
        return None
    return db_url

def parse_db_url(db_url):
    """Parse PostgreSQL connection URL into components"""
    # Format: postgresql://user:password@host:port/database
    try:
        # Remove postgresql:// prefix
        if db_url.startswith('postgresql://'):
            db_url = db_url.replace('postgresql://', '')
        elif db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', '')
        
        # Split into parts
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

def backup_with_pg_dump(db_info):
    """Create backup using pg_dump command"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'database_backup_{timestamp}.sql'
    
    # Set PGPASSWORD environment variable for pg_dump
    env = os.environ.copy()
    if db_info['password']:
        env['PGPASSWORD'] = db_info['password']
    
    # Build pg_dump command
    cmd = [
        'pg_dump',
        '-h', db_info['host'],
        '-p', str(db_info['port']),
        '-U', db_info['user'],
        '-d', db_info['database'],
        '-F', 'c',  # Custom format (compressed)
        '-f', backup_filename,
        '--verbose'
    ]
    
    print(f"📦 Creating backup: {backup_filename}")
    print(f"   Host: {db_info['host']}")
    print(f"   Database: {db_info['database']}")
    print("   This may take a few minutes...")
    
    try:
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, check=True)
        print(f"✅ Backup created successfully: {backup_filename}")
        print(f"   File size: {os.path.getsize(backup_filename) / 1024 / 1024:.2f} MB")
        return backup_filename
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating backup with pg_dump:")
        print(f"   {e.stderr}")
        return None
    except FileNotFoundError:
        print("❌ pg_dump not found. Trying Python-based backup...")
        return None

def backup_with_python(db_url):
    """Create backup using Python (fallback if pg_dump not available)"""
    try:
        import psycopg2
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    except ImportError:
        print("❌ psycopg2 not installed. Installing...")
        subprocess.run(['pip', 'install', 'psycopg2-binary'], check=True)
        import psycopg2
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'database_backup_{timestamp}.sql'
    
    print(f"📦 Creating backup using Python: {backup_filename}")
    print("   This may take a few minutes...")
    
    try:
        conn = psycopg2.connect(db_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY tablename;
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"   Found {len(tables)} tables to backup")
        
        with open(backup_filename, 'w', encoding='utf-8') as f:
            f.write(f"-- Database Backup\n")
            f.write(f"-- Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"-- Tables: {', '.join(tables)}\n\n")
            
            for table in tables:
                print(f"   Backing up table: {table}")
                # Get table structure
                cursor.execute(f"""
                    SELECT column_name, data_type, character_maximum_length, is_nullable
                    FROM information_schema.columns
                    WHERE table_name = '{table}'
                    ORDER BY ordinal_position;
                """)
                columns = cursor.fetchall()
                
                # Get table data
                cursor.execute(f'SELECT * FROM "{table}"')
                rows = cursor.fetchall()
                
                # Write CREATE TABLE statement
                f.write(f'\n-- Table: {table}\n')
                f.write(f'DROP TABLE IF EXISTS "{table}" CASCADE;\n')
                
                # Build column definitions
                col_defs = []
                for col in columns:
                    col_name, data_type, max_length, is_nullable = col
                    col_def = f'"{col_name}" {data_type}'
                    if max_length:
                        col_def += f'({max_length})'
                    if is_nullable == 'NO':
                        col_def += ' NOT NULL'
                    col_defs.append(col_def)
                
                f.write(f'CREATE TABLE "{table}" (\n')
                f.write(',\n'.join(f'    {col}' for col in col_defs))
                f.write('\n);\n\n')
                
                # Write INSERT statements
                if rows:
                    f.write(f'-- Data for table: {table}\n')
                    for row in rows:
                        values = []
                        for val in row:
                            if val is None:
                                values.append('NULL')
                            elif isinstance(val, str):
                                # Escape single quotes
                                val = val.replace("'", "''")
                                values.append(f"'{val}'")
                            else:
                                values.append(str(val))
                        f.write(f'INSERT INTO "{table}" VALUES ({", ".join(values)});\n')
                    f.write('\n')
        
        cursor.close()
        conn.close()
        
        print(f"✅ Backup created successfully: {backup_filename}")
        print(f"   File size: {os.path.getsize(backup_filename) / 1024 / 1024:.2f} MB")
        return backup_filename
        
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        return None

def main():
    print("=" * 60)
    print("🗄️  Database Backup Tool")
    print("=" * 60)
    print()
    
    db_url = get_database_url()
    if not db_url:
        return
    
    # Try pg_dump first (faster and more reliable)
    db_info = parse_db_url(db_url)
    if db_info and db_info['database']:
        backup_file = backup_with_pg_dump(db_info)
        if backup_file:
            print()
            print("=" * 60)
            print("✅ BACKUP COMPLETE!")
            print("=" * 60)
            print(f"📁 Backup file: {backup_file}")
            print()
            print("💡 To restore this backup:")
            print(f"   pg_restore -d your_database_name {backup_file}")
            print()
            print("   Or use the restore_database.py script")
            return
    
    # Fallback to Python-based backup
    print()
    print("Trying Python-based backup method...")
    backup_file = backup_with_python(db_url)
    
    if backup_file:
        print()
        print("=" * 60)
        print("✅ BACKUP COMPLETE!")
        print("=" * 60)
        print(f"📁 Backup file: {backup_file}")
        print()
        print("💡 To restore this backup:")
        print(f"   psql -d your_database_name -f {backup_file}")
        print()
        print("   Or use the restore_database.py script")
    else:
        print()
        print("❌ Backup failed. Please check the error messages above.")

if __name__ == '__main__':
    main()

