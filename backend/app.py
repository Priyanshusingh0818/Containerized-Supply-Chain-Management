import os
from datetime import timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from dotenv import load_dotenv
from models import db, User
from routes.items import items_bp
from routes.transactions import transactions_bp
from routes.analytics import analytics_bp
from routes.audit import audit_bp
from utils.db import init_db, set_db_permissions

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:////app/data/inventory.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Longer access token expiry to reduce unexpected 401s during normal use
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=12)
app.config['JWT_TOKEN_LOCATION'] = ['headers']

# Initialize extensions
CORS(app, resources={r"/api/*": {"origins": "*", "allow_headers": ["Content-Type", "Authorization"], "expose_headers": ["Content-Type", "Authorization"]}})
socketio = SocketIO(app, cors_allowed_origins="*")
db.init_app(app)
jwt = JWTManager(app)
# Make socketio available on the Flask app for utils to emit from
app.socketio = socketio

# Register blueprints
app.register_blueprint(items_bp, url_prefix='/api')
app.register_blueprint(transactions_bp, url_prefix='/api')
app.register_blueprint(analytics_bp, url_prefix='/api')
app.register_blueprint(audit_bp, url_prefix='/api')

# Initialize database
with app.app_context():
    init_db(app)
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    if os.path.exists(db_path):
        set_db_permissions(db_path)

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Missing username or password'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401
    
    # Create access token with role
    access_token = create_access_token(
        identity=user.username,
        additional_claims={'role': user.role}
    )
    
    return jsonify({
        'access_token': access_token,
        'user': user.to_dict()
    }), 200

@app.route('/api/auth/register', methods=['POST'])
def register():
    """User registration endpoint"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Missing username or password'}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400
    
    user = User(
        username=data['username'],
        role=data.get('role', 'viewer')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict()), 201

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'InvGuard API is running'
    }), 200

@app.route('/api/', methods=['GET'])
def api_root():
    """API root endpoint"""
    return jsonify({
        'message': 'Welcome to InvGuard API',
        'version': '1.0.0',
        'endpoints': {
            'auth': '/api/auth/login, /api/auth/register',
            'items': '/api/items',
            'transactions': '/api/transactions',
            'analytics': '/api/analytics/*'
        }
    }), 200

if __name__ == '__main__':
    # Use socketio.run so Flask-SocketIO properly initializes the async server
    # Eventlet is installed in the container (requirements.txt)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)