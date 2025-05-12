# Setting Up Django Admin User in Render

Since Render's free plan doesn't provide shell access, we've implemented an automated solution to create a superuser during deployment.

## How It Works

The `create_superuser.py` script is run during deployment and creates an admin user automatically. By default, it uses these credentials:

- **Username**: admin
- **Email**: admin@example.com
- **Password**: admin@123

## Customizing Admin Credentials

For security reasons, you should set your own admin credentials using environment variables in Render:

1. Log in to your Render dashboard
2. Navigate to your web service
3. Go to the "Environment" tab
4. Add the following environment variables:
   - `ADMIN_USERNAME`: Your desired admin username
   - `ADMIN_EMAIL`: Your admin email address
   - `ADMIN_PASSWORD`: Your secure admin password

## Important Security Notes

1. **Change the default credentials**: Always change the default admin credentials by setting environment variables
2. **Use a strong password**: Make sure your admin password is secure
3. **Limited permissions**: Consider creating additional staff users with limited permissions for day-to-day operations

## Accessing the Admin Panel

After deployment, you can access the Django admin panel at:
`https://your-app-name.onrender.com/admin/`

## Troubleshooting

If you encounter issues with admin user creation:

1. Check the deployment logs for any errors
2. Verify your environment variables are set correctly
3. If necessary, you can manually redeploy to trigger the admin user creation again 