from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from api.models import db, User

auth = Blueprint('auth', __name__)


@auth.route('/register', methods=['POST'])
def register():
    """
        Register a new user. Endpoint: POST / auth/register
        Expects JSON: {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "1234567890",
        "password": "password123",
        "role": "student" // or "instructor"
        }
    """
    data = request.json
    if not data:
        return jsonify({"message": "Invalid JSON"}), 400

    if 'role' not in data or data['role'] not in ['student', 'instructor']:
        return jsonify({"message": "Invalid role. Must be 'student' or 'instructor'"}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({"message": "Email already registered"}), 400

    user = User(name=data['name'], email=data['email'],
                phone=data['phone'], role=data['role'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": f"{data['role'].capitalize()} registered successfully!"}), 201


@auth.route('/login', methods=['POST'])
def login():
    """
        Login a user. Endpoint: POST /auth/login
        Expects JSON: {
        "email": "john.doe@example.com",
        "password": "password123"
        }
    """
    data = request.json
    if not data:
        return jsonify({"message": "Invalid JSON"}), 400
    user = User.query.filter_by(email=data['email']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({"message": "Invalid credentials"}), 401

    token = create_access_token(identity={"id": user.id, "role": user.role})
    return jsonify({"token": token}), 200


def role_required(required_role):
    """Custom decorator for role-based access control"""
    def wrapper(fn):
        @jwt_required()
        def decorated_function(*args, **kwargs):
            identity = get_jwt_identity()
            if not identity or identity.get('role') != required_role:
                return jsonify({"message": "Access forbidden: insufficient permissions"}), 403
            return fn(*args, **kwargs)
        # Забезпечення унікального імені функції
        decorated_function.__name__ = f"{fn.__name__}_{required_role}"
        return decorated_function
    return wrapper


@auth.route('/', methods=['GET'])
def welcome():
    """
        Welcome route. Endpoint: GET /
        Response: {"message": "Вітаю на проєкті!"}
    """
    return jsonify({"message": "Вітаю на проєкті!"}), 200
