from werkzeug.security import generate_password_hash, check_password_hash

class User:
    def __init__(self, username, email, password, firstName, lastName):
        self.username = username
        self.email = email
        self.firstName = firstName
        self.lastName = lastName
        self.password = generate_password_hash(password)

    def to_dict(self):
        return {
            "username": self.username,
            "email": self.email,
            "password": self.password, 
            "firstName": self.firstName,
            "lastName": self.lastName,
        }

    @staticmethod
    def validate_password(hashed_password, password):
        """
        Check if the provided password matches the hashed password.
        """
        return check_password_hash(hashed_password, password)

    @staticmethod
    def from_dict(data):
        """
        Create a User instance from a dictionary.
        """
        return User(
            username=data["username"],
            email=data["email"],
            password=data["password"],
            firstName=data["firstName"],
            lastName=data["lastName"]
        )
