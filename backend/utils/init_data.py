from models import db, User
from werkzeug.security import generate_password_hash

def init_admin():
    """Initialize admin user if not exists"""
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            role='admin'
        )
        admin.set_password('admin')
        db.session.add(admin)
        db.session.commit()