#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
mkdir -p instance
mkdir -p static/uploads

# Initialize database if needed
python << END
try:
    from app import app, db
    with app.app_context():
        db.create_all()
        print('Database initialized successfully')
except Exception as e:
    print(f'Warning: Database initialization failed: {e}')
    print('This is normal for first deployment')
END
