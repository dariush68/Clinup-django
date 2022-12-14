#!/bin/bash

# log into docker
#docker exec -t -i 66175bfd6ae6 bash
#or
#docker-compose run web python manage.py migrate

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput

# Apply database migrations
echo "Apply database migrations"
python manage.py makemigrations
python manage.py migrate

# Start server
echo "Starting server"
#python manage.py runserver 0.0.0.0:8000