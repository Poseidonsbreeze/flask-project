from flask import Blueprint, request, jsonify
from datetime import datetime
from app.extensions import db
from app.models import Scholarship

scholarship_bp = Blueprint("scholarship", __name__)


def serialize_scholarship(s):
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
        "is_archived": s.is_archived,
    }


# CREATE SCHOLARSHIP
@scholarship_bp.route("/scholarships", methods=["POST"])
def create_scholarship():
    data = request.get_json()

    scholarship = Scholarship(
        title=data.get("title"),
        provider=data.get("provider"),
        country=data.get("country"),
        degree_level=data.get("degree_level"),
        eligibility=data.get("eligibility"),
        description=data.get("description"),
        deadline=data.get("deadline"),
        application_link=data.get("application_link")
    )

    db.session.add(scholarship)
    db.session.commit()

    return jsonify({"message": "Scholarship created"}), 201


# GET ALL SCHOLARSHIPS (excluding archived and deleted)
@scholarship_bp.route("/scholarships", methods=["GET"])
def get_scholarships():
    scholarships = Scholarship.query.filter_by(is_archived=False, deleted_at=None).all()
    return jsonify([serialize_scholarship(s) for s in scholarships]), 200


# GET SINGLE SCHOLARSHIP
@scholarship_bp.route("/scholarships/<int:id>", methods=["GET"])
def get_scholarship(id):
    s = Scholarship.query.filter_by(id=id, deleted_at=None).first()
    if not s:
        return jsonify({"error": "Not found"}), 404
    return jsonify(serialize_scholarship(s)), 200


# GET ARCHIVED SCHOLARSHIPS (excluding deleted)
@scholarship_bp.route("/scholarships/archived", methods=["GET"])
def get_archived_scholarships():
    scholarships = Scholarship.query.filter_by(is_archived=True, deleted_at=None).all()
    return jsonify([serialize_scholarship(s) for s in scholarships]), 200


# ARCHIVE SCHOLARSHIP
@scholarship_bp.route("/scholarships/<int:id>/archive", methods=["PATCH"])
def archive_scholarship(id):
    s = Scholarship.query.filter_by(id=id, deleted_at=None).first()
    if not s:
        return jsonify({"error": "Scholarship not found"}), 404

    s.is_archived = True
    db.session.commit()
    return jsonify({"message": "Scholarship archived successfully"}), 200


# UNARCHIVE SCHOLARSHIP
@scholarship_bp.route("/scholarships/<int:id>/unarchive", methods=["PATCH"])
def unarchive_scholarship(id):
    s = Scholarship.query.filter_by(id=id, deleted_at=None).first()
    if not s:
        return jsonify({"error": "Scholarship not found"}), 404

    s.is_archived = False
    db.session.commit()
    return jsonify({"message": "Scholarship restored successfully"}), 200


# DELETE SCHOLARSHIP (soft delete)
@scholarship_bp.route("/scholarships/<int:id>", methods=["DELETE"])
def delete_scholarship(id):
    s = Scholarship.query.filter_by(id=id, deleted_at=None).first()
    if not s:
        return jsonify({"error": "Scholarship not found"}), 404

    s.deleted_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"message": "Scholarship deleted successfully"}), 200
