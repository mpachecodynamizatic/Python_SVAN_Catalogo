#!/usr/bin/env bash
# exit on error
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
mkdir -p instance
mkdir -p static/uploads

# Initialize database if needed
python -c "from app import app, db; 
with app.app_context():
    db.create_all()
    print('Database initialized successfully')"
