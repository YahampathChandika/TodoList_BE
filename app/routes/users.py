from flask import Blueprint, request, jsonify, current_app
from app.models.user_model import User
from app.utils.jwt_utils import generate_jwt
import re

bp = Blueprint("users", __name__, url_prefix="/users")

@bp.route('/register', methods=['POST'])
def register_user():
    data = request.json
    db = current_app.db

    # Validation
    if not data.get('username') or not data.get('password') or not data.get('email') or not data.get('firstName') or not data.get('lastName'):
        return jsonify({"error": "Missing required fields"}), 400

    if not re.match(r"[^@]+@[^@]+\.[^@]+", data["email"]):
        return jsonify({"error": "Invalid email format"}), 400

    if db.users.find_one({"username": data["username"]}):
        return jsonify({"error": "Username already exists"}), 400

    # Create and save the user
    user = User(data["username"], data["email"], data["password"], data["firstName"], data["lastName"])
    db.users.insert_one(user.to_dict())
    return jsonify({"message": "User registered successfully"}), 201

@bp.route('/login', methods=['POST'])
def login_user():
    data = request.json
    db = current_app.db

    if not data.get('username') or not data.get('password'):
        return jsonify({"error": "Missing required fields"}), 400

    user = db.users.find_one({"username": data["username"]})
    if not user or not User.validate_password(user["password"], data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    # Generate JWT token
    token = generate_jwt({"userId": str(user["_id"]), "username": user["username"], "firstName": user["firstName"], "lastName": user["lastName"], "email": user["email"]})
    return jsonify({"token": token}), 200
