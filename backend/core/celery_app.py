import os
from celery import Celery
from dotenv import load_dotenv

# Load .env from project root
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(base_dir, ".env")
load_dotenv(env_path)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "blostem_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["backend.tasks.signals", "backend.tasks.tracker"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    beat_schedule={
        "cluster-signals-every-10-min": {
            "task": "periodic_clustering_task",
            "schedule": 600.0, # 10 minutes
        },
        "poll-replies-every-5-min": {
            "task": "poll_deal_replies_task",
            "schedule": 300.0, # 5 minutes
        },
    }
)

if __name__ == "__main__":
    celery_app.start()
