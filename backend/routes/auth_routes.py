from flask import Blueprint, request, jsonify
import bcrypt
import jwt
from datetime import datetime, timedelta
from functools import wraps
from config import Config
try:
    from database_sqlite import execute_query, execute_update
except ImportError:
    from database import execute_query, execute_update

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# JWT Token Helper Functions
def generate_token(user_id, email):
    """Generate JWT token for authenticated user"""
    payload = {
        'user_id': user_id,
        'email': email,
        'exp': datetime.utcnow() + timedelta(hours=Config.JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM)
    return token

def verify_token(token):
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=[Config.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# Authentication Decorator
def token_required(f):
    """Decorator to protect routes that require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Authentication token is missing'}), 401
        
        # Verify token
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Add user info to request
        request.user_id = payload['user_id']
        request.user_email = payload['email']
        
        return f(*args, **kwargs)
    
    return decorated

# ============================================
# REGISTER NEW USER
# ============================================
@bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['firstName', 'lastName', 'email', 'password', 'userType']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        first_name = data['firstName']
        last_name = data['lastName']
        email = data['email'].lower().strip()
        password = data['password']
        user_type = data['userType']
        
        # Validate user type
        if user_type not in ['student', 'institution', 'company']:
            return jsonify({'error': 'Invalid user type'}), 400
        
        # Validate password strength
        if len(password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters long'}), 400
        
        # Check if user already exists
        existing_user = execute_query(
            "SELECT id FROM users WHERE email = ?",
            (email,)
        )
        
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 409
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Insert new user
        user_id = execute_update(
            """INSERT INTO users (first_name, last_name, email, password_hash, user_type)
               VALUES (?, ?, ?, ?, ?)""",
            (first_name, last_name, email, password_hash.decode('utf-8'), user_type)
        )
        
        if not user_id:
            return jsonify({'error': 'Failed to create user'}), 500
        
        # Generate token
        token = generate_token(user_id, email)
        
        return jsonify({
            'message': 'User registered successfully',
            'token': token,
            'user': {
                'id': user_id,
                'firstName': first_name,
                'lastName': last_name,
                'email': email,
                'userType': user_type
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# LOGIN USER
# ============================================
@bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return token"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        # Get user from database
        users = execute_query(
            """SELECT id, first_name, last_name, email, password_hash, user_type, is_active
               FROM users WHERE email = ?""",
            (email,)
        )
        
        if not users:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        user = users[0]
        
        # Check if account is active
        if not user['is_active']:
            return jsonify({'error': 'Account is deactivated'}), 403
        
        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Update last login
        execute_update(
            "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
            (user['id'],)
        )
        
        # Generate token
        token = generate_token(user['id'], user['email'])
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user['id'],
                'firstName': user['first_name'],
                'lastName': user['last_name'],
                'email': user['email'],
                'userType': user['user_type']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# VERIFY TOKEN
# ============================================
@bp.route('/verify', methods=['GET'])
@token_required
def verify():
    """Verify if token is valid and return user info"""
    try:
        # Get user info
        users = execute_query(
            """SELECT id, first_name, last_name, email, user_type
               FROM users WHERE id = ? AND is_active = 1""",
            (request.user_id,)
        )
        
        if not users:
            return jsonify({'error': 'User not found'}), 404
        
        user = users[0]
        
        return jsonify({
            'valid': True,
            'user': {
                'id': user['id'],
                'firstName': user['first_name'],
                'lastName': user['last_name'],
                'email': user['email'],
                'userType': user['user_type']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# LOGOUT USER
# ============================================
@bp.route('/logout', methods=['POST'])
@token_required
def logout():
    """Logout user (client should delete token)"""
    return jsonify({
        'message': 'Logout successful'
    }), 200

# ============================================
# GET USER PROFILE
# ============================================
@bp.route('/profile', methods=['GET'])
@token_required
def get_profile():
    """Get user profile information"""
    try:
        users = execute_query(
            """SELECT id, first_name, last_name, email, user_type, 
                      email_verified, created_at, last_login
               FROM users WHERE id = ?""",
            (request.user_id,)
        )
        
        if not users:
            return jsonify({'error': 'User not found'}), 404
        
        user = users[0]
        
        created_at_val = user.get('created_at')
        if hasattr(created_at_val, 'isoformat'):
            created_at_val = created_at_val.isoformat()
        last_login_val = user.get('last_login')
        if hasattr(last_login_val, 'isoformat'):
            last_login_val = last_login_val.isoformat()

        return jsonify({
            'user': {
                'id': user['id'],
                'firstName': user['first_name'],
                'lastName': user['last_name'],
                'email': user['email'],
                'userType': user['user_type'],
                'emailVerified': bool(user.get('email_verified')),
                'createdAt': str(created_at_val) if created_at_val else None,
                'lastLogin': str(last_login_val) if last_login_val else None
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# UPDATE USER PROFILE
# ============================================
@bp.route('/profile', methods=['PUT'])
@token_required
def update_profile():
    """Update user profile information"""
    try:
        data = request.get_json()
        
        # Build update query dynamically
        update_fields = []
        params = []
        
        if 'firstName' in data:
            update_fields.append("first_name = ?")
            params.append(data['firstName'])
        
        if 'lastName' in data:
            update_fields.append("last_name = ?")
            params.append(data['lastName'])
        
        if not update_fields:
            return jsonify({'error': 'No fields to update'}), 400
        
        params.append(request.user_id)
        
        query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
        execute_update(query, tuple(params))
        
        return jsonify({
            'message': 'Profile updated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
