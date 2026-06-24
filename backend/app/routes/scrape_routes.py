from flask import Blueprint, jsonify
from app.scraping.scraper_engine import run_all_scrapers
from app.scraping.seed_data import seed_scholarships

scrape_bp = Blueprint("scrape", __name__)


@scrape_bp.route("/scrape/run", methods=["GET"])
def scrape_all():
    result = run_all_scrapers()
    return jsonify(result)


@scrape_bp.route("/seed", methods=["GET"])
def seed_database():
    count = seed_scholarships()
    return jsonify({"message": f"Seeded {count} scholarships", "total_added": count})