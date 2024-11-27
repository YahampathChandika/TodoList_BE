import jwt
from datetime import datetime, timedelta
from app.config import Config

# Function to generate JWT
def generate_jwt(payload):
    payload["exp"] = datetime.utcnow() + timedelta(days=1)  # 1-day expiry
    return jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")

# Function to validate and decode JWT
def validate_jwt(token):
    try:
        return jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# Function to decode JWT (to use in your routes)
def decode_jwt(token):
    try:
        # Decode the JWT and return the payload
        return jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError("Token has expired")  # Throw explicit error for expired token
    except jwt.InvalidTokenError:
        raise jwt.InvalidTokenError("Invalid token")  # Throw explicit error for invalid token
