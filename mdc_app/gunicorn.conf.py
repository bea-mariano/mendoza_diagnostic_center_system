#!/bin/bash
set -e

echo "Starting deployment..."

# Navigate to project directory
cd /home/ubuntu/mendoza_diagnostic_center_system/mdc_app

# Activate virtual environment
source ../venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Run Django commands
python manage.py migrate
python manage.py collectstatic --noinput

# Restart services
sudo systemctl restart mdc-app
sudo systemctl reload nginx

# Check status
echo "Checking service status..."
sudo systemctl is-active mdc-app
sudo systemctl is-active nginx

echo "Deployment completed successfully!"
echo "Your app should be available at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"