from flask import Blueprint, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.assessment import Assessment, AssessmentItem, Indicator, IndicatorItem
from app.models.user_data import UserPermission
from database import db
from datetime import datetime
#from app.routes.auth import auth_bp
import logging

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Add StreamHandler to display logs in the console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logging.getLogger().addHandler(console_handler)

logging.info("App initialized successfully.")

assessment_bp = Blueprint('assessment', __name__)
#CORS(assessment_bp, resources={r"/*": {"origins": "*"}})
#CORS(auth_bp, resources={r"/*": {"origins": "*"}})

@assessment_bp.route('', methods=['GET'])
@assessment_bp.route('/', methods=['GET'])
@jwt_required()
def get_assessments():
    logging.info("Fetching all assessments.")
    try:
        current_user_id = get_jwt_identity()
        logging.info(f"Current user ID: {current_user_id}")
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
            
        # Admin and Moderator can see all assessments
        if current_user.role in ['Admin', 'Moderator']:
            assessments = Assessment.query.all()
        else:
            # Regular users can only see published assessments
            assessments = Assessment.query.filter_by(status='published').all()
            
        logging.info("Assessments fetched successfully.")
        return jsonify({
            'assessments': [assessment.to_dict() for assessment in assessments]
        }), 200
    except Exception as e:
        logging.error(f"Error fetching assessments: {e}")
        return jsonify({'error': str(e)}), 500

@assessment_bp.route('', methods=['POST'])
@assessment_bp.route('/', methods=['POST'])
@jwt_required()
def create_assessment():
    #logging.info("Create_assessment function called.")
    try:
        current_user_id = get_jwt_identity()
        #logging.info(f"Current user ID: {current_user_id}")
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

        #logging.info("Before adding assessment to the session.")
        db.session.add(assessment)
        #logging.info("After adding assessment to the session. Flushing session.")
        db.session.flush()  # Ensure assessment.id is generated
        #logging.info(f"Assessment flushed with ID: {assessment.id}")

        # Add assessment items if provided
        if data.get('items'):
            for item_idx, item_data in enumerate(data['items']):
                if item_data.get('title'):
                    if not assessment.id:
                        raise ValueError("Assessment ID is not set. Cannot add assessment items.")

                    assessment_item = AssessmentItem(
                        assessment_id=assessment.id,
                        title=item_data['title'],
                        order_index=item_idx
                    )
                    db.session.add(assessment_item)
                    db.session.flush()
                    
                    # Debugging: Log assessment_item_id
                    #logging.info(f"AssessmentItem ID: {assessment_item.id}")
                    
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
                                db.session.flush()
                                
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
                                            db.session.flush()
                                
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
                                            db.session.flush()
        
        logging.info("Committing transaction.")
        db.session.commit()
        logging.info("Transaction committed successfully.")
        response = {
            'message': 'Assessment created successfully',
            'assessment': assessment.to_dict(include_items=True)
        }
        #logging.info(f"Response sent to frontend: {response}")
        return jsonify(response), 201
    except Exception as e:
        logging.error(f"Error creating assessment: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@assessment_bp.route('', methods=['OPTIONS'])
@assessment_bp.route('/', methods=['OPTIONS'])
def handle_options():
    return '', 200


@assessment_bp.route('/<assessment_id>', methods=['GET'])
@jwt_required()
def get_assessment(assessment_id):
    logging.info(f"Fetching assessment with ID: {assessment_id}")
    try:
        current_user_id = get_jwt_identity()
        #logging.info(f"Current user ID: {current_user_id}")
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
            
        assessment = Assessment.query.get(assessment_id)
        
        if not assessment:
            return jsonify({'error': 'Assessment not found'}), 404
            
        # Check permissions
        if current_user.role not in ['Admin', 'Moderator'] and assessment.status != 'published':
            return jsonify({'error': 'Access denied'}), 403
            
        logging.info("Assessment fetched successfully.")
        return jsonify({
            'assessment': assessment.to_dict(include_items=True)
        }), 200
        
    except Exception as e:
        logging.error(f"Error fetching assessment: {e}")
        return jsonify({'error': str(e)}), 500

@assessment_bp.route('/<assessment_id>', methods=['PUT'])
@jwt_required()
def update_assessment(assessment_id):
    logging.info(f"Updating assessment with ID: {assessment_id}")
    try:
        current_user_id = get_jwt_identity()
        #logging.info(f"Current user ID: {current_user_id}")
        current_user = User.query.get(current_user_id)
        
        if not current_user or current_user.role not in ['Admin', 'Moderator']:
            logging.error("Insufficient permissions.")
            return jsonify({'error': 'Insufficient permissions'}), 403
            
        assessment = Assessment.query.get(assessment_id)
        
        if not assessment:
            logging.error(f"Assessment with ID {assessment_id} not found.")
            return jsonify({'error': 'Assessment not found'}), 404
            
        data = request.get_json()
        #logging.info(f"Data received for update: {data}")
        
        if not data:
            logging.error("No data provided for update.")
            return jsonify({'error': 'No data provided'}), 400
        
        # Update status if provided
        if 'status' in data:
            #logging.info(f"Updating assessment status to: {data['status']}")
            assessment.status = data['status']
        
        # Update items
        if 'items' in data:
            for item_data in data['items']:
                #logging.info(f"Processing item: {item_data}")
                assessment_item = AssessmentItem.query.filter_by(
                    assessment_id=assessment.id,
                    order_index=item_data['order_index']
                ).first()
                
                if not assessment_item:
                    # Create new item if it doesn't exist
                    assessment_item = AssessmentItem(
                        assessment_id=assessment.id,
                        title=item_data['title'],
                        order_index=item_data['order_index']
                    )
                    db.session.add(assessment_item)
                else:
                    # Update existing item
                    assessment_item.title = item_data['title']
                
                db.session.flush()  # Ensure ID is generated
                
                # Update indicators
                if 'indicators' in item_data:
                    for indicator_data in item_data['indicators']:
                        #logging.info(f"Processing indicator: {indicator_data}")
                        indicator = Indicator.query.filter_by(
                            assessment_item_id=assessment_item.id,
                            order_index=indicator_data['order_index']
                        ).first()
                        
                        if not indicator:
                            # Create new indicator if it doesn't exist
                            indicator = Indicator(
                                assessment_item_id=assessment_item.id,
                                title=indicator_data['title'],
                                order_index=indicator_data['order_index']
                            )
                            db.session.add(indicator)
                        else:
                            # Update existing indicator
                            indicator.title = indicator_data['title']
                        
                        db.session.flush()  # Ensure ID is generated
                        
                        # Update indicator items
                        if 'items' in indicator_data:
                            for item_data in indicator_data['items']:
                                #logging.info(f"Processing indicator item: {item_data}")
                                indicator_item = IndicatorItem.query.filter_by(
                                    indicator_id=indicator.id,
                                    order_index=item_data['order_index']
                                ).first()
                                
                                if not indicator_item:
                                    # Create new indicator item if it doesn't exist
                                    indicator_item = IndicatorItem(
                                        indicator_id=indicator.id,
                                        title=item_data['title'],
                                        target_value=item_data['target_value'],
                                        actual_target=item_data['actual_target'],
                                        order_index=item_data['order_index']
                                    )
                                    db.session.add(indicator_item)
                                else:
                                    # Update existing indicator item
                                    indicator_item.title = item_data['title']
                                    indicator_item.target_value = item_data['target_value']
                                    indicator_item.actual_target = item_data['actual_target']
                        
                        # Update permissions
                        if 'permissions' in indicator_data:
                            for permission_data in indicator_data['permissions']:
                                #logging.info(f"Processing permission: {permission_data}")
                                permission = UserPermission.query.filter_by(
                                    user_id=permission_data['user_id'],
                                    indicator_id=indicator.id
                                ).first()
                                
                                if not permission:
                                    # Create new permission if it doesn't exist
                                    permission = UserPermission(
                                        user_id=permission_data['user_id'],
                                        indicator_id=indicator.id,
                                        can_view=permission_data.get('can_view', False),
                                        can_edit=permission_data.get('can_edit', False)
                                    )
                                    db.session.add(permission)
                                else:
                                    # Update existing permission
                                    permission.can_view = permission_data.get('can_view', False)
                                    permission.can_edit = permission_data.get('can_edit', False)
        
        assessment.updated_at = datetime.utcnow()
        logging.info("Committing changes to the database.")
        db.session.commit()
        db.session.refresh(assessment)
        logging.info("Changes committed successfully.")
        
        #logging.info(f"Assessment data before response: {assessment.to_dict(include_items=True)}")
        return jsonify({
            'message': 'Assessment updated successfully',
            'assessment': assessment.to_dict(include_items=True)
        }), 200
        
    except Exception as e:
        logging.error(f"Error updating assessment: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@assessment_bp.route('/<assessment_id>', methods=['DELETE'])
@jwt_required()
def delete_assessment(assessment_id):
    logging.info(f"Deleting assessment with ID: {assessment_id}")
    try:
        current_user_id = get_jwt_identity()
        #logging.info(f"Current user ID: {current_user_id}")
        current_user = User.query.get(current_user_id)
        
        if not current_user or current_user.role not in ['Admin', 'Moderator']:
            return jsonify({'error': 'Insufficient permissions'}), 403
            
        assessment = Assessment.query.get(assessment_id)
        
        if not assessment:
            return jsonify({'error': 'Assessment not found'}), 404
            
        db.session.delete(assessment)
        db.session.commit()
        
        logging.info("Assessment deleted successfully.")
        return jsonify({'message': 'Assessment deleted successfully'}), 200
        
    except Exception as e:
        logging.error(f"Error deleting assessment: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

