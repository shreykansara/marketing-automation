#!/bin/bash
# Start the FastAPI application using Gunicorn with Uvicorn workers for production
gunicorn backend.main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
