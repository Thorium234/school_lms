#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Create public directory
mkdir -p public

# Copy static files to public directory
cp -r staticfiles/* public/static/ || true
mkdir -p public/media

# Create vercel required files
echo "from school.wsgi import application" > vercel_app.py

echo "Build completed successfully!"