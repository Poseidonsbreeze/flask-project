from flask import Blueprint, jsonify
import math
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Scholarship
from app.matching.match_engine import compute_matches

match_bp = Blueprint("match", __name__)


def _serialize_match_scholarship(s):
    return {
        "id": s.id,
        "title": s.title,
        "provider": s.provider,
        "country": s.country,
        "degree_level": s.degree_level,
        "eligibility": s.eligibility,
        "description": s.description,
        "deadline": s.deadline.isoformat() if s.deadline else None,
        "application_link": s.application_link,
    }


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

    for match in matches[:10]:
        scholarship = scholarships[match["scholarship_index"]]

        raw_score = match.get("score", 0.0)
        safe_score = raw_score if (isinstance(raw_score, (int, float)) and math.isfinite(raw_score)) else 0.0

        base = _serialize_match_scholarship(scholarship)
        base["score"] = round(safe_score, 3)
        results.append(base)

    return jsonify(results), 200