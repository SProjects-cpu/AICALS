# GitHub Deployment Guide for Courier Management System

This guide explains how to prepare your project for GitHub deployment and subsequent Render hosting.

## 1. Prepare Files for GitHub

### Create a ZIP File

1. Include these essential files and directories:
   - `courier/` - The main app directory
   - `CourierManagement/` - The project directory
   - `templates/` - Global templates
   - `staticfiles/` - Compiled static files
   - `manage.py` - Django management script
   - `build.sh` - Render build script
   - `create_superuser.py` - Admin user creation script
   - `updated_requirements.txt` - Dependencies
   - `render.yaml` - Render configuration
   - `.gitignore` - Git ignore rules
   - `README.md` - Project documentation
   - `DEPLOY_TO_RENDER.md` - Render deployment guide
   - `SUPERUSER_SETUP.md` - Admin setup guide
   - Any other essential configuration files

2. Exclude these files/directories (already in .gitignore):
   - `db.sqlite3` - Local database (PostgreSQL will be used instead)
   - `__pycache__/` directories and `.pyc` files - Compiled Python files
   - `newenv/` and other virtual environment directories
   - Local media files (user uploads)
   - Any sensitive information files

### Ensure File Permissions

Make sure `build.sh` has executable permissions:
```bash
chmod +x build.sh
```

## 2. GitHub Repository Setup

1. **Create a new GitHub repository**:
   - Go to [GitHub](https://github.com) and sign in
   - Click the '+' icon and select "New repository"
   - Name your repository (e.g., "courier-management-system")
   - Add a description (optional)
   - Choose public or private visibility
   - Do NOT initialize with README, .gitignore, or license
   - Click "Create repository"

2. **Initialize your local repository**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

3. **Connect to GitHub and push**:
   ```bash
   git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
   git branch -M main
   git push -u origin main
   ```

## 3. Connect Render to GitHub

1. Log in to your Render dashboard
2. Click "New" and select "Web Service"
3. Choose "Build and deploy from a Git repository"
4. Connect your GitHub account if not already connected
5. Select your repository
6. Render will automatically detect the `render.yaml` file
7. Click "Approve" to create the services defined in the YAML

## 4. Monitor Deployment

1. Render will automatically start building and deploying your application
2. Monitor the build logs for any errors
3. Once deployment is successful, your app will be available at your Render URL
4. PostgreSQL database will be automatically created and linked

## 5. Post-Deployment Steps

1. Set secure environment variables in the Render dashboard
   - Update admin credentials (username, email, password)
   - Set any other sensitive environment variables
2. Test your application functionality thoroughly
3. Set up custom domain if needed

---

## Note for Free Tier Users

Since you're using Render's free plan without shell access:

1. Ensure all migrations and setup scripts work automatically
2. Use the automatic deployment from GitHub
3. Any database data migration must be handled through the deployment scripts
4. Monitor logs through the Render dashboard 