"""
IAMShield - Authentication Routes
POST /api/register, POST /api/login, POST /api/forgot-password, GET /api/me
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.database import get_db
from bson import ObjectId
import bcrypt, re
from datetime import datetime

auth_bp = Blueprint("auth", __name__)

def valid_email(e):
    """
    Strict email validation:
    - local part: 1+ chars before @
    - domain: 2+ chars before the dot  (rejects 'x@y.com' style single-char domains)
    - TLD: 2–6 letters only  (rejects numbers-only TLDs, too-short endings)
    - no spaces anywhere
    """
    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9\-]{2,}\.[a-zA-Z]{2,6}$'
    return re.match(pattern, e.strip()) is not None
def valid_password(p): return len(p) >= 8 and any(c.isupper() for c in p) and any(c.isdigit() for c in p)

@auth_bp.route("/register", methods=["POST"])
def register():
    d = request.get_json(force=True, silent=True) or {}
    for f in ["firstName","lastName","email","password","organizationName"]:
        if not d.get(f):
            return jsonify({"error": f"'{f}' is required"}), 400
    if not valid_email(d["email"]):
        return jsonify({"error": "Invalid email address"}), 400
    if not valid_password(d["password"]):
        return jsonify({"error": "Password needs 8+ chars, one uppercase & one digit"}), 400
    db = get_db()
    if db.users.find_one({"email": d["email"].lower()}):
        return jsonify({"error": "Email already registered"}), 409
    hashed = bcrypt.hashpw(d["password"].encode(), bcrypt.gensalt())
    user = {
        "firstName":        d["firstName"].strip(),
        "lastName":         d["lastName"].strip(),
        "email":            d["email"].lower().strip(),
        "password":         hashed,
        "organizationName": d["organizationName"].strip(),
        "createdAt":        datetime.utcnow()
    }
    res   = db.users.insert_one(user)
    uid   = str(res.inserted_id)
    token = create_access_token(identity=uid)
    return jsonify({
        "message": "Account created",
        "token":   token,
        "user": {
            "id":               uid,
            "firstName":        user["firstName"],
            "lastName":         user["lastName"],
            "email":            user["email"],
            "organizationName": user["organizationName"]
        }
    }), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    d = request.get_json(force=True, silent=True) or {}
    if not d.get("email") or not d.get("password"):
        return jsonify({"error": "Email and password required"}), 400
    db   = get_db()
    user = db.users.find_one({"email": d["email"].lower().strip()})
    if not user or not bcrypt.checkpw(d["password"].encode(), user["password"]):
        return jsonify({"error": "Invalid email or password"}), 401
    uid   = str(user["_id"])
    token = create_access_token(identity=uid)
    return jsonify({
        "message": "Login successful",
        "token":   token,
        "user": {
            "id":               uid,
            "firstName":        user["firstName"],
            "lastName":         user["lastName"],
            "email":            user["email"],
            "organizationName": user["organizationName"]
        }
    }), 200

@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    return jsonify({"message": "If that email exists, a reset link has been sent."}), 200

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_me():
    uid  = get_jwt_identity()
    db   = get_db()
    user = db.users.find_one({"_id": ObjectId(uid)})
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        "id":               str(user["_id"]),
        "firstName":        user["firstName"],
        "lastName":         user["lastName"],
        "email":            user["email"],
        "organizationName": user["organizationName"]
    }), 200
