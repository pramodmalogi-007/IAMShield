"""
IAMShield - Dashboard Route (no orders/payment)
GET /api/dashboard
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.database import get_db

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def get_dashboard():
    uid   = get_jwt_identity()
    db    = get_db()

    page  = int(request.args.get("page",  1))
    limit = int(request.args.get("limit", 10))
    skip  = (page - 1) * limit

    total_assessments = db.assessments.count_documents({"userId": uid})
    all_assessments   = list(
        db.assessments.find({"userId": uid})
        .sort("createdAt", -1)
        .skip(skip)
        .limit(limit)
    )
    for a in all_assessments:
        a["_id"]       = str(a["_id"])
        a["createdAt"] = a["createdAt"].isoformat()

    latest      = db.assessments.find_one({"userId": uid}, sort=[("createdAt", -1)])
    recommended = latest.get("results", [])[:4] if latest else []

    return jsonify({
        "stats": {
            "totalAssessments": total_assessments,
        },
        "assessments":  all_assessments,
        "totalPages":   (total_assessments + limit - 1) // limit,
        "currentPage":  page,
        "recommended":  recommended,
    }), 200
