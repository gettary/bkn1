from app import db
import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('Admin', 'Moderator', 'User', name='user_roles'), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assessments = db.relationship('Assessment', backref='creator', lazy=True)
    user_data = db.relationship('UserData', backref='user', lazy=True)
    permissions = db.relationship('UserPermission', backref='user', lazy=True)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def has_permission(self, indicator_id, permission_type='view'):
        """Check if user has permission for specific indicator"""
        if self.role in ['Admin', 'Moderator']:
            return True
            
        permission = UserPermission.query.filter_by(
            user_id=self.id,
            indicator_id=indicator_id
        ).first()
        
        if not permission:
            return False
            
        if permission_type == 'view':
            return permission.can_view
        elif permission_type == 'edit':
            return permission.can_edit
            
        return False
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'full_name': self.full_name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }