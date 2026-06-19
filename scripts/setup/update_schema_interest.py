import sqlite3
import os
import json

def update_database_schema():
    """
    Update the database schema to add interest category columns and answer patterns
    """
    print("Updating database schema for interest categories...")
    
    # Path to the database file
    db_path = os.path.join('neuroapt', 'app', 'neuroapt.db')
    
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        return
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Add new columns to TestResult table for interest categories
        columns_to_add = [
            # Interest category scores
            ('stem_tech_score', 'INTEGER DEFAULT 0'),
            ('creative_media_score', 'INTEGER DEFAULT 0'),
            ('people_oriented_score', 'INTEGER DEFAULT 0'),
            ('business_management_score', 'INTEGER DEFAULT 0'),
            ('legal_governance_score', 'INTEGER DEFAULT 0'),
            ('logistics_distribution_score', 'INTEGER DEFAULT 0'),
            # Answer patterns for career matching
            ('answer_patterns', 'TEXT DEFAULT "{}"')
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
        
        # Commit the changes
        conn.commit()
        print("Database schema updated successfully for interest categories")
        
    except Exception as e:
        print(f"Error updating database schema: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    update_database_schema() 