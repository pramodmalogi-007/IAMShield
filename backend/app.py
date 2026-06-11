"""
IAMShield - Identity & Access Management Platform
Main Flask Application Entry Point
Run: python app.py
"""

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

load_dotenv()

from routes.auth       import auth_bp
from routes.assessment import assessment_bp
from routes.dashboard  import dashboard_bp
from routes.admin      import admin_bp
from routes.ai         import ai_bp
# cart and orders removed per requirements

def create_app():
    app = Flask(__name__, static_folder="../frontend", static_url_path="")

    app.config["JWT_SECRET_KEY"]           = os.getenv("JWT_SECRET_KEY", "iamshield-secret-2024")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False
    app.config["JWT_TOKEN_LOCATION"]       = ["headers"]
    app.config["JWT_HEADER_NAME"]          = "Authorization"
    app.config["JWT_HEADER_TYPE"]          = "Bearer"

    CORS(app, resources={r"/api/*": {"origins": "*"}},
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

    jwt = JWTManager(app)

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"error": "Invalid token", "details": str(error)}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({"error": "Authorization token required"}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "Token has expired"}), 401

    app.register_blueprint(auth_bp,       url_prefix="/api")
    app.register_blueprint(assessment_bp, url_prefix="/api")
    app.register_blueprint(dashboard_bp,  url_prefix="/api")
    app.register_blueprint(admin_bp,      url_prefix="/api")

    @app.route("/")
    def index():
        return app.send_static_file("index.html")

    @app.route("/<path:path>")
    def static_files(path):
        try:    return app.send_static_file(path)
        except: return app.send_static_file("index.html")

    return app

if __name__ == "__main__":
    app = create_app()
    print("IAMShield running on http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)