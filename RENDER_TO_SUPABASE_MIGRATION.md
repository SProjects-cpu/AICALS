# AICALS: Render PostgreSQL → Supabase Migration Guide

## 🚨 **CRITICAL: Zero-Downtime Production Migration**

This guide ensures **NO DATA LOSS** during migration from Render PostgreSQL to Supabase PostgreSQL for your live production system.

## 📊 **Current Architecture**
```
✅ PRODUCTION (Live)
Frontend: Render Web Service → Render PostgreSQL (Free Tier)
Domain: www.aicals.com
Status: ⚠️ Active customers using system
```

## 🎯 **Target Architecture**
```
🎯 AFTER MIGRATION
Frontend: Render Web Service → Supabase PostgreSQL
Domain: www.aicals.com
Status: ✅ Zero downtime, all data preserved
```

## 🔄 **Phase 1: Data Backup (ZERO Risk)**

### **Method 1: Django Data Export (Recommended)**

**Step 1A: Connect to Your Live System**
```bash
# Clone your production repository locally
git clone https://github.com/SProjects-cpu/AICALS.git
cd AICALS

# Set up virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r updated_requirements.txt
```

**Step 1B: Configure Connection to Production Database**
```bash
# Get your Render PostgreSQL URL from Render Dashboard
# Go to: Render Dashboard → Your Database → Connection Details
# Copy the "External Database URL"

# Set environment variable (TEMPORARY - for backup only)
$env:DATABASE_URL = "your_render_postgresql_url_here"
```

**Step 1C: Export All Data**
```bash
# Export all application data (SAFE - READ-ONLY operation)
python manage.py dumpdata > production_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').json

# Export specific models for verification
python manage.py dumpdata courier > courier_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').json
python manage.py dumpdata auth.User > users_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').json
```

### **Method 2: PostgreSQL Dump (Alternative)**

**Step 2A: Using pg_dump (if you have access)**
```bash
# If pg_dump is available locally
pg_dump "your_render_postgresql_url" > production_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql

# Compressed backup
pg_dump "your_render_postgresql_url" | gzip > production_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql.gz
```

### **Method 3: Render Dashboard Export (GUI)**

1. **Go to Render Dashboard**
2. **Navigate to your PostgreSQL service**
3. **Look for "Export" or "Backup" options**
4. **Download the backup file**

## 🔄 **Phase 2: Supabase Setup**

### **Step 2A: Create Supabase Project**
```bash
1. Go to: https://supabase.com/
2. Create new project
3. Choose region: ap-south-1 (Mumbai) - same as your current setup
4. Note down connection details
```

### **Step 2B: Get Supabase Connection String**
```bash
# From Supabase Dashboard → Settings → Database
# Use SESSION POOLER for Django (recommended):
postgresql://postgres.[ref]:[password]@aws-0-ap-south-1.pooler.supabase.com:6543/postgres
```

## 🔄 **Phase 3: Test Migration (SAFE Environment)**

### **Step 3A: Local Testing**
```bash
# Set Supabase connection locally
$env:DATABASE_URL = "your_supabase_postgresql_url"

# Run migrations to create schema
python manage.py migrate

# Import your backed up data
python manage.py loaddata production_backup_YYYYMMDD_HHMMSS.json

# Verify data integrity
python manage.py shell
>>> from courier.models import Order, OrderUpdate, Profile
>>> print(f"Orders: {Order.objects.count()}")
>>> print(f"Updates: {OrderUpdate.objects.count()}")
>>> print(f"Users: {Profile.objects.count()}")
```

### **Step 3B: Create Test Superuser**
```bash
# Create admin user in Supabase
python create_superuser.py

# Or manually
python manage.py createsuperuser
```

### **Step 3C: Verification Checklist**
- [ ] All orders imported correctly
- [ ] Order tracking history preserved
- [ ] User accounts and profiles intact
- [ ] Admin panel accessible
- [ ] Customer tracking works
- [ ] All relationships maintained

## 🔄 **Phase 4: Production Migration (Minimal Downtime)**

### **Option A: Zero-Downtime Migration** ⭐ **RECOMMENDED**

**Step 4A: Prepare Environment Variables**
```bash
# Keep these ready for Render Dashboard:
DATABASE_URL=your_supabase_postgresql_connection_string
SECRET_KEY=your_existing_secret_key
DEBUG=False
RENDER_EXTERNAL_HOSTNAME=www.aicals.com
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin@123456
```

**Step 4B: Quick Switch Process**
```bash
⏰ TIMING: Do this during LOW TRAFFIC hours (e.g., 2-4 AM)

1. 🔒 Put site in "Maintenance Mode" (optional)
   - Create a temporary maintenance page
   - Or inform users of brief update

2. 📊 Final data sync
   - Export latest data: python manage.py dumpdata > final_backup.json
   - Import to Supabase: python manage.py loaddata final_backup.json

3. ⚡ Switch Database Connection (< 2 minutes)
   - Go to Render Dashboard → Your Web Service → Environment
   - Update DATABASE_URL to Supabase connection string
   - Click "Deploy" (automatic restart)

4. ✅ Verify and Monitor
   - Test login, tracking, orders
   - Monitor error logs
   - Verify customer functionality

5. 🎉 Go Live
   - Remove maintenance mode
   - Monitor system performance
```

### **Option B: Blue-Green Deployment** (Advanced)

**Step 4C: Parallel Deployment**
```bash
1. Create NEW Render Web Service with Supabase
2. Test thoroughly on staging domain
3. Switch DNS/domain when ready
4. Keep old service as backup for 24-48 hours
```

## 🔄 **Phase 5: Post-Migration Cleanup**

### **Step 5A: Monitor and Verify**
```bash
✅ Check these after migration:
- Customer login/signup works
- Order placement works
- Package tracking works
- Admin panel functional
- No broken functionality
- Performance acceptable
```

### **Step 5B: Cleanup**
```bash
📋 After 48-72 hours of stable operation:
- Remove Render PostgreSQL database service
- Update documentation
- Keep backups for recovery (30+ days)
```

## 🚨 **Emergency Rollback Plan**

### **If Something Goes Wrong:**
```bash
🔄 IMMEDIATE ROLLBACK (< 5 minutes):
1. Go to Render Dashboard
2. Change DATABASE_URL back to original Render PostgreSQL
3. Click "Deploy" 
4. System returns to original state
5. No data lost (original database unchanged)

💾 DATA RECOVERY:
1. Original Render database still intact
2. All backups available for restore
3. Can retry migration after fixing issues
```

## 📋 **Migration Checklist**

### **Pre-Migration**
- [ ] Export production data successfully
- [ ] Test import on local Supabase
- [ ] Verify all data integrity
- [ ] Create Supabase project in correct region
- [ ] Test connection strings work
- [ ] Plan maintenance window (optional)

### **During Migration**
- [ ] Final data export from production
- [ ] Import to Supabase
- [ ] Update Render environment variables
- [ ] Deploy and verify functionality
- [ ] Monitor for issues

### **Post-Migration**
- [ ] Customer functionality verified
- [ ] Admin panel working
- [ ] Performance monitoring
- [ ] Keep old database for 48+ hours
- [ ] Update documentation

## 🛠️ **Troubleshooting Common Issues**

### **Connection Issues**
```bash
# If connection fails, check:
1. Supabase URL format correct
2. SSL settings in Django
3. Firewall/security group settings
4. Connection pooling vs direct connection
```

### **Data Import Issues**
```bash
# If loaddata fails:
1. Check Django version compatibility
2. Handle foreign key constraints
3. Import in correct order (users → profiles → orders → updates)
4. Use --verbosity=2 for detailed output
```

### **Performance Issues**
```bash
# If slower than expected:
1. Use connection pooling URL
2. Check Supabase region matches
3. Monitor connection count
4. Consider Session pooler vs Transaction pooler
```

## 📞 **Support and Recovery**

### **Emergency Contacts**
- **Immediate Issue**: Rollback to original database
- **Data Recovery**: Use backed up JSON files
- **Technical Support**: Supabase support for database issues

### **Backup Strategy Going Forward**
```bash
# Set up regular backups
1. Weekly automated exports: python manage.py dumpdata
2. Monthly full database dumps
3. Keep 3 months of backups minimum
4. Store backups in multiple locations
```

## 🎯 **Expected Benefits After Migration**

### **Immediate Benefits**
- ✅ **500MB storage** vs 100MB on Render free tier
- ✅ **60 concurrent connections** vs limited on Render
- ✅ **24/7 availability** - no database sleep
- ✅ **Better performance** with dedicated PostgreSQL
- ✅ **Advanced monitoring** via Supabase dashboard

### **Long-term Benefits**
- 🚀 **Scalability**: Easy to upgrade as business grows
- 🔧 **Additional Features**: Built-in auth, real-time, storage
- 📊 **Better Analytics**: Advanced database insights
- 💰 **Cost Effective**: Better free tier limits
- 🔒 **Enhanced Security**: Enterprise-grade PostgreSQL

## ⚠️ **Important Notes**

1. **No Customer Impact**: Migration designed for zero downtime
2. **Data Safety**: Original database remains until cleanup
3. **Rollback Ready**: Can revert in under 5 minutes if needed
4. **Testing**: Everything tested locally before production
5. **Monitoring**: Close monitoring for 48+ hours post-migration

## 📅 **Recommended Timeline**

```bash
Day 1: Data backup and Supabase setup
Day 2: Local testing and verification
Day 3: Production migration (during low traffic)
Day 4-5: Monitoring and optimization
Day 7: Cleanup and documentation update
```

**This migration plan ensures your customers experience NO disruption while gaining significantly better database performance and reliability!** 🚀
