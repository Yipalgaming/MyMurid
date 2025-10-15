#!/usr/bin/env python3
"""
Performance monitoring utility for the Canteen Kiosk application.
"""

import time
import psutil
import os
from datetime import datetime
import sqlite3
import psycopg2
from config import config

class PerformanceMonitor:
    """Monitor application performance metrics"""
    
    def __init__(self):
        self.start_time = time.time()
        self.metrics = {}
    
    def get_system_metrics(self):
        """Get system performance metrics"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'uptime': time.time() - self.start_time
        }
    
    def get_database_metrics(self):
        """Get database performance metrics"""
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            return {'error': 'No database URL found'}
        
        try:
            if database_url.startswith('sqlite'):
                return self._get_sqlite_metrics(database_url)
            elif database_url.startswith('postgresql'):
                return self._get_postgresql_metrics(database_url)
            else:
                return {'error': 'Unsupported database type'}
        except Exception as e:
            return {'error': str(e)}
    
    def _get_sqlite_metrics(self, database_url):
        """Get SQLite specific metrics"""
        db_path = database_url.replace('sqlite:///', '')
        if not os.path.exists(db_path):
            return {'error': 'Database file not found'}
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get database size
            db_size = os.path.getsize(db_path)
            
            # Get table counts
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            table_counts = {}
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                table_counts[table_name] = count
            
            conn.close()
            
            return {
                'database_size_mb': round(db_size / (1024 * 1024), 2),
                'table_counts': table_counts,
                'total_records': sum(table_counts.values())
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _get_postgresql_metrics(self, database_url):
        """Get PostgreSQL specific metrics"""
        try:
            conn = psycopg2.connect(database_url)
            cursor = conn.cursor()
            
            # Get database size
            cursor.execute("SELECT pg_size_pretty(pg_database_size(current_database()))")
            db_size = cursor.fetchone()[0]
            
            # Get table counts
            cursor.execute("""
                SELECT schemaname, tablename, n_tup_ins, n_tup_upd, n_tup_del, n_live_tup, n_dead_tup
                FROM pg_stat_user_tables
            """)
            tables = cursor.fetchall()
            
            table_info = {}
            total_records = 0
            for table in tables:
                schema, name, inserts, updates, deletes, live_tuples, dead_tuples = table
                table_info[f"{schema}.{name}"] = {
                    'live_tuples': live_tuples,
                    'dead_tuples': dead_tuples,
                    'inserts': inserts,
                    'updates': updates,
                    'deletes': deletes
                }
                total_records += live_tuples
            
            conn.close()
            
            return {
                'database_size': db_size,
                'table_info': table_info,
                'total_records': total_records
            }
        except Exception as e:
            return {'error': str(e)}
    
    def check_performance_thresholds(self):
        """Check if performance metrics exceed thresholds"""
        system_metrics = self.get_system_metrics()
        warnings = []
        
        if system_metrics['cpu_percent'] > 80:
            warnings.append(f"High CPU usage: {system_metrics['cpu_percent']:.1f}%")
        
        if system_metrics['memory_percent'] > 85:
            warnings.append(f"High memory usage: {system_metrics['memory_percent']:.1f}%")
        
        if system_metrics['disk_usage'] > 90:
            warnings.append(f"High disk usage: {system_metrics['disk_usage']:.1f}%")
        
        return warnings
    
    def generate_report(self):
        """Generate a comprehensive performance report"""
        print("📊 PERFORMANCE MONITORING REPORT")
        print("=" * 50)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # System metrics
        print("🖥️ SYSTEM METRICS:")
        system_metrics = self.get_system_metrics()
        for key, value in system_metrics.items():
            if key == 'uptime':
                print(f"  {key}: {value:.1f} seconds")
            else:
                print(f"  {key}: {value:.1f}%")
        print()
        
        # Database metrics
        print("🗄️ DATABASE METRICS:")
        db_metrics = self.get_database_metrics()
        if 'error' in db_metrics:
            print(f"  Error: {db_metrics['error']}")
        else:
            for key, value in db_metrics.items():
                if isinstance(value, dict):
                    print(f"  {key}:")
                    for sub_key, sub_value in value.items():
                        print(f"    {sub_key}: {sub_value}")
                else:
                    print(f"  {key}: {value}")
        print()
        
        # Performance warnings
        warnings = self.check_performance_thresholds()
        if warnings:
            print("⚠️ PERFORMANCE WARNINGS:")
            for warning in warnings:
                print(f"  - {warning}")
        else:
            print("✅ All performance metrics are within normal ranges")
        print()

def main():
    """Main monitoring function"""
    monitor = PerformanceMonitor()
    monitor.generate_report()

if __name__ == "__main__":
    main()
