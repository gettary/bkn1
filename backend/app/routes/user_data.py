from flask import Blueprint, request, jsonify, current_app as app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app.models.user import User
from app.models.assessment import IndicatorItem, Indicator
from app.models.user_data import UserData, UserPermission
from database import db
import os
from PIL import Image
import logging

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


user_data_bp = Blueprint('user_data', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@user_data_bp.route('/<indicator_item_id>', methods=['GET'])
@jwt_required()
def get_user_data(indicator_item_id):
    """Get user data for specific indicator item"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
            
        indicator_item = IndicatorItem.query.get(indicator_item_id)
        
        if not indicator_item:
            return jsonify({'error': 'Indicator item not found'}), 404
            
        # Check if user has permission to view this indicator
        if not current_user.has_permission(indicator_item.indicator_id, 'view'):
            return jsonify({'error': 'Access denied'}), 403
            
        user_data = UserData.query.filter_by(
            user_id=current_user_id,
            indicator_item_id=indicator_item_id
        ).first()
        
        if user_data:
            return jsonify({'user_data': user_data.to_dict()}), 200
        else:
            return jsonify({'user_data': None}), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_data_bp.route('/<indicator_item_id>', methods=['POST'])
@jwt_required()
def save_user_data(indicator_item_id):
    """Save user data for specific indicator item"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
            
        indicator_item = IndicatorItem.query.get(indicator_item_id)
        
        if not indicator_item:
            return jsonify({'error': 'Indicator item not found'}), 404
            
        # Check if user has permission to edit this indicator
        if not current_user.has_permission(indicator_item.indicator_id, 'view'):
            return jsonify({'error': 'Access denied'}), 403
            
        data = request.get_json()
        
        # Find existing user data or create new
        user_data = UserData.query.filter_by(
            user_id=current_user_id,
            indicator_item_id=indicator_item_id
        ).first()
        
        if not user_data:
            user_data = UserData(
                user_id=current_user_id,
                indicator_item_id=indicator_item_id
            )
            db.session.add(user_data)
            
        # Update fields
        if 'performance' in data:
            user_data.performance = data['performance']
        if 'rate' in data:
            user_data.rate = data['rate']
        if 'score' in data:
            user_data.score = data['score']
        if 'status' in data:
            # Validate status change
            if data['status'] == 'complete':
                # Check if all required fields are filled
                required_fields = ['performance', 'rate', 'score']
                missing_fields = []
                
                for field in required_fields:
                    value = data.get(field) or getattr(user_data, field)
                    if not value or not str(value).strip():
                        missing_fields.append(field)
                        
                if missing_fields:
                    return jsonify({
                        'error': 'Required fields are missing',
                        'missing_fields': missing_fields
                    }), 400
                    
            user_data.status = data['status']
            
        db.session.commit()
        
        return jsonify({
            'message': 'User data saved successfully',
            'user_data': user_data.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_data_bp.route('/<indicator_item_id>/upload', methods=['POST'])
@jwt_required()
def upload_image(indicator_item_id):
    """Upload image for indicator item"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
            
        indicator_item = IndicatorItem.query.get(indicator_item_id)
        
        if not indicator_item:
            return jsonify({'error': 'Indicator item not found'}), 404
            
        # Check if user has permission
        if not current_user.has_permission(indicator_item.indicator_id, 'view'):
            return jsonify({'error': 'Access denied'}), 403
            
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            
            # Create unique filename
            import time
            timestamp = str(int(time.time()))
            filename = f"{current_user_id}_{indicator_item_id}_{timestamp}_{filename}"
            
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Save and validate image
            file.save(filepath)
            
            try:
                # Validate it's a valid image
                with Image.open(filepath) as img:
                    img.verify()
                    
                # Update user data with image path
                user_data = UserData.query.filter_by(
                    user_id=current_user_id,
                    indicator_item_id=indicator_item_id
                ).first()
                
                if not user_data:
                    user_data = UserData(
                        user_id=current_user_id,
                        indicator_item_id=indicator_item_id
                    )
                    db.session.add(user_data)
                    
                # Remove old image if exists
                if user_data.image_path and os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], user_data.image_path)):
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], user_data.image_path))
                    
                user_data.image_path = filename
                db.session.commit()
                
                return jsonify({
                    'message': 'Image uploaded successfully',
                    'image_path': filename
                }), 200
                
            except Exception:
                # Remove invalid file
                if os.path.exists(filepath):
                    os.remove(filepath)
                return jsonify({'error': 'Invalid image file'}), 400
                
        else:
            return jsonify({'error': 'Invalid file type. Only PNG, JPG, JPEG, GIF are allowed'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_data_bp.route('/report/<assessment_id>', methods=['GET'])
@jwt_required()
def get_assessment_report(assessment_id):
    """Get assessment report data"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
            
        from app.models.assessment import Assessment
        assessment = Assessment.query.get(assessment_id)
        
        if not assessment or assessment.status != 'published':
            return jsonify({'error': 'Assessment not found or not published'}), 404
            
        report_data = []
        
        for item in assessment.items:
            item_data = {
                'title': item.title,
                'indicators': []
            }
            
            for indicator in item.indicators:
                # Check if user has permission to see this indicator
                if current_user.role in ['Admin', 'Moderator'] or current_user.has_permission(indicator.id, 'view'):
                    indicator_data = {
                        'title': indicator.title,
                        'items': [],
                        'user_data': []
                    }
                    
                    for indicator_item in indicator.items:
                        indicator_data['items'].append(indicator_item.to_dict())
                        
                        # Get user data for this indicator item
                        if current_user.role in ['Admin', 'Moderator']:
                            # Show all user data
                            user_data_list = UserData.query.filter_by(indicator_item_id=indicator_item.id).all()
                            for ud in user_data_list:
                                user_info = User.query.get(ud.user_id)
                                indicator_data['user_data'].append({
                                    'user_name': user_info.full_name if user_info else 'Unknown',
                                    'status': ud.status,
                                    'data': ud.to_dict()
                                })
                        else:
                            # Show only current user data
                            user_data = UserData.query.filter_by(
                                user_id=current_user_id,
                                indicator_item_id=indicator_item.id
                            ).first()
                            if user_data:
                                indicator_data['user_data'].append({
                                    'user_name': current_user.full_name,
                                    'status': user_data.status,
                                    'data': user_data.to_dict()
                                })
                    
                    # Add permission info for admin/moderator
                    if current_user.role in ['Admin', 'Moderator']:
                        permissions = UserPermission.query.filter_by(indicator_id=indicator.id).all()
                        indicator_data['permissions'] = []
                        for perm in permissions:
                            user_info = User.query.get(perm.user_id)
                            if user_info:
                                indicator_data['permissions'].append({
                                    'user_name': user_info.full_name,
                                    'can_view': perm.can_view,
                                    'can_edit': perm.can_edit
                                })
                    
                    item_data['indicators'].append(indicator_data)
            
            if item_data['indicators']:  # Only add items that have visible indicators
                report_data.append(item_data)
        
        return jsonify({'report': report_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_data_bp.route('/<indicator_item_id>/delete', methods=['DELETE'])
@jwt_required()
def delete_uploaded_file(indicator_item_id):
    """Delete uploaded image for indicator item"""
    logging.info(f"Request to delete image for indicator_item_id: {indicator_item_id}")
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        if not current_user:
            return jsonify({'error': 'User not found'}), 404

        indicator_item = IndicatorItem.query.get(indicator_item_id)

        if not indicator_item:
            return jsonify({'error': 'Indicator item not found'}), 404

        # Check if user has permission
        if not current_user.has_permission(indicator_item.indicator_id, 'edit'):
            return jsonify({'error': 'Access denied'}), 403

        user_data = UserData.query.filter_by(
            user_id=current_user_id,
            indicator_item_id=indicator_item_id
        ).first()
        logging.info(f"User data found for deletion: {user_data}")

        if not user_data or not user_data.image_path:
            return jsonify({'error': 'No image to delete'}), 404

        # Remove the file from the filesystem
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], user_data.image_path)
        logging.info(f"Image path for deletion: {user_data.image_path}")
        if os.path.exists(file_path):
            os.remove(file_path)

        # Remove the image path from the database
        user_data.image_path = None
        db.session.commit()

        return jsonify({'message': 'Image deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500