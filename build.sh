#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
mkdir -p instance
mkdir -p static/uploads

# Initialize database tables if they don't exist
# db.create_all() ONLY creates tables that don't exist
# It DOES NOT drop or delete existing data
echo "Initializing database tables (existing data will be preserved)..."
python << END
import os
try:
    from app import app, db
    
    db_file = '/opt/render/project/src/instance/catalogos_nuevo.db'
    if os.path.exists(db_file):
        print(f'Database file exists at {db_file} - preserving existing data')
        file_size = os.path.getsize(db_file)
        print(f'Database size: {file_size} bytes')
    else:
        print('Database file does not exist - creating new database')
    
    with app.app_context():
        db.create_all()
        print('Database tables initialized successfully (existing data preserved)')
except Exception as e:
    print(f'Warning: Database initialization failed: {e}')
    print('This may be normal for first deployment')
END
