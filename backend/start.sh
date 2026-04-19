#!/bin/bash

# 1. Start Celery Beat (Background)
echo "Starting Celery Beat..."
celery -A backend.core.celery_app beat --loglevel=info &

# 2. Start Celery Worker (Background)
echo "Starting Celery Worker..."
celery -A backend.core.celery_app worker --loglevel=info --pool=solo &

# 3. Start a dummy health-check server on $PORT (Foreground)
# This keeps Render happy by listening to their requested port on the Free Tier.
echo "Starting Dummy Health Check Server on port $PORT..."
python -m http.server $PORT
