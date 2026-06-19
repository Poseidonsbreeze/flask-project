from apscheduler.schedulers.background import BackgroundScheduler
from app.scraping.scraper_engine import run_all_scrapers


def start_scheduler(app):

    scheduler = BackgroundScheduler()

    scheduler.add_job(
        func=lambda: run_with_context(app),
        trigger="interval",
        hours=6
    )

    scheduler.start()


def run_with_context(app):
    try:
        with app.app_context():
            run_all_scrapers()
    except Exception as e:
        print(f"[SCHEDULER] Error during scheduled scrape: {str(e)}")