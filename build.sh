#!/usr/bin/env bash
# Exit on error
set -o errexit

pip install -r updated_requirements.txt

# Create the directory and the missing SVG file
mkdir -p courier/static/courier/css/
touch courier/static/courier/css/mejs-controls.svg

# Create an empty SVG file with basic content
cat > courier/static/courier/css/mejs-controls.svg << 'EOL'
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="400" height="120" viewBox="0 0 400 120">
  <!-- Media player controls -->
  <g id="controls">
    <circle cx="20" cy="20" r="15" fill="none" stroke="white" stroke-width="2"/>
    <polygon points="15,12 28,20 15,28" fill="white"/>
  </g>
</svg>
EOL

python manage.py collectstatic --no-input
python manage.py migrate

# Create superuser automatically
python create_superuser.py 