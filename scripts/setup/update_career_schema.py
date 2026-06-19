"""
Update Career Schema Script

This script creates the necessary database tables for the Career models.
Run this script after adding the Career models to models.py.
"""

import os
import sys
from flask import Flask
from flask_migrate import Migrate, upgrade
from neuroapt.app import create_app, db
from neuroapt.app.models import Career, CareerSkill, CareerEducation, CareerSalary

def create_migration_app():
    """Create a Flask app for database migrations"""
    app = create_app()
    return app

def run_migrations():
    """Run database migrations to create Career tables"""
    app = create_migration_app()
    
    with app.app_context():
        migrate = Migrate(app, db)
        
        # Check if tables already exist
        inspector = db.inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        if 'career' in existing_tables:
            print("Career tables already exist. No migration needed.")
            return
        
        print("Creating Career tables...")
        
        # Create tables directly if they don't exist
        db.create_all()
        
        print("Career tables created successfully!")
        print("You can now populate careers using the admin interface.")

if __name__ == "__main__":
    run_migrations() 