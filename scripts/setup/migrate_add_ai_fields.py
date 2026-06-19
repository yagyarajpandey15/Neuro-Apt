"""
Database migration script to add AI-powered fields and new tables
Run this after updating models.py
"""

import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from neuroapt.app import create_app, db
from neuroapt.app.models import TestResult, Question
from sqlalchemy import text

def migrate_add_ai_fields():
    """Add new AI-powered fields and tables to the database"""
    app = create_app()
    
    with app.app_context():
        print("Starting database migration for AI fields...")
        
        try:
            # Check if columns already exist before adding
            inspector = db.inspect(db.engine)
            
            # Add fields to TestResult table
            existing_columns = [col['name'] for col in inspector.get_columns('test_result')]
            
            print("\n1. Adding fields to TestResult table...")
            
            if 'ai_analysis' not in existing_columns:
                db.session.execute(text('ALTER TABLE test_result ADD COLUMN ai_analysis TEXT'))
                print("   ✓ Added ai_analysis column")
            else:
                print("   - ai_analysis column already exists")
            
            if 'confidence_level' not in existing_columns:
                db.session.execute(text('ALTER TABLE test_result ADD COLUMN confidence_level VARCHAR(20)'))
                print("   ✓ Added confidence_level column")
            else:
                print("   - confidence_level column already exists")
            
            if 'answer_pattern_flag' not in existing_columns:
                db.session.execute(text('ALTER TABLE test_result ADD COLUMN answer_pattern_flag VARCHAR(20)'))
                print("   ✓ Added answer_pattern_flag column")
            else:
                print("   - answer_pattern_flag column already exists")
            
            if 'contradictions_detected' not in existing_columns:
                db.session.execute(text('ALTER TABLE test_result ADD COLUMN contradictions_detected TEXT'))
                print("   ✓ Added contradictions_detected column")
            else:
                print("   - contradictions_detected column already exists")
            
            if 'interest_intersection' not in existing_columns:
                db.session.execute(text('ALTER TABLE test_result ADD COLUMN interest_intersection VARCHAR(50)'))
                print("   ✓ Added interest_intersection column")
            else:
                print("   - interest_intersection column already exists")
            
            # Add field to Question table
            question_columns = [col['name'] for col in inspector.get_columns('question')]
            
            print("\n2. Adding field to Question table...")
            
            if 'is_high_diagnostic' not in question_columns:
                db.session.execute(text('ALTER TABLE question ADD COLUMN is_high_diagnostic BOOLEAN DEFAULT 0'))
                print("   ✓ Added is_high_diagnostic column")
            else:
                print("   - is_high_diagnostic column already exists")
            
            # Create new tables
            existing_tables = inspector.get_table_names()
            
            print("\n3. Creating new tables...")
            
            # TestRetakeHistory table
            if 'test_retake_history' not in existing_tables:
                db.session.execute(text('''
                    CREATE TABLE test_retake_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        result_id INTEGER NOT NULL,
                        retake_number INTEGER NOT NULL,
                        taken_at DATETIME NOT NULL,
                        score_snapshot TEXT,
                        FOREIGN KEY (user_id) REFERENCES user(id),
                        FOREIGN KEY (result_id) REFERENCES test_result(id)
                    )
                '''))
                print("   ✓ Created test_retake_history table")
            else:
                print("   - test_retake_history table already exists")
            
            # MicroAssessment table
            if 'micro_assessment' not in existing_tables:
                db.session.execute(text('''
                    CREATE TABLE micro_assessment (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title VARCHAR(100) NOT NULL,
                        career_a VARCHAR(100) NOT NULL,
                        career_b VARCHAR(100) NOT NULL,
                        questions TEXT NOT NULL,
                        created_at DATETIME NOT NULL
                    )
                '''))
                print("   ✓ Created micro_assessment table")
            else:
                print("   - micro_assessment table already exists")
            
            # MicroAssessmentResult table
            if 'micro_assessment_result' not in existing_tables:
                db.session.execute(text('''
                    CREATE TABLE micro_assessment_result (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        assessment_id INTEGER NOT NULL,
                        answers TEXT,
                        ai_result TEXT,
                        taken_at DATETIME NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES user(id),
                        FOREIGN KEY (assessment_id) REFERENCES micro_assessment(id)
                    )
                '''))
                print("   ✓ Created micro_assessment_result table")
            else:
                print("   - micro_assessment_result table already exists")
            
            # Commit all changes
            db.session.commit()
            
            print("\n" + "="*60)
            print("✓ Database migration completed successfully!")
            print("="*60)
            print("\nNew fields added to TestResult:")
            print("  - ai_analysis (cached AI analysis JSON)")
            print("  - confidence_level (HIGH/MODERATE/LOW/UNRELIABLE)")
            print("  - answer_pattern_flag (decisive/ambivalent/random)")
            print("  - contradictions_detected (JSON list)")
            print("  - interest_intersection (e.g., 'STEM+Creative')")
            print("\nNew field added to Question:")
            print("  - is_high_diagnostic (Boolean flag)")
            print("\nNew tables created:")
            print("  - test_retake_history")
            print("  - micro_assessment")
            print("  - micro_assessment_result")
            print("\n")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error during migration: {str(e)}")
            print("Rolling back changes...")
            raise

if __name__ == "__main__":
    migrate_add_ai_fields()
