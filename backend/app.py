from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql+psycopg2://bkn1_user:bkn1_password@localhost:5432/bkn1_db?client_encoding=utf8')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jd2faf048fdd50310e08f393074652b444ca68160e355008e95cd674026fd85a4')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400  # 24 hours
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize database
from database import db
db.init_app(app)

# Initialize other extensions
jwt = JWTManager(app)
#CORS(app)
# เปิดใช้งาน CORS สำหรับทุก origin
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/api/assessments', methods=['POST'])
def create_assessment():
    return {"message": "Assessment created"}, 200

# Create uploads directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Import models
from app.models.user import User
from app.models.assessment import Assessment, AssessmentItem, Indicator, IndicatorItem
from app.models.user_data import UserData, UserPermission

# Import routes
from app.routes.auth import auth_bp
from app.routes.assessment import assessment_bp
from app.routes.user_data import user_data_bp

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(assessment_bp, url_prefix='/api/assessments')
app.register_blueprint(user_data_bp, url_prefix='/api/user-data')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)