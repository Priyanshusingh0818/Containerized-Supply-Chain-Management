import os
from datetime import timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from models import db, User
from routes.items import items_bp
from routes.transactions import transactions_bp
from routes.analytics import analytics_bp
from routes.audit import audit_bp
from utils.db import init_db, set_db_permissions
from config import get_config

# Get validated configuration
Config = get_config()

app = Flask(__name__)

# Load configuration from config class
app.config.from_object(Config)

# Environment detection
FLASK_ENV = Config.FLASK_ENV
IS_PRODUCTION = FLASK_ENV == 'production'

# CORS Configuration - Secure for production
if IS_PRODUCTION:
    # Strict CORS in production
    CORS(app, resources={
        r"/api/*": {
            "origins": Config.CORS_ORIGINS,
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "max_age": 3600
        }
    })
    socketio = SocketIO(app, cors_allowed_origins=Config.CORS_ORIGINS)
else:
    # Relaxed CORS for development
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Content-Type", "Authorization"]
        }
    })
    socketio = SocketIO(app, cors_allowed_origins="*")

db.init_app(app)
jwt = JWTManager(app)

# Make socketio available on the Flask app for utils to emit from
app.socketio = socketio

# JWT Error Handlers
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        'message': 'Token has expired',
        'error': 'token_expired'
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'message': 'Invalid token',
        'error': 'invalid_token'
    }), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        'message': 'Authorization token is missing',
        'error': 'authorization_required'
    }), 401

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

# Authentication Routes
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
@jwt_required()  # Require authentication to register new users
def register():
    """User registration endpoint - Admin only in production"""
    # In production, only admins should create users
    if IS_PRODUCTION:
        from flask_jwt_extended import get_jwt
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({'message': 'Admin access required'}), 403
    
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

# Health & Info Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db.session.execute('SELECT 1')
        db_status = 'connected'
    except Exception as e:
        db_status = 'disconnected'
        
    return jsonify({
        'status': 'healthy' if db_status == 'connected' else 'degraded',
        'message': 'InvGuard API is running',
        'database': db_status,
        'environment': FLASK_ENV
    }), 200

@app.route('/api/', methods=['GET'])
def api_root():
    """API root endpoint"""
    return jsonify({
        'message': 'Welcome to InvGuard API',
        'version': '1.0.0',
        'environment': FLASK_ENV,
        'endpoints': {
            'auth': '/api/auth/login, /api/auth/register',
            'items': '/api/items',
            'transactions': '/api/transactions',
            'analytics': '/api/analytics/*',
            'health': '/api/health'
        }
    }), 200

# Error Handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'message': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'message': 'Internal server error'}), 500

@app.errorhandler(403)
def forbidden(error):
    return jsonify({'message': 'Access forbidden'}), 403

if __name__ == '__main__':
    # Use socketio.run so Flask-SocketIO properly initializes the async server
    debug_mode = not IS_PRODUCTION
    socketio.run(app, host='0.0.0.0', port=5000, debug=debug_mode)