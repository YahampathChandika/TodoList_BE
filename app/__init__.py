from flask import Flask
from pymongo import MongoClient
from app.routes import users, todos
from app.config import Config
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Configure CORS to allow only the frontend origin
    CORS(app)

    # Register blueprints
    from app.routes.users import bp as users_bp
    from app.routes.todos import bp as todos_bp

    app.register_blueprint(users_bp)
    app.register_blueprint(todos_bp)

    # MongoDB setup
    client = MongoClient(app.config["MONGO_URI"])
    app.db = client[app.config["DATABASE_NAME"]]

    return app
