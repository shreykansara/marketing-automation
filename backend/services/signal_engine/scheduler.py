import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
from services.signal_engine.utils.logger import get_logger
from services.signal_engine.processor import run_ingestion_pipeline_async

logger = get_logger("signal_engine.scheduler")

scheduler = BackgroundScheduler()

def scheduled_job():
    logger.info("Executing scheduled ingestion job...")
    # BackgroundScheduler runs in a separate thread. We need to create an event loop for the async function.
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run_ingestion_pipeline_async())
    except Exception as e:
        logger.error(f"Scheduled job failed: {e}")
    finally:
        loop.close()

def start_scheduler():
    logger.info("Starting background scheduler for Signal Engine...")
    # Add a job to run every 6 hours
    scheduler.add_job(scheduled_job, 'interval', hours=6, id='ingestion_job', replace_existing=True)
    scheduler.start()
    logger.info("Scheduler started successfully.")

def shutdown_scheduler():
    logger.info("Shutting down background scheduler...")
    scheduler.shutdown(wait=False)
