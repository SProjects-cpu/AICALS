import os
import django
from django.conf import settings

# Configure settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CourierManagement.settings')
django.setup()

# Import User model
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

User = get_user_model()

# Define admin credentials
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin@123')

# Create superuser if not exists
try:
    if not User.objects.filter(username=ADMIN_USERNAME).exists():
        User.objects.create_superuser(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            password=ADMIN_PASSWORD
        )
        print(f"Superuser '{ADMIN_USERNAME}' created successfully!")
    else:
        print(f"Superuser '{ADMIN_USERNAME}' already exists.")
except IntegrityError:
    print(f"Could not create superuser '{ADMIN_USERNAME}'. User might already exist with different credentials.")
except Exception as e:
    print(f"An error occurred while creating superuser: {str(e)}") 