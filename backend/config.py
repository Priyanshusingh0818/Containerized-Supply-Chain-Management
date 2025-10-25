import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration"""
    # Required environment variables
    REQUIRED_ENV_VARS = ['JWT_SECRET_KEY']
    
    # Flask
    SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = 12 * 3600  # 12 hours in seconds
    JWT_TOKEN_LOCATION = ['headers']
    
    # Database
    DATABASE_PATH = os.getenv('DATABASE_PATH', '/app/data/inventory.db')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # Admin Credentials (for initial setup)
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
    
    @classmethod
    def validate(cls):
        """Validate that all required environment variables are set"""
        missing = []
        for var in cls.REQUIRED_ENV_VARS:
            if not os.getenv(var):
                missing.append(var)
        
        if missing:
            print(f"❌ ERROR: Missing required environment variables: {', '.join(missing)}")
            print("Please set these in your .env file")
            sys.exit(1)
        
        # Check for weak default passwords in production
        if os.getenv('FLASK_ENV') == 'production':
            admin_pass = os.getenv('ADMIN_PASSWORD', '')
            if admin_pass in ['admin', 'admin123', 'password', '']:
                print("❌ ERROR: Weak or missing ADMIN_PASSWORD in production!")
                print("Please set a strong password in your .env file")
                sys.exit(1)
        
        print("✓ Configuration validated successfully")


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    FLASK_ENV = 'development'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    FLASK_ENV = 'production'
    
    # Override CORS for production
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'https://yourdomain.com').split(',')
    
    @classmethod
    def validate(cls):
        """Additional production validations"""
        super().validate()
        
        # Ensure CORS is not set to wildcard
        if '*' in cls.CORS_ORIGINS:
            print("⚠ WARNING: CORS_ORIGINS is set to '*' in production!")
            print("This allows any website to access your API")
            response = input("Continue anyway? (yes/no): ")
            if response.lower() != 'yes':
                sys.exit(1)


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    FLASK_ENV = 'testing'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get configuration based on FLASK_ENV"""
    env = os.getenv('FLASK_ENV', 'development')
    config_class = config.get(env, config['default'])
    config_class.validate()
    return config_class