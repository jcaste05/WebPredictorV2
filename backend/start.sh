#!/bin/bash
# start.sh

# Set PYTHONPATH
echo "Setting PYTHONPATH..."
export PYTHONPATH=/app:$PYTHONPATH

# Create the database
echo "Creating database..."
python backend/db/dev_init_db.py

# Start the FastAPI application
echo "Starting API..."
exec uvicorn backend.api.main:app --host 0.0.0.0 --port 8000
