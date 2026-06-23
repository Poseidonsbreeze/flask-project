import atexit
import os
from apscheduler.schedulers.background import BackgroundScheduler
from app.scraping.scraper_engine import run_all_scrapers


def start_scheduler(app):
    # Avoid double-start when Flask debug mode uses the reloader
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or not app.debug:
        scheduler = BackgroundScheduler()

        # every 6 hours
        scheduler.add_job(
            func=lambda: run_with_context(app),
            trigger="interval",
            hours=6
        )

        hours=6
    )

    scheduler.start()


def run_with_context(app):
    with app.app_context():
        run_all_scrapers()