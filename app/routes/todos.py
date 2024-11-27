from flask import Blueprint, request, jsonify, current_app
from app.models.todo_model import Todo
from bson import ObjectId
import jwt
from app.utils.jwt_utils import decode_jwt  # Assuming you have a JWT utility for decoding

bp = Blueprint("todos", __name__, url_prefix="/todos")  # Blueprint object is named 'bp'

@bp.route("/", methods=["OPTIONS"])
def handle_options():
    return jsonify({"message": "Preflight request allowed"}), 200

# Function to verify JWT token
def verify_jwt_token():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Token is missing"}), 403  # Forbidden

    try:
        # Remove "Bearer " prefix if present
        if token.startswith("Bearer "):
            token = token[7:]

        # Decode the token
        payload = decode_jwt(token)
        return payload  # Return the payload if the token is valid
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token has expired"}), 401  # Unauthorized
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401  # Unauthorized

@bp.route('/', methods=['POST'])
def create_todo():
    # Verify JWT token
    payload = verify_jwt_token()
    if isinstance(payload, tuple):  # If an error occurred during verification
        return payload

    data = request.json
    db = current_app.db

    if not data.get('userId') or not data.get('task') or not data.get('date') or not data.get('time'):
        return jsonify({"error": "Missing required fields"}), 400

    # Validate date and time
    if not Todo.validate_date(data["date"]):
        return jsonify({"error": "Invalid date format (YYYY-MM-DD expected)"}), 400
    if not Todo.validate_time(data["time"]):
        return jsonify({"error": "Invalid time format (HH:MM expected)"}), 400

    # Create and save the to-do
    todo = Todo(
        user_id=data["userId"],
        task=data["task"],
        date=data["date"],
        time=data["time"]
    )
    result = db.todos.insert_one(todo.to_dict())
    return jsonify({"message": "To-Do created", "id": str(result.inserted_id)}), 201

@bp.route('/<user_id>', methods=['GET'])
def get_todos(user_id):
    # Verify JWT token
    payload = verify_jwt_token()
    if isinstance(payload, tuple):  # If an error occurred during verification
        return payload

    db = current_app.db
    todos = db.todos.find({"userId": user_id})

    # Convert each todo document to a dictionary, including the '_id' field
    todos_list = []
    for todo in todos:
        todo_dict = Todo.from_dict(todo).to_dict()
        todo_dict["id"] = str(todo["_id"])  # Add the 'id' field from '_id'
        todos_list.append(todo_dict)

    return jsonify(todos_list), 200


@bp.route('/byId/<todo_id>', methods=['GET'])
def get_todo_by_id(todo_id):
    # Verify JWT token
    payload = verify_jwt_token()
    if isinstance(payload, tuple):  # If an error occurred during verification
        return payload

    db = current_app.db

    # Fetch the to-do by ID
    todo = db.todos.find_one({"_id": ObjectId(todo_id)})
    if not todo:
        return jsonify({"error": "To-Do not found"}), 404

    # Convert MongoDB document to a dictionary
    todo_dict = Todo.from_dict(todo).to_dict()
    todo_dict["id"] = str(todo["_id"])  # Add the 'id' field

    return jsonify(todo_dict), 200


@bp.route('/toggle/<todo_id>', methods=['PATCH'])
def toggle_completed(todo_id):
    # Verify JWT token
    payload = verify_jwt_token()
    if isinstance(payload, tuple):  # If an error occurred during verification
        return payload

    db = current_app.db

    # Fetch the current state of the to-do
    todo = db.todos.find_one({"_id": ObjectId(todo_id)})
    if not todo:
        return jsonify({"error": "To-Do not found"}), 404

    # Toggle the 'completed' field
    current_state = todo.get("completed", False)  # Default to False if 'completed' is not set
    updated_state = not current_state

    # Update the to-do item
    result = db.todos.update_one({"_id": ObjectId(todo_id)}, {"$set": {"completed": updated_state}})
    if result.matched_count == 0:
        return jsonify({"error": "Failed to toggle the completed state"}), 500

    return jsonify({"message": "To-Do toggled", "completed": updated_state}), 200


@bp.route('/<todo_id>', methods=['PUT'])
def update_todo(todo_id):
    # Verify JWT token
    payload = verify_jwt_token()
    if isinstance(payload, tuple):  # If an error occurred during verification
        return payload

    data = request.json
    db = current_app.db

    # Fields to update
    update_fields = {}
    if "task" in data:
        update_fields["task"] = data["task"]
    if "date" in data:
        if not Todo.validate_date(data["date"]):
            return jsonify({"error": "Invalid date format (YYYY-MM-DD expected)"}), 400
        update_fields["date"] = data["date"]
    if "time" in data:
        if not Todo.validate_time(data["time"]):
            return jsonify({"error": "Invalid time format (HH:MM expected)"}), 400
        update_fields["time"] = data["time"]
    if "completed" in data:
        update_fields["completed"] = data["completed"]

    # Update the to-do item
    result = db.todos.update_one({"_id": ObjectId(todo_id)}, {"$set": update_fields})
    if result.matched_count == 0:
        return jsonify({"error": "To-Do not found"}), 404
    return jsonify({"message": "To-Do updated"}), 200

@bp.route('/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    # Verify JWT token
    payload = verify_jwt_token()
    if isinstance(payload, tuple):  # If an error occurred during verification
        return payload

    db = current_app.db

    # Delete the to-do item
    result = db.todos.delete_one({"_id": ObjectId(todo_id)})
    if result.deleted_count == 0:
        return jsonify({"error": "To-Do not found"}), 404
    return jsonify({"message": "To-Do deleted"}), 200
