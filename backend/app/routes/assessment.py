from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.assessment import Assessment, AssessmentItem, Indicator, IndicatorItem
from app.models.user_data import UserPermission
from database import db
from datetime import datetime


assessment_bp = Blueprint('assessment', __name__)

@assessment_bp.route('/', methods=['GET'])
@jwt_required()
def get_assessments():
    """Get all assessments based on user role"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
            
        # Admin and Moderator can see all assessments
        if current_user.role in ['Admin', 'Moderator']:
            assessments = Assessment.query.all()
        else:
            # Regular users can only see published assessments
            assessments = Assessment.query.filter_by(status='published').all()
            
        return jsonify({
            'assessments': [assessment.to_dict() for assessment in assessments]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@assessment_bp.route('/', methods=['POST'])
@jwt_required()
def create_assessment():
    """Create new assessment"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user or current_user.role not in ['Admin', 'Moderator']:
            return jsonify({'error': 'Insufficient permissions'}), 403
            
        data = request.get_json()
        
        if not data or not data.get('fiscal_year'):
            return jsonify({'error': 'Fiscal year is required'}), 400
            
        # Generate assessment name
        base_name = f"ปีงบประมาณ{data['fiscal_year']}"
        name = base_name
        counter = 1
        
        # Check for duplicate names and append number if needed
        while Assessment.query.filter_by(name=name).first():
            name = f"{base_name}-{counter}"
            counter += 1
            
        assessment = Assessment(
            name=name,
            fiscal_year=data['fiscal_year'],
            created_by=current_user_id
        )
        
        db.session.add(assessment)
        
        # Add assessment items if provided
        if data.get('items'):
            for item_idx, item_data in enumerate(data['items']):
                if item_data.get('title'):
                    assessment_item = AssessmentItem(
                        assessment_id=assessment.id,
                        title=item_data['title'],
                        order_index=item_idx
                    )
                    db.session.add(assessment_item)
                    
                    # Add indicators if provided
                    if item_data.get('indicators'):
                        for ind_idx, indicator_data in enumerate(item_data['indicators']):
                            if indicator_data.get('title'):
                                indicator = Indicator(
                                    assessment_item_id=assessment_item.id,
                                    title=indicator_data['title'],
                                    order_index=ind_idx
                                )
                                db.session.add(indicator)
                                
                                # Add indicator items if provided
                                if indicator_data.get('items'):
                                    for itm_idx, indicator_item_data in enumerate(indicator_data['items']):
                                        if indicator_item_data.get('title'):
                                            indicator_item = IndicatorItem(
                                                indicator_id=indicator.id,
                                                title=indicator_item_data['title'],
                                                target_value=indicator_item_data.get('target_value'),
                                                actual_target=indicator_item_data.get('actual_target'),
                                                order_index=itm_idx
                                            )
                                            db.session.add(indicator_item)
                                
                                # Add user permissions if provided
                                if indicator_data.get('permissions'):
                                    for permission_data in indicator_data['permissions']:
                                        if permission_data.get('user_id'):
                                            permission = UserPermission(
                                                user_id=permission_data['user_id'],
                                                indicator_id=indicator.id,
                                                can_view=permission_data.get('can_view', False),
                                                can_edit=permission_data.get('can_edit', False)
                                            )
                                            db.session.add(permission)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Assessment created successfully',
            'assessment': assessment.to_dict(include_items=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@assessment_bp.route('/<assessment_id>', methods=['GET'])
@jwt_required()
def get_assessment(assessment_id):
    """Get specific assessment"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
            
        assessment = Assessment.query.get(assessment_id)
        
        if not assessment:
            return jsonify({'error': 'Assessment not found'}), 404
            
        # Check permissions
        if current_user.role not in ['Admin', 'Moderator'] and assessment.status != 'published':
            return jsonify({'error': 'Access denied'}), 403
            
        return jsonify({
            'assessment': assessment.to_dict(include_items=True)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@assessment_bp.route('/<assessment_id>', methods=['PUT'])
@jwt_required()
def update_assessment(assessment_id):
    """Update assessment"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user or current_user.role not in ['Admin', 'Moderator']:
            return jsonify({'error': 'Insufficient permissions'}), 403
            
        assessment = Assessment.query.get(assessment_id)
        
        if not assessment:
            return jsonify({'error': 'Assessment not found'}), 404
            
        data = request.get_json()
        
        # Update status if provided
        if 'status' in data:
            if data['status'] == 'published':
                # Validate that all required fields are filled
                validation_errors = []
                for item in assessment.items:
                    if not item.title.strip():
                        validation_errors.append(f"Assessment item title is required")
                    for indicator in item.indicators:
                        if not indicator.title.strip():
                            validation_errors.append(f"Indicator title is required")
                        for indicator_item in indicator.items:
                            if not indicator_item.title.strip():
                                validation_errors.append(f"Indicator item title is required")
                
                if validation_errors:
                    return jsonify({
                        'error': 'Validation failed',
                        'details': validation_errors
                    }), 400
                    
            assessment.status = data['status']
            
        assessment.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Assessment updated successfully',
            'assessment': assessment.to_dict(include_items=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@assessment_bp.route('/<assessment_id>', methods=['DELETE'])
@jwt_required()
def delete_assessment(assessment_id):
    """Delete assessment"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user or current_user.role not in ['Admin', 'Moderator']:
            return jsonify({'error': 'Insufficient permissions'}), 403
            
        assessment = Assessment.query.get(assessment_id)
        
        if not assessment:
            return jsonify({'error': 'Assessment not found'}), 404
            
        db.session.delete(assessment)
        db.session.commit()
        
        return jsonify({'message': 'Assessment deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500