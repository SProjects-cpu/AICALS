"""
WSGI config for CourierManagement project on PythonAnywhere.

This file contains the WSGI application used by PythonAnywhere's web server.
It is specifically configured for deployment on PythonAnywhere.
"""

import os
import sys

# Add the project directory to the Python path
# Replace 'yourusername' with your actual PythonAnywhere username
path = '/home/yourusername/AICALS'
if path not in sys.path:
    sys.path.append(path)

# Set the environment variable for Django settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'CourierManagement.settings'

# Import the Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application() 