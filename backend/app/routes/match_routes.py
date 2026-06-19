from flask import Blueprint, jsonify
import math
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Scholarship
from app.matching.match_engine import compute_matches

match_bp = Blueprint("match", __name__)


@match_bp.route("/match", methods=["GET"])
@jwt_required()
def match_scholarships():

    user_id = int(get_jwt_identity())

    user = User.query.get(user_id)
    scholarships = Scholarship.query.filter_by(is_archived=False, deleted_at=None).all()

    if not user:
        return jsonify({"error": "User not found"}), 404

    user_profile = user.profile_text or user.full_name

    matches = compute_matches(user_profile, scholarships)

    results = []

    for match in matches[:10]:  # top 10
        scholarship = scholarships[match["scholarship_index"]]

        # ensure score is a finite number before sending
        raw_score = match.get("score", 0.0)
        safe_score = raw_score if (isinstance(raw_score, (int, float)) and math.isfinite(raw_score)) else 0.0

        results.append({
            "id": scholarship.id,
            "title": scholarship.title,
            "provider": scholarship.provider,
            "country": scholarship.country,
            "degree_level": scholarship.degree_level,
            "eligibility": scholarship.eligibility,
            "description": scholarship.description,
            "deadline": str(scholarship.deadline),
            "application_link": scholarship.application_link,
            "score": round(safe_score, 3)
        })

    return jsonify(results), 200