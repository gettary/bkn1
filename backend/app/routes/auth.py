from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models.user import User
from database import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password are required'}), 400
        
        user = User.query.filter_by(username=data['username']).first()
        print(f"Password hash in DB: {user.password_hash}")
        print(f"Password provided: {data['password']}")
        if user and user.check_password(data['password']) and user.is_active:
            print("Password matched!")
            access_token = create_access_token(identity=user.id)
            return jsonify({
                'access_token': access_token,
                'user': user.to_dict()
            }), 200
        else:
            print("Password mismatch")
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        print(f"Error during login: {e}")

        user = User.query.filter_by(username='admin').first()
        if user:
            user.set_password('lihaung')  # เปลี่ยนรหัสผ่าน
            db.session.commit()
            print("Password reset successful")
        else:
            print("User not found")
            return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.is_active:
            return jsonify({'error': 'User not found'}), 404
            
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """Get all users (for admin/moderator)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user or current_user.role not in ['Admin', 'Moderator']:
            return jsonify({'error': 'Insufficient permissions'}), 403
            
        users = User.query.filter_by(is_active=True).all()
        return jsonify({
            'users': [user.to_dict() for user in users]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500