# SUPABASE SETUP GUIDE

## Step 1: Create Supabase Project

1. **Go to [supabase.com](https://supabase.com)** and sign in/sign up
2. **Click "New Project"**
3. **Fill in the project details:**
   - **Organization**: Select your organization (or create one)
   - **Name**: `AICALS-Courier-DB` (or your preferred name)
   - **Database Password**: Choose a strong password ⚠️ **SAVE THIS PASSWORD!**
   - **Region**: Choose closest to Singapore (since your Render DB is there)
     - Recommended: `Asia Pacific (Singapore)` or `Asia Pacific (Sydney)`
   - **Pricing Plan**: Start with Free tier (sufficient for testing)

4. **Click "Create new project"**
5. **Wait for project creation** (usually takes 1-2 minutes)

## Step 2: Get Connection Details

Once your project is created:

1. **Go to Project Settings** (gear icon in left sidebar)
2. **Click "Database"** in the left menu
3. **Find the "Connection parameters" section**
4. **Copy the connection details:**

   ```
   Host: db.xxxxxxxxxxxxx.supabase.co
   Database name: postgres  
   Port: 5432
   User: postgres
   Password: [the password you chose]
   ```

## Step 3: Get Connection Strings

In the same Database settings page, scroll down to find **"Connection string"** section:

### For Django (recommended):
```
postgresql://postgres:[YOUR-PASSWORD]@db.xxxxxxxxxxxxx.supabase.co:5432/postgres
```

### Connection Pooler Options:
- **Session**: `postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[region].pooler.supabase.com:6543/postgres`
- **Transaction**: `postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[region].pooler.supabase.com:5432/postgres`

**For Django, use the Session pooler (port 6543) for better performance.**

## Step 4: Test Connection

Replace `[YOUR-PASSWORD]` with your actual database password and use the connection string.

**Example:**
```bash
postgresql://postgres:your_secure_password_here@db.abcdefghijklmnop.supabase.co:6543/postgres
```

## Important Notes:

- ✅ **Save your database password** - you cannot retrieve it later
- ✅ **Use Session pooler (port 6543)** for Django applications  
- ✅ **Choose a region close to your users** for better performance
- ✅ **Free tier** gives you:
  - Up to 500MB database
  - Up to 2GB bandwidth
  - Up to 50MB file uploads
  - Sufficient for testing and small production

## Security Best Practices:

1. **Never commit passwords to git**
2. **Use environment variables** for connection strings
3. **Enable Row Level Security (RLS)** if needed
4. **Set up proper authentication** before production

## Next Steps:

Once you have your Supabase connection string:
1. Set it as `DATABASE_URL` environment variable
2. Run the migration test script
3. Verify data import works correctly
4. Plan the production switch

## Troubleshooting:

- **Connection timeout**: Check if your IP is allowed (Supabase allows all IPs by default)
- **Password issues**: Reset password in Database settings
- **SSL errors**: Supabase requires SSL - Django handles this automatically with `dj-database-url`
