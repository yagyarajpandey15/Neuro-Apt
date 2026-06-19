import sqlite3
import os

def update_database_schema():
    """
    Update the database schema to add new personality trait and work attribute columns
    """
    print("Updating database schema...")
    
    # Path to the database file
    db_path = os.path.join('neuroapt', 'app', 'neuroapt.db')
    
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        return
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if the Career table exists, if not create it
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS career (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            work_environment TEXT,
            job_outlook TEXT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
        ''')
        
        # Add new columns to TestResult table for personality traits
        columns_to_add = [
            # Personality trait scores
            ('openness_score', 'INTEGER DEFAULT 0'),
            ('conscientiousness_score', 'INTEGER DEFAULT 0'),
            ('extraversion_score', 'INTEGER DEFAULT 0'),
            ('agreeableness_score', 'INTEGER DEFAULT 0'),
            ('neuroticism_score', 'INTEGER DEFAULT 0'),
            
            # Work attribute scores
            ('leadership_score', 'INTEGER DEFAULT 0'),
            ('teamwork_score', 'INTEGER DEFAULT 0'),
            ('creativity_score', 'INTEGER DEFAULT 0'),
            ('analytical_score', 'INTEGER DEFAULT 0'),
            ('communication_score', 'INTEGER DEFAULT 0'),
            ('adaptability_score', 'INTEGER DEFAULT 0'),
        ]
        
        # Add new columns to QuestionOption table
        option_columns = [
            ('trait_impact', 'TEXT'),
            ('trait_value', 'INTEGER DEFAULT 0')
        ]
        
        # Add columns to TestResult table
        for column_name, column_type in columns_to_add:
            try:
                cursor.execute(f"ALTER TABLE test_result ADD COLUMN {column_name} {column_type}")
                print(f"Added column {column_name} to test_result table")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"Column {column_name} already exists in test_result table")
                else:
                    print(f"Error adding column {column_name}: {e}")
        
        # Add columns to QuestionOption table
        for column_name, column_type in option_columns:
            try:
                cursor.execute(f"ALTER TABLE question_option ADD COLUMN {column_name} {column_type}")
                print(f"Added column {column_name} to question_option table")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"Column {column_name} already exists in question_option table")
                else:
                    print(f"Error adding column {column_name}: {e}")
        
        # Commit the changes
        conn.commit()
        print("Database schema updated successfully")
        
    except Exception as e:
        print(f"Error updating database schema: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    update_database_schema() 