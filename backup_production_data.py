#!/usr/bin/env python
"""
AICALS Production Data Backup Script
====================================

This script safely backs up all data from your live Render PostgreSQL database
without affecting your production system or customers.

SAFETY FEATURES:
- READ-ONLY operations only
- No modifications to production data
- Detailed logging and verification
- Multiple backup formats
- Data integrity checks

Usage:
    python backup_production_data.py
"""

import os
import sys
import json
import django
from django.core.management import call_command
from django.db import connection
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'backup_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProductionBackup:
    def __init__(self):
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.backup_dir = f"production_backup_{self.timestamp}"
        self.create_backup_directory()
        
    def create_backup_directory(self):
        """Create backup directory if it doesn't exist"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            logger.info(f"Created backup directory: {self.backup_dir}")
    
    def check_database_connection(self):
        """Verify connection to production database"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version()")
                version = cursor.fetchone()[0]
                logger.info(f"✅ Connected to: {version}")
                return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {str(e)}")
            return False
    
    def get_database_stats(self):
        """Get statistics about the database"""
        try:
            # Django ORM imports
            from courier.models import Order, OrderUpdate, Profile, Contact, Product, Pending_order, Shipping
            from django.contrib.auth.models import User
            
            stats = {
                'users': User.objects.count(),
                'profiles': Profile.objects.count(),
                'orders': Order.objects.count(),
                'order_updates': OrderUpdate.objects.count(),
                'contacts': Contact.objects.count(),
                'products': Product.objects.count(),
                'pending_orders': Pending_order.objects.count(),
                'shipping_records': Shipping.objects.count(),
            }
            
            logger.info("📊 Database Statistics:")
            for key, value in stats.items():
                logger.info(f"   {key}: {value} records")
                
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to get database stats: {str(e)}")
            return {}
    
    def backup_all_data(self):
        """Create comprehensive backup of all data"""
        try:
            backup_file = os.path.join(self.backup_dir, f"complete_backup_{self.timestamp}.json")
            
            logger.info("📦 Creating complete database backup...")
            
            with open(backup_file, 'w') as f:
                call_command('dumpdata', 
                           stdout=f,
                           verbosity=2,
                           indent=2)
            
            # Check file size
            file_size = os.path.getsize(backup_file)
            logger.info(f"✅ Complete backup created: {backup_file}")
            logger.info(f"   File size: {file_size / 1024 / 1024:.2f} MB")
            
            return backup_file
            
        except Exception as e:
            logger.error(f"❌ Complete backup failed: {str(e)}")
            return None
    
    def backup_by_app(self):
        """Create separate backups for each app"""
        try:
            backups = {}
            
            # Backup courier app data
            courier_file = os.path.join(self.backup_dir, f"courier_data_{self.timestamp}.json")
            logger.info("📦 Backing up courier app data...")
            
            with open(courier_file, 'w') as f:
                call_command('dumpdata', 'courier',
                           stdout=f,
                           verbosity=1,
                           indent=2)
            backups['courier'] = courier_file
            
            # Backup user data
            users_file = os.path.join(self.backup_dir, f"users_data_{self.timestamp}.json")
            logger.info("📦 Backing up user data...")
            
            with open(users_file, 'w') as f:
                call_command('dumpdata', 'auth.User',
                           stdout=f,
                           verbosity=1,
                           indent=2)
            backups['users'] = users_file
            
            # Backup sessions (optional)
            sessions_file = os.path.join(self.backup_dir, f"sessions_data_{self.timestamp}.json")
            logger.info("📦 Backing up session data...")
            
            with open(sessions_file, 'w') as f:
                call_command('dumpdata', 'sessions',
                           stdout=f,
                           verbosity=1,
                           indent=2)
            backups['sessions'] = sessions_file
            
            logger.info("✅ App-specific backups completed")
            return backups
            
        except Exception as e:
            logger.error(f"❌ App-specific backup failed: {str(e)}")
            return {}
    
    def create_metadata_file(self, stats, backup_files):
        """Create metadata file with backup information"""
        try:
            metadata_file = os.path.join(self.backup_dir, f"backup_metadata_{self.timestamp}.json")
            
            metadata = {
                'backup_timestamp': self.timestamp,
                'backup_date': datetime.now().isoformat(),
                'database_stats': stats,
                'backup_files': backup_files,
                'django_version': django.get_version(),
                'python_version': sys.version,
                'backup_method': 'Django dumpdata',
                'source_database': 'Render PostgreSQL',
                'target_database': 'Supabase PostgreSQL (migration)',
                'status': 'completed'
            }
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2, default=str)
            
            logger.info(f"✅ Metadata file created: {metadata_file}")
            return metadata_file
            
        except Exception as e:
            logger.error(f"❌ Failed to create metadata: {str(e)}")
            return None
    
    def verify_backup_integrity(self, backup_file):
        """Verify backup file integrity"""
        try:
            logger.info("🔍 Verifying backup integrity...")
            
            # Check if file exists and is not empty
            if not os.path.exists(backup_file):
                logger.error(f"❌ Backup file not found: {backup_file}")
                return False
            
            file_size = os.path.getsize(backup_file)
            if file_size == 0:
                logger.error(f"❌ Backup file is empty: {backup_file}")
                return False
            
            # Try to load JSON to verify format
            with open(backup_file, 'r') as f:
                data = json.load(f)
                record_count = len(data)
                
            logger.info(f"✅ Backup verification successful:")
            logger.info(f"   File size: {file_size / 1024 / 1024:.2f} MB")
            logger.info(f"   Records: {record_count}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Backup verification failed: {str(e)}")
            return False
    
    def run_backup(self):
        """Execute the complete backup process"""
        logger.info("🚀 Starting AICALS Production Backup Process")
        logger.info("=" * 60)
        
        # Check database connection
        if not self.check_database_connection():
            logger.error("❌ Cannot proceed without database connection")
            return False
        
        # Get database statistics
        stats = self.get_database_stats()
        if not stats:
            logger.warning("⚠️ Could not retrieve database statistics")
        
        # Create complete backup
        complete_backup = self.backup_all_data()
        if not complete_backup:
            logger.error("❌ Failed to create complete backup")
            return False
        
        # Create app-specific backups
        app_backups = self.backup_by_app()
        
        # Verify backup integrity
        if not self.verify_backup_integrity(complete_backup):
            logger.error("❌ Backup integrity verification failed")
            return False
        
        # Create metadata file
        all_backups = {'complete': complete_backup}
        all_backups.update(app_backups)
        
        metadata_file = self.create_metadata_file(stats, all_backups)
        
        # Success summary
        logger.info("=" * 60)
        logger.info("🎉 BACKUP COMPLETED SUCCESSFULLY!")
        logger.info(f"📁 Backup directory: {self.backup_dir}")
        logger.info("📋 Files created:")
        for name, file_path in all_backups.items():
            if file_path and os.path.exists(file_path):
                size_mb = os.path.getsize(file_path) / 1024 / 1024
                logger.info(f"   {name}: {os.path.basename(file_path)} ({size_mb:.2f} MB)")
        
        if metadata_file:
            logger.info(f"   metadata: {os.path.basename(metadata_file)}")
        
        logger.info("\n📋 Next Steps:")
        logger.info("1. Verify all backup files are created")
        logger.info("2. Test restore on local Supabase database")
        logger.info("3. Proceed with migration when ready")
        logger.info("4. Keep backups safe for emergency recovery")
        
        return True

def main():
    """Main backup execution"""
    print("🚀 AICALS Production Database Backup")
    print("=" * 50)
    
    # Check if DATABASE_URL is set
    if not os.environ.get('DATABASE_URL'):
        print("❌ ERROR: DATABASE_URL environment variable not set!")
        print("\nPlease set your Render PostgreSQL URL:")
        print("$env:DATABASE_URL = 'your_render_postgresql_url'")
        sys.exit(1)
    
    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CourierManagement.settings')
    django.setup()
    
    # Create backup instance and run
    backup = ProductionBackup()
    success = backup.run_backup()
    
    if success:
        print("\n✅ Backup completed successfully!")
        print("Your production data is safely backed up and ready for migration.")
        sys.exit(0)
    else:
        print("\n❌ Backup failed!")
        print("Please check the log files for details and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
