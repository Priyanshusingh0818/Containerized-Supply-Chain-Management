import os
from datetime import timedelta
from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt
from dotenv import load_dotenv
from models import db, User
from routes.items import items_bp
from routes.transactions import transactions_bp
from routes.analytics import analytics_bp
from routes.audit import audit_bp
from utils.db import init_db, set_db_permissions

# Load environment variables from .env file (development only)
# In production (Render), use environment variables set in dashboard
load_dotenv()

app = Flask(__name__)

# Configuration
JWT_SECRET = os.getenv('JWT_SECRET_KEY')
if not JWT_SECRET:
    env_hint = "Set environment variables in Render Dashboard" if os.getenv('RENDER') else "Check your .env file"
    raise ValueError(f"JWT_SECRET_KEY environment variable is not set! {env_hint}")

app.config['SECRET_KEY'] = JWT_SECRET
app.config['JWT_SECRET_KEY'] = JWT_SECRET
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.getenv('DATABASE_PATH', '/data/inventory.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=12)
app.config['JWT_TOKEN_LOCATION'] = ['headers']

# Environment detection
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
IS_PRODUCTION = FLASK_ENV == 'production'

# CORS Configuration
CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
print(f"CORS Origins: {CORS_ORIGINS}")

if IS_PRODUCTION and '*' not in CORS_ORIGINS:
    # Strict CORS in production
    CORS(app, resources={
        r"/api/*": {
            "origins": CORS_ORIGINS,
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "max_age": 3600
        }
    })
    socketio = SocketIO(app, cors_allowed_origins=CORS_ORIGINS)
else:
    # Relaxed CORS for development or if wildcard is set
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
    # Create directory if it doesn't exist
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    
    if os.path.exists(db_path):
        set_db_permissions(db_path)
    print(f"Database initialized at: {db_path}")

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
    
    access_token = create_access_token(
        identity=user.username,
        additional_claims={'role': user.role}
    )
    
    return jsonify({
        'access_token': access_token,
        'user': user.to_dict()
    }), 200

@app.route('/api/auth/register', methods=['POST'])
@jwt_required()
def register():
    """User registration endpoint - Admin only in production"""
    if IS_PRODUCTION:
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
        db.session.execute('SELECT 1')
        db_status = 'connected'
    except Exception as e:
        print(f"Database health check failed: {e}")
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

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    # If a frontend URL is supplied via environment (e.g. FRONTEND_URL),
    # redirect the root request to the frontend site. This is useful when
    # backend and frontend are deployed as separate services (Render, Docker, etc.).
    frontend_url = os.getenv('FRONTEND_URL')
    if frontend_url:
        # Ensure we redirect to the frontend (preserve trailing slash behaviour)
        return redirect(frontend_url, code=302)

    return jsonify({
        'message': 'InvGuard API Server',
        'api': '/api/',
        'health': '/api/health'
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
    # Get port from environment (Render uses PORT env variable)
    port = int(os.getenv('PORT', 5000))
    debug_mode = not IS_PRODUCTION
    
    print(f"Starting server on port {port}")
    print(f"Environment: {FLASK_ENV}")
    print(f"Debug mode: {debug_mode}")
    
    socketio.run(app, host='0.0.0.0', port=port, debug=debug_mode)
