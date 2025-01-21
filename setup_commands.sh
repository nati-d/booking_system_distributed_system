# Create a new Django project
django-admin startproject ticketing_notification_service

# Navigate into the project directory
cd ticketing_notification_service

# Create a new Django app
python manage.py startapp notifications

# Install required packages
pip install django djangorestframework celery redis

