import os
import sqlite3
from models import db, User, Item
from utils.init_data import init_admin

def init_db(app):
    """Initialize database with tables and default data"""
    # Extract database path
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    db_path = db_uri.replace('sqlite:///', '')
    
    # Ensure the data directory exists with proper permissions
    data_dir = os.path.dirname(db_path)
    if data_dir:
        try:
            # Create directory if it doesn't exist
            if not os.path.exists(data_dir):
                os.makedirs(data_dir, mode=0o755, exist_ok=True)
                print(f"✓ Created data directory: {data_dir}")
            
            # Verify directory is writable
            if not os.access(data_dir, os.W_OK):
                raise PermissionError(
                    f"Data directory {data_dir} exists but is not writable. "
                    f"Current user: {os.getuid()}, Directory owner: {os.stat(data_dir).st_uid}"
                )
            
            print(f"✓ Data directory is writable: {data_dir}")
            
        except Exception as e:
            print(f"✗ Error with data directory: {e}")
            raise
    
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✓ Database tables created successfully")
            
            # Initialize admin user
            init_admin()
            
            # Add viewer user if it doesn't exist
            if not User.query.filter_by(username='viewer').first():
                viewer = User(username='viewer', role='viewer')
                viewer.set_password('viewer123')
                db.session.add(viewer)
                db.session.commit()
                print("✓ Viewer user created")
            
            # Add sample items if database is empty
            if Item.query.count() == 0:
                sample_items = [
                    Item(name='Laptop Dell XPS 15', sku='LAP001', category='Electronics', 
                         quantity=15, price=1200.00, reorder_level=5, 
                         description='High-performance laptop for development'),
                    Item(name='Office Chair Ergonomic', sku='FUR001', category='Furniture', 
                         quantity=25, price=250.00, reorder_level=10,
                         description='Comfortable office chair with lumbar support'),
                    Item(name='Wireless Mouse Logitech', sku='ELE001', category='Electronics', 
                         quantity=8, price=35.00, reorder_level=15,
                         description='Wireless mouse with USB receiver'),
                    Item(name='Desk Lamp LED', sku='OFF001', category='Office Supplies', 
                         quantity=42, price=45.00, reorder_level=20,
                         description='Adjustable LED desk lamp'),
                    Item(name='Monitor 27 inch 4K', sku='MON001', category='Electronics', 
                         quantity=12, price=450.00, reorder_level=8,
                         description='4K UHD monitor with HDR support'),
                    Item(name='Standing Desk', sku='FUR002', category='Furniture', 
                         quantity=6, price=800.00, reorder_level=3,
                         description='Electric height-adjustable standing desk'),
                ]
                for item in sample_items:
                    db.session.add(item)
                db.session.commit()
                print(f"✓ Added {len(sample_items)} sample items")
            
            print("✓ Database initialized successfully!")
            
            # Set secure permissions on the database file
            set_db_permissions(db_path)
            
        except Exception as e:
            print(f"✗ Error initializing database: {e}")
            raise

def set_db_permissions(db_path):
    """Set secure permissions for database file (chmod 600)"""
    try:
        if os.path.exists(db_path):
            os.chmod(db_path, 0o600)
            print(f"✓ Database permissions set to 600 for {db_path}")
        else:
            print(f"⚠ Database file not found yet: {db_path}")
    except Exception as e:
        print(f"⚠ Warning: Could not set database permissions: {e}")
        # Don't raise - this is not critical