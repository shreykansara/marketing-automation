#!/bin/bash

# Start the Celery Worker in the background
echo "Starting Celery Worker..."
celery -A backend.core.celery_app worker --loglevel=info --pool=solo &

# Start the Celery Beat scheduler in the background
echo "Starting Celery Beat..."
celery -A backend.core.celery_app beat --loglevel=info &

# Start the FastAPI application with Gunicorn
echo "Starting FastAPI with Gunicorn..."
gunicorn backend.main:app -w 1 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
