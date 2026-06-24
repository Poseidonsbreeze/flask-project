from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
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


def serialize_calendar_event(s):
    return {
        "id": s.id,
        "title": s.title,
        "provider": s.provider,
        "country": s.country,
        "degree_level": s.degree_level,
        "deadline": s.deadline.isoformat() if s.deadline else None,
        "application_link": s.application_link,
        "days_until": (s.deadline - datetime.utcnow().date()).days if s.deadline else None,
        "is_urgent": s.deadline and (s.deadline - datetime.utcnow().date()).days <= 30,
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


# CALENDAR VIEW - Scholarships with deadlines
@scholarship_bp.route("/calendar", methods=["GET"])
def get_calendar():
    scholarships = Scholarship.query.filter(
        Scholarship.is_archived == False,
        Scholarship.deleted_at == None,
        Scholarship.deadline != None
    ).order_by(Scholarship.deadline.asc()).all()

    now = datetime.utcnow().date()
    upcoming = []
    past = []

    for s in scholarships:
        event = serialize_calendar_event(s)
        if s.deadline >= now:
            upcoming.append(event)
        else:
            past.append(event)

    return jsonify({
        "upcoming": upcoming,
        "past": past,
        "total_upcoming": len(upcoming),
        "total_past": len(past)
    }), 200


# UPCOMING DEADLINES (next 30 days)
@scholarship_bp.route("/deadlines/upcoming", methods=["GET"])
def get_upcoming_deadlines():
    days = request.args.get('days', 30, type=int)
    cutoff = datetime.utcnow().date() + timedelta(days=days)

    scholarships = Scholarship.query.filter(
        Scholarship.is_archived == False,
        Scholarship.deleted_at == None,
        Scholarship.deadline != None,
        Scholarship.deadline <= cutoff,
        Scholarship.deadline >= datetime.utcnow().date()
    ).order_by(Scholarship.deadline.asc()).all()

    return jsonify([serialize_calendar_event(s) for s in scholarships]), 200
