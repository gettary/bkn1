from app import db
import uuid
from datetime import datetime

class Assessment(db.Model):
    __tablename__ = 'assessments'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False, unique=True)
    fiscal_year = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum('draft', 'published', name='assessment_status'), nullable=False, default='draft')
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('AssessmentItem', backref='assessment', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, include_items=False):
        """Convert assessment to dictionary"""
        result = {
            'id': self.id,
            'name': self.name,
            'fiscal_year': self.fiscal_year,
            'status': self.status,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_items:
            result['items'] = [item.to_dict(include_indicators=True) for item in self.items]
            
        return result

class AssessmentItem(db.Model):
    __tablename__ = 'assessment_items'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    assessment_id = db.Column(db.String(36), db.ForeignKey('assessments.id'), nullable=False)
    title = db.Column(db.String(500), nullable=False)
    order_index = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    indicators = db.relationship('Indicator', backref='assessment_item', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, include_indicators=False):
        """Convert assessment item to dictionary"""
        result = {
            'id': self.id,
            'assessment_id': self.assessment_id,
            'title': self.title,
            'order_index': self.order_index,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_indicators:
            result['indicators'] = [indicator.to_dict(include_items=True) for indicator in self.indicators]
            
        return result

class Indicator(db.Model):
    __tablename__ = 'indicators'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    assessment_item_id = db.Column(db.String(36), db.ForeignKey('assessment_items.id'), nullable=False)
    title = db.Column(db.String(500), nullable=False)
    order_index = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    items = db.relationship('IndicatorItem', backref='indicator', lazy=True, cascade='all, delete-orphan')
    permissions = db.relationship('UserPermission', backref='indicator', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, include_items=False):
        """Convert indicator to dictionary"""
        result = {
            'id': self.id,
            'assessment_item_id': self.assessment_item_id,
            'title': self.title,
            'order_index': self.order_index,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_items:
            result['items'] = [item.to_dict() for item in self.items]
            
        return result

class IndicatorItem(db.Model):
    __tablename__ = 'indicator_items'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    indicator_id = db.Column(db.String(36), db.ForeignKey('indicators.id'), nullable=False)
    title = db.Column(db.String(500), nullable=False)
    target_value = db.Column(db.String(200))
    actual_target = db.Column(db.String(200))
    order_index = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user_data = db.relationship('UserData', backref='indicator_item', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert indicator item to dictionary"""
        return {
            'id': self.id,
            'indicator_id': self.indicator_id,
            'title': self.title,
            'target_value': self.target_value,
            'actual_target': self.actual_target,
            'order_index': self.order_index,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }