#!/usr/bin/env python3
"""
Production Migration Monitor
============================

This script monitors the live site after migration to ensure everything is working.
"""

import requests
import time
from datetime import datetime
import sys

class MigrationMonitor:
    def __init__(self, site_url="https://aicals.com"):
        self.site_url = site_url
        self.start_time = datetime.now()
        
    def check_site_health(self):
        """Check if the main site is responding"""
        try:
            print(f"\n🌐 Testing {self.site_url}...")
            response = requests.get(self.site_url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Site responding: {response.status_code}")
                print(f"⏱️  Response time: {response.elapsed.total_seconds():.2f}s")
                return True
            else:
                print(f"⚠️  Site returned: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Site unreachable: {str(e)}")
            return False
    
    def check_database_pages(self):
        """Check pages that require database access"""
        test_pages = [
            "/",  # Home page
            "/track/",  # Track orders page
        ]
        
        results = []
        for page in test_pages:
            try:
                url = self.site_url + page
                print(f"🔍 Testing {url}...")
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    print(f"✅ Page OK: {page}")
                    results.append(True)
                else:
                    print(f"⚠️  Page issue: {page} - Status: {response.status_code}")
                    results.append(False)
                    
            except Exception as e:
                print(f"❌ Page failed: {page} - Error: {str(e)}")
                results.append(False)
        
        return all(results)
    
    def monitor_continuous(self, duration_minutes=30, check_interval=60):
        """Monitor the site continuously for a specified duration"""
        print(f"🕐 Starting continuous monitoring for {duration_minutes} minutes...")
        print(f"📊 Checking every {check_interval} seconds")
        print("=" * 60)
        
        end_time = datetime.now().timestamp() + (duration_minutes * 60)
        check_count = 0
        success_count = 0
        
        while datetime.now().timestamp() < end_time:
            check_count += 1
            print(f"\n🔍 Health Check #{check_count} at {datetime.now().strftime('%H:%M:%S')}")
            
            site_ok = self.check_site_health()
            db_ok = self.check_database_pages()
            
            if site_ok and db_ok:
                success_count += 1
                print("✅ All systems operational")
            else:
                print("❌ Issues detected!")
                
            # Show progress
            elapsed = datetime.now() - self.start_time
            remaining = duration_minutes - (elapsed.total_seconds() / 60)
            success_rate = (success_count / check_count) * 100
            
            print(f"📊 Success rate: {success_rate:.1f}% ({success_count}/{check_count})")
            print(f"⏱️  Time remaining: {remaining:.1f} minutes")
            
            if remaining > 1:  # Don't sleep on the last check
                print(f"😴 Next check in {check_interval} seconds...")
                time.sleep(check_interval)
        
        print("\n" + "=" * 60)
        print(f"🎯 Monitoring Complete!")
        print(f"📊 Final Success Rate: {success_rate:.1f}% ({success_count}/{check_count})")
        
        if success_rate >= 95:
            print("🎉 MIGRATION SUCCESSFUL - Site is stable!")
            return True
        else:
            print("⚠️  MIGRATION NEEDS ATTENTION - Issues detected!")
            return False
    
    def quick_test(self):
        """Run a quick test to verify migration success"""
        print("🚀 Quick Migration Test")
        print("=" * 30)
        
        site_ok = self.check_site_health()
        db_ok = self.check_database_pages()
        
        if site_ok and db_ok:
            print("\n✅ QUICK TEST PASSED")
            print("🎉 Migration appears successful!")
            print("💡 Consider running continuous monitoring for 30 minutes")
            return True
        else:
            print("\n❌ QUICK TEST FAILED")
            print("🚨 Migration may have issues - check immediately!")
            return False

def main():
    monitor = MigrationMonitor()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--continuous":
            duration = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            return monitor.monitor_continuous(duration_minutes=duration)
        elif sys.argv[1] == "--quick":
            return monitor.quick_test()
    
    # Default: quick test
    return monitor.quick_test()

if __name__ == "__main__":
    success = main()
    print(f"\nMonitoring completed: {'SUCCESS' if success else 'ISSUES DETECTED'}")
    sys.exit(0 if success else 1)
