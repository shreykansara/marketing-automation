#!/bin/bash

# Start the FastAPI application for production
# Using 1 worker for Render Free Tier (512MB RAM)
gunicorn -w 1 -k uvicorn.workers.UvicornWorker backend.main:app --bind 0.0.0.0:$PORT
