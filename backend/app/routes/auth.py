from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models.user import User
from database import db
from passlib.hash import bcrypt, scrypt
import logging

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()

        # Validate input
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password are required'}), 400

        # Fetch user from database
        user = User.query.filter_by(username=data['username']).first()
        if not user or not user.is_active:
            return jsonify({'error': 'Invalid credentials'}), 401

        # Check password with bcrypt or scrypt
        password = data['password']
        
        # Debugging: Print hash and password details        
        logging.basicConfig(level=logging.INFO)
        #logging.info(f"Password hash from database: {user.password_hash}")
        #logging.info(f"Password provided: {password}")
        
        if user.password_hash.startswith("$2b$"):  # bcrypt hash
            if not bcrypt.verify(password, user.password_hash):
                return jsonify({'error': 'Invalid credentials'}), 401
        elif user.password_hash.startswith("scrypt:"):  # scrypt hash
            try:
                verification_result = scrypt.verify(password, user.password_hash)
                #logging.info(f"scrypt.verify result: {verification_result}")
                if not verification_result:
                    return jsonify({'error': 'Invalid credentials'}), 401
            except ValueError as e:
                #logging.error(f"Error during hash verification: {str(e)}")
                return jsonify({'error': f'Hash verification failed: {str(e)}'}), 400
        else:
            return jsonify({'error': 'Unsupported hash format'}), 400

        # Generate access token
        access_token = create_access_token(identity=user.id)
        return jsonify({
            'access_token': access_token,
            'user': user.to_dict()
        }), 200

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

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
        }, 200)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/users', methods=['POST'])
@jwt_required()
def add_user():
    """Add a new user (Admin only)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        if not current_user or current_user.role != 'Admin':
            return jsonify({'error': 'Insufficient permissions'}), 403

        data = request.get_json()
        if not data or not all(key in data for key in ['username', 'email', 'password', 'role', 'full_name']):
            return jsonify({'error': 'All fields (username, email, password, role, full_name) are required'}), 400

        # Hash password with bcrypt
        password_hash = bcrypt.hash(data['password'])

        new_user = User(
            username=data['username'],
            email=data['email'],
            role=data['role'],
            full_name=data['full_name'],
            password_hash=password_hash,
        )
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': 'User added successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/users/<user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """Delete a user (Admin only)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        if not current_user or current_user.role != 'Admin':
            return jsonify({'error': 'Insufficient permissions'}), 403

        user_to_delete = User.query.get(user_id)
        if not user_to_delete:
            return jsonify({'error': 'User not found'}), 404

        db.session.delete(user_to_delete)
        db.session.commit()

        return jsonify({'message': 'User deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
