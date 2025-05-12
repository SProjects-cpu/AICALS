# Deploying Courier Management System to Render

This guide will walk you through deploying this Django application to Render.com with PostgreSQL database.

## QuickStart Guide

For the fastest deployment process:

1. **Prepare Your Project**:
   - Run `prepare_render_zip.bat` to clean the project and create a ZIP file
   - Alternatively, follow the instructions in `ZIP_CREATION.md`

2. **GitHub Setup**:
   - Create a new GitHub repository
   - Upload your project files (follow `GITHUB_DEPLOYMENT.md`)

3. **Render Deployment**:
   - Connect your GitHub repo to Render
   - Render will use the `render.yaml` file to set up the web service and database
   - The project will be deployed automatically with PostgreSQL

4. **Post-Deployment**:
   - Update admin credentials through the Render dashboard
   - Test your application

## Prerequisites

1. A [Render account](https://render.com)
2. Your code pushed to a Git repository (GitHub, GitLab, or Bitbucket)

## Deployment Steps

### 1. Create a Web Service on Render

1. Log in to your Render dashboard
2. Click "New" and select "Web Service"
3. Connect your Git repository that contains this project
4. Configure the service:
   - **Name**: courier-management-system (or your preferred name)
   - **Environment**: Python 3
   - **Region**: Choose the one closest to your users
   - **Branch**: main (or your default branch)
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn CourierManagement.wsgi:application`
   - **Plan**: Select your preferred plan (Free is available)

### 2. Create a PostgreSQL Database

1. In your Render dashboard, click "New" and select "PostgreSQL"
2. Configure the database:
   - **Name**: courier_db (or your preferred name)
   - **Database**: courier_db
   - **User**: courier_admin
   - **Region**: Choose the same region as your web service
   - **Plan**: Select your preferred plan

3. Click "Create Database"
4. Once created, note the "Internal Database URL" - this will be automatically linked to your application through the render.yaml configuration

### 3. Configure Environment Variables

The render.yaml file will automatically set up the following environment variables:

- `SECRET_KEY`: A secure random string (Render will generate this for you)
- `DEBUG`: Set to 'False' for production
- `PYTHON_VERSION`: 3.10.0 (or your preferred version)
- `DATABASE_URL`: The internal connection string to your PostgreSQL database

### 4. Deploy Your Application

1. Click "Create Web Service"
2. If you're using the render.yaml file (recommended), Render will automatically:
   - Create the PostgreSQL database
   - Configure the environment variables
   - Link the database to your web service
3. Wait for the build and deployment to complete
4. Your app will be available at https://your-service-name.onrender.com

## Post-Deployment Steps

1. Initial Database Migration:
   - The database migrations and superuser creation will happen automatically during deployment
   - The automated script will create a superuser with the credentials specified in your environment variables
   - See [SUPERUSER_SETUP.md](SUPERUSER_SETUP.md) for customizing admin credentials

2. Verify static files are loading correctly
3. Test all functionality of your application
4. Access the admin panel at https://your-service-name.onrender.com/admin/

## Environment Variables

The render.yaml file automatically sets up these environment variables:

- `SECRET_KEY`: A secure random string (Render will generate this for you)
- `DEBUG`: Set to 'False' for production
- `PYTHON_VERSION`: 3.10.0 (or your preferred version)
- `DATABASE_URL`: The internal connection string to your PostgreSQL database
- `ADMIN_USERNAME`: Default admin username (change in production)
- `ADMIN_EMAIL`: Default admin email (change in production)
- `ADMIN_PASSWORD`: Default admin password (change in production)

## Data Migration (If Migrating from SQLite)

If you're migrating from SQLite to PostgreSQL, follow these steps:

1. On your local machine, dump your SQLite data:
   ```
   python manage.py dumpdata --exclude auth.permission --exclude contenttypes > data.json
   ```

2. Push this file to your repository

3. On Render Shell, load the data:
   ```
   python manage.py loaddata data.json
   ```

## Troubleshooting

If you encounter issues:

1. Check the logs in the Render dashboard
2. Ensure all environment variables are set correctly
3. Verify database connection is working
4. Check that whitenoise is configured correctly for static files

## Maintaining Your Deployment

- Updates to your app will automatically deploy when you push changes to your repository
- Monitor your app's performance in the Render dashboard
- Regularly backup your PostgreSQL database using Render's backup features 