from flask import Blueprint, jsonify
from app.scraping.scraper_engine import run_all_scrapers

scrape_bp = Blueprint("scrape", __name__)


@scrape_bp.route("/scrape/run", methods=["GET"])
def scrape_all():
    result = run_all_scrapers()
    return jsonify(result)