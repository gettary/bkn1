from database import db
import uuid
from datetime import datetime

class UserData(db.Model):
    __tablename__ = 'user_data'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    indicator_item_id = db.Column(db.String(36), db.ForeignKey('indicator_items.id'), nullable=False)
    performance = db.Column(db.String(500))
    rate = db.Column(db.String(100))
    score = db.Column(db.String(100))
    image_path = db.Column(db.String(500))
    status = db.Column(db.Enum('draft', 'complete', name='user_data_status'), nullable=False, default='draft')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint for user and indicator item
    __table_args__ = (db.UniqueConstraint('user_id', 'indicator_item_id'),)
    
    def to_dict(self):
        """Convert user data to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'indicator_item_id': self.indicator_item_id,
            'performance': self.performance,
            'rate': self.rate,
            'score': self.score,
            'image_path': self.image_path,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class UserPermission(db.Model):
    __tablename__ = 'user_permissions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    indicator_id = db.Column(db.String(36), db.ForeignKey('indicators.id'), nullable=False)
    can_view = db.Column(db.Boolean, default=False)
    can_edit = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint for user and indicator
    __table_args__ = (db.UniqueConstraint('user_id', 'indicator_id'),)
    
    def to_dict(self):
        """Convert user permission to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'indicator_id': self.indicator_id,
            'can_view': self.can_view,
            'can_edit': self.can_edit,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }