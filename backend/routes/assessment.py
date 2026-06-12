"""
IAMShield - Assessment Engine Routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.database import get_db
from datetime import datetime
import uuid

assessment_bp = Blueprint("assessment", __name__)


def _score_products(db, category, answers):
    """
    answers = { "1": ["val1","val2"], "2": ["val3"] }
    Flatten all selected values, then score products.
    Tiebreaker: number of directly matched feature weights, then feature count.
    Each product also gets a rank_reason explaining why it placed where it did.
    """
    products = list(db.products.find({"category": category}))
    all_selected = []
    for vals in answers.values():
        if isinstance(vals, list):
            all_selected.extend(vals)
        else:
            all_selected.append(vals)

    scored = []
    for p in products:
        weights      = p.get("score_weights", {})
        raw_score    = sum(weights.get(v, 0) for v in all_selected)
        max_score    = sum(weights.values()) or 1
        norm         = min(round((raw_score / max_score) * 100), 100)
        matched_keys = [v for v in all_selected if v in weights]
        scored.append({
            "id":            p["id"],
            "name":          p["name"],
            "category":      p["category"],
            "price":         p.get("price", 0),
            "description":   p["description"],
            "features":      p.get("features", []),
            "score":         norm,
            "_matched_keys": matched_keys,
            "_feat_count":   len(p.get("features", [])),
        })

    # Sort: score desc → matched_keys count desc → feature count desc → name asc
    scored.sort(key=lambda x: (
        -x["score"],
        -len(x["_matched_keys"]),
        -x["_feat_count"],
        x["name"]
    ))

    # Assign rank and build a reason sentence
    rank_labels = ["1st", "2nd", "3rd", "4th", "5th"]
    for i, p in enumerate(scored):
        label = rank_labels[i] if i < len(rank_labels) else f"{i+1}th"
        matched = p["_matched_keys"]
        if p["score"] == 100:
            reason = (f"Ranked {label} — perfect match. "
                      f"Every requirement you selected aligns with this product's core strengths "
                      f"({len(matched)} of your {len(all_selected)} selections directly matched).")
        elif p["score"] >= 70:
            reason = (f"Ranked {label} — strong match ({p['score']}%). "
                      f"{len(matched)} of your {len(all_selected)} selections matched this product's capabilities.")
        elif p["score"] >= 40:
            reason = (f"Ranked {label} — partial match ({p['score']}%). "
                      f"Covers {len(matched)} of your requirements but may need supplementing.")
        else:
            reason = (f"Ranked {label} — low match ({p['score']}%). "
                      f"Only {len(matched)} of your selections align with this product.")
        p["rank_reason"] = reason
        # Clean up internal fields
        del p["_matched_keys"]
        del p["_feat_count"]

    return scored


@assessment_bp.route("/categories", methods=["GET"])
def get_categories():
    db   = get_db()
    cats = list(db.categories.find({}).sort("order", 1))
    for c in cats:
        c.pop("_id", None)
    return jsonify(cats), 200


@assessment_bp.route("/questions", methods=["GET"])
def get_questions():
    cat = request.args.get("category")
    db  = get_db()
    q   = {"category": cat} if cat else {}
    qs  = list(db.questions.find(q).sort("order", 1))
    for x in qs:
        x["_id"] = str(x["_id"])
    return jsonify(qs), 200


@assessment_bp.route("/products", methods=["GET"])
def get_products():
    cat = request.args.get("category")
    db  = get_db()
    q   = {"category": cat} if cat else {}
    ps  = list(db.products.find(q))
    for p in ps:
        p.pop("_id", None)
        p.pop("score_weights", None)
    return jsonify(ps), 200


@assessment_bp.route("/assessment/submit-guest", methods=["POST"])
def submit_guest_assessment():
    data     = request.get_json(force=True, silent=True) or {}
    category = data.get("category")
    answers  = data.get("answers", {})
    if not category:
        return jsonify({"error": "category required"}), 400

    db     = get_db()
    scored = _score_products(db, category, answers)

    session_id = str(uuid.uuid4())
    doc = {
        "sessionId": session_id,
        "userId":    None,
        "category":  category,
        "answers":   answers,
        "results":   scored,
        "claimed":   False,
        "createdAt": datetime.utcnow(),
    }
    db.assessments.insert_one(doc)

    return jsonify({
        "message":     "Assessment complete",
        "category":    category,
        "recommended": scored,
        "sessionId":   session_id,
        "answers":     answers,
    }), 200


@assessment_bp.route("/assessment/claim", methods=["POST"])
@jwt_required()
def claim_assessment():
    uid        = get_jwt_identity()
    data       = request.get_json(force=True, silent=True) or {}
    session_id = data.get("sessionId")
    if not session_id:
        return jsonify({"error": "sessionId required"}), 400

    db  = get_db()
    res = db.assessments.update_one(
        {"sessionId": session_id, "claimed": False},
        {"$set": {"userId": uid, "claimed": True, "claimedAt": datetime.utcnow()}}
    )
    if res.matched_count == 0:
        return jsonify({"error": "Session not found or already claimed"}), 404

    doc = db.assessments.find_one({"sessionId": session_id})
    doc["_id"]       = str(doc["_id"])
    doc["createdAt"] = doc["createdAt"].isoformat()
    return jsonify({
        "message":     "Assessment linked to your account",
        "recommended": doc.get("results", []),
        "category":    doc.get("category"),
        "answers":     doc.get("answers", {}),
    }), 200


@assessment_bp.route("/assessment/submit", methods=["POST"])
@jwt_required()
def submit_assessment():
    uid      = get_jwt_identity()
    data     = request.get_json(force=True, silent=True) or {}
    category = data.get("category")
    answers  = data.get("answers", {})
    if not category:
        return jsonify({"error": "category required"}), 400

    db     = get_db()
    scored = _score_products(db, category, answers)

    doc = {
        "userId":    uid,
        "category":  category,
        "answers":   answers,
        "results":   scored,
        "claimed":   True,
        "createdAt": datetime.utcnow(),
    }
    db.assessments.insert_one(doc)

    return jsonify({
        "message":     "Assessment complete",
        "category":    category,
        "recommended": scored,
        "answers":     answers,
    }), 200


@assessment_bp.route("/assessment/history", methods=["GET"])
@jwt_required()
def history():
    uid   = get_jwt_identity()
    db    = get_db()
    page  = int(request.args.get("page",  1))
    limit = int(request.args.get("limit", 20))
    skip  = (page - 1) * limit

    total = db.assessments.count_documents({"userId": uid})
    arr   = list(
        db.assessments.find({"userId": uid})
        .sort("createdAt", -1)
        .skip(skip)
        .limit(limit)
    )
    for a in arr:
        a["_id"]       = str(a["_id"])
        a["createdAt"] = a["createdAt"].isoformat()

    return jsonify({
        "total":       total,
        "page":        page,
        "totalPages":  (total + limit - 1) // limit,
        "assessments": arr,
    }), 200