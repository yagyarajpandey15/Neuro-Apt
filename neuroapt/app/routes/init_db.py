"""
One-time database initialization route
Visit /initialize-database once after deployment to create admin user
"""
from flask import Blueprint, jsonify
from neuroapt.app import db, bcrypt
from neuroapt.app.models import User
import os

init_bp = Blueprint('init', __name__)

@init_bp.route('/initialize-database', methods=['GET'])
def initialize_database():
    """
    Initialize database with admin user.
    This should only be called once after deployment.
    """
    try:
        # Ensure all tables are created
        db.create_all()
        
        # Check if admin already exists
        admin_email = "admin@neuroapt.com"
        existing_admin = User.query.filter_by(email=admin_email).first()
        
        if existing_admin:
            return jsonify({
                'status': 'already_initialized',
                'message': 'Admin user already exists!',
                'admin_email': admin_email
            }), 200
        
        # Create admin user
        admin_username = "admin"
        admin_password = "Admin123!"
        
        hashed_password = bcrypt.generate_password_hash(admin_password).decode('utf-8')
        admin_user = User(
            username=admin_username,
            email=admin_email,
            password=hashed_password,
            is_admin=True
        )
        
        db.session.add(admin_user)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Database initialized successfully!',
            'admin_credentials': {
                'email': admin_email,
                'password': admin_password,
                'note': 'Please change this password after first login!'
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
