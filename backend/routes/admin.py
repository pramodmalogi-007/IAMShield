"""
IAMShield - Admin Routes
POST   /api/admin/login
GET    /api/admin/stats
GET    /api/admin/users
DELETE /api/admin/users/<id>
GET    /api/admin/assessments
GET    /api/admin/products
POST   /api/admin/products
DELETE /api/admin/products/<id>
GET    /api/admin/questions
POST   /api/admin/questions
DELETE /api/admin/questions/<id>
"""

from flask import Blueprint, request, jsonify, session
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.database import get_db
from bson import ObjectId
import bcrypt
from datetime import datetime
from functools import wraps

admin_bp = Blueprint("admin", __name__)

# ── Admin JWT guard ───────────────────────────────────────────────────────────
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        from flask_jwt_extended import verify_jwt_in_request, get_jwt
        try:
            verify_jwt_in_request()
            claims = get_jwt()
            if not claims.get("is_admin"):
                return jsonify({"error": "Admin access required"}), 403
        except Exception as e:
            return jsonify({"error": "Admin auth required", "details": str(e)}), 401
        return f(*args, **kwargs)
    return decorated


# ── Admin Login ───────────────────────────────────────────────────────────────
@admin_bp.route("/admin/login", methods=["POST"])
def admin_login():
    d = request.get_json(force=True, silent=True) or {}
    username = d.get("username", "").strip()
    password = d.get("password", "")
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    db    = get_db()
    admin = db.admins.find_one({"username": username})
    if not admin or not bcrypt.checkpw(password.encode(), admin["password"]):
        return jsonify({"error": "Invalid admin credentials"}), 401

    # Issue JWT with admin claim
    token = create_access_token(
        identity=str(admin["_id"]),
        additional_claims={"is_admin": True}
    )
    return jsonify({
        "message": "Admin login successful",
        "token":   token,
        "admin":   {"id": str(admin["_id"]), "username": admin["username"]}
    }), 200


# ── Stats ─────────────────────────────────────────────────────────────────────
@admin_bp.route("/admin/stats", methods=["GET"])
@admin_required
def admin_stats():
    db = get_db()
    return jsonify({
        "users":       db.users.count_documents({}),
        "assessments": db.assessments.count_documents({}),
        "products":    db.products.count_documents({}),
        "categories":  db.categories.count_documents({}),
        "questions":   db.questions.count_documents({}),
    }), 200


# ── Users ─────────────────────────────────────────────────────────────────────
@admin_bp.route("/admin/users", methods=["GET"])
@admin_required
def admin_users():
    db    = get_db()
    users = list(db.users.find({}, {"password": 0}).sort("createdAt", -1))
    for u in users:
        u["_id"]       = str(u["_id"])
        u["createdAt"] = u.get("createdAt", datetime.utcnow()).isoformat()
    return jsonify(users), 200


@admin_bp.route("/admin/users/<user_id>", methods=["DELETE"])
@admin_required
def admin_delete_user(user_id):
    db  = get_db()
    try:
        res = db.users.delete_one({"_id": ObjectId(user_id)})
    except Exception:
        return jsonify({"error": "Invalid user ID"}), 400
    if res.deleted_count == 0:
        return jsonify({"error": "User not found"}), 404
    # also remove their assessments
    db.assessments.delete_many({"userId": user_id})
    return jsonify({"message": "User deleted"}), 200


# ── Assessments ───────────────────────────────────────────────────────────────
@admin_bp.route("/admin/assessments", methods=["GET"])
@admin_required
def admin_assessments():
    db   = get_db()
    page = int(request.args.get("page", 1))
    lim  = int(request.args.get("limit", 20))
    skip = (page - 1) * lim
    total = db.assessments.count_documents({})
    arr   = list(db.assessments.find({}).sort("createdAt", -1).skip(skip).limit(lim))
    for a in arr:
        a["_id"]       = str(a["_id"])
        a["createdAt"] = a["createdAt"].isoformat()
    return jsonify({"total": total, "assessments": arr}), 200


# ── Products CRUD ─────────────────────────────────────────────────────────────
@admin_bp.route("/admin/products", methods=["GET"])
@admin_required
def admin_get_products():
    db = get_db()
    ps = list(db.products.find({}))
    for p in ps:
        p["_id"] = str(p["_id"])
    return jsonify(ps), 200


@admin_bp.route("/admin/products", methods=["POST"])
@admin_required
def admin_add_product():
    d        = request.get_json(force=True, silent=True) or {}
    required = ["id", "name", "category", "price", "description"]
    for f in required:
        if not d.get(f):
            return jsonify({"error": f"'{f}' is required"}), 400
    db = get_db()
    if db.products.find_one({"id": d["id"]}):
        return jsonify({"error": "Product id already exists"}), 409
    doc = {
        "id":           d["id"],
        "name":         d["name"],
        "category":     d["category"],
        "price":        int(d["price"]),
        "description":  d["description"],
        "features":     d.get("features", []),
        "score_weights": d.get("score_weights", {}),
        "createdAt":    datetime.utcnow(),
    }
    db.products.insert_one(doc)
    doc["_id"] = str(doc["_id"])
    return jsonify({"message": "Product added", "product": doc}), 201


@admin_bp.route("/admin/products/<product_id>", methods=["DELETE"])
@admin_required
def admin_delete_product(product_id):
    db  = get_db()
    res = db.products.delete_one({"id": product_id})
    if res.deleted_count == 0:
        return jsonify({"error": "Product not found"}), 404
    return jsonify({"message": "Product deleted"}), 200


# ── Questions CRUD ────────────────────────────────────────────────────────────
@admin_bp.route("/admin/questions", methods=["GET"])
@admin_required
def admin_get_questions():
    db = get_db()
    qs = list(db.questions.find({}).sort("order", 1))
    for q in qs:
        q["_id"] = str(q["_id"])
    return jsonify(qs), 200


@admin_bp.route("/admin/questions", methods=["POST"])
@admin_required
def admin_add_question():
    d = request.get_json(force=True, silent=True) or {}
    if not d.get("text") or not d.get("category"):
        return jsonify({"error": "text and category required"}), 400
    db  = get_db()
    doc = {
        "category":  d["category"],
        "order":     d.get("order", 99),
        "text":      d["text"],
        "options":   d.get("options", []),
        "createdAt": datetime.utcnow(),
    }
    res     = db.questions.insert_one(doc)
    doc["_id"] = str(res.inserted_id)
    return jsonify({"message": "Question added", "question": doc}), 201


@admin_bp.route("/admin/questions/<q_id>", methods=["DELETE"])
@admin_required
def admin_delete_question(q_id):
    db  = get_db()
    res = db.questions.delete_one({"_id": ObjectId(q_id)})
    if res.deleted_count == 0:
        return jsonify({"error": "Question not found"}), 404
    return jsonify({"message": "Question deleted"}), 200