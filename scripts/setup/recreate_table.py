import sqlite3
import os
import shutil
from datetime import datetime

# Path to the SQLite database
db_path = os.path.join('neuroapt', 'app', 'neuroapt.db')

print(f"Database path: {os.path.abspath(db_path)}")
if os.path.exists(db_path):
    print(f"Database file exists at {db_path}")
    # Create a backup of the database
    backup_path = f"{db_path}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
    shutil.copy2(db_path, backup_path)
    print(f"Created backup at {backup_path}")
else:
    print(f"Database file does not exist at {db_path}")
    exit(1)

# Connect to the database
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Beginning schema fix...")
    
    # Step 1: Backup existing user data
    print("Backing up user data...")
    cursor.execute("SELECT * FROM user")
    user_data = cursor.fetchall()
    print(f"Found {len(user_data)} user records")
    
    # Get user column names
    cursor.execute("PRAGMA table_info(user)")
    user_columns = cursor.fetchall()
    user_column_names = [column[1] for column in user_columns]
    print(f"User columns: {user_column_names}")
    
    # Step 2: Backup existing test_result data
    print("Backing up test result data...")
    cursor.execute("SELECT * FROM test_result")
    test_result_data = cursor.fetchall()
    print(f"Found {len(test_result_data)} test result records")
    
    # Get test_result column names
    cursor.execute("PRAGMA table_info(test_result)")
    test_result_columns = cursor.fetchall()
    test_result_column_names = [column[1] for column in test_result_columns]
    print(f"Test result columns: {test_result_column_names}")

    # Step 3: Drop all tables that depend on test_result first
    print("Dropping dependent tables...")
    cursor.execute("PRAGMA foreign_keys = OFF")
    tables_to_check = ["user_answer"]
    for table in tables_to_check:
        try:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if cursor.fetchone():
                print(f"Dropping table {table}")
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
        except Exception as e:
            print(f"Error dropping table {table}: {e}")
    
    # Step 4: Drop the test_result table
    print("Dropping test_result table...")
    cursor.execute("DROP TABLE IF EXISTS test_result")
    
    # Step 5: Create new test_result table without the problematic relationship
    print("Creating new test_result table...")
    cursor.execute("""
    CREATE TABLE test_result (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        test_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        verbal_score INTEGER DEFAULT 0,
        numerical_score INTEGER DEFAULT 0,
        abstract_score INTEGER DEFAULT 0,
        orientation_score INTEGER DEFAULT 0,
        interest_score INTEGER DEFAULT 0,
        personality_score INTEGER DEFAULT 0,
        aptitude_score INTEGER DEFAULT 0,
        eq_score INTEGER DEFAULT 0,
        work_style_score INTEGER DEFAULT 0,
        openness_score INTEGER DEFAULT 0,
        conscientiousness_score INTEGER DEFAULT 0,
        extraversion_score INTEGER DEFAULT 0,
        agreeableness_score INTEGER DEFAULT 0,
        neuroticism_score INTEGER DEFAULT 0,
        leadership_score INTEGER DEFAULT 0,
        teamwork_score INTEGER DEFAULT 0,
        creativity_score INTEGER DEFAULT 0,
        analytical_score INTEGER DEFAULT 0,
        communication_score INTEGER DEFAULT 0, 
        adaptability_score INTEGER DEFAULT 0,
        stem_tech_score INTEGER DEFAULT 0,
        creative_media_score INTEGER DEFAULT 0,
        people_oriented_score INTEGER DEFAULT 0,
        business_management_score INTEGER DEFAULT 0,
        legal_governance_score INTEGER DEFAULT 0,
        logistics_distribution_score INTEGER DEFAULT 0,
        answer_patterns TEXT DEFAULT '{}',
        total_score INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES user (id)
    )
    """)
    
    # Step 6: Restore test_result data
    if test_result_data:
        print("Restoring test result data...")
        for row in test_result_data:
            # Extract values from original data
            id_val = row[0]
            user_id = row[1]
            test_date = row[2]
            
            # Create a dictionary of existing column values
            value_dict = {}
            for i, col_name in enumerate(test_result_column_names):
                if i < len(row):
                    value_dict[col_name] = row[i]
            
            # Build dynamic INSERT statement based on available columns
            columns = ['id', 'user_id', 'test_date']
            values = [id_val, user_id, test_date]
            
            # Add other columns if they exist in the original data
            for col in test_result_column_names:
                if col not in ['id', 'user_id', 'test_date'] and col in value_dict:
                    columns.append(col)
                    values.append(value_dict[col])
            
            # Generate the SQL statement
            placeholders = ', '.join(['?' for _ in columns])
            columns_str = ', '.join(columns)
            
            cursor.execute(f"""
            INSERT INTO test_result ({columns_str}) VALUES ({placeholders})
            """, values)
    
    # Step 7: Recreate UserAnswer table if needed
    print("Recreating UserAnswer table...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_answer (
        id INTEGER PRIMARY KEY,
        test_result_id INTEGER NOT NULL,
        question_id INTEGER NOT NULL,
        selected_option_id INTEGER NOT NULL,
        FOREIGN KEY (test_result_id) REFERENCES test_result (id),
        FOREIGN KEY (question_id) REFERENCES question (id),
        FOREIGN KEY (selected_option_id) REFERENCES question_option (id)
    )
    """)
    
    # Step 8: Enable foreign keys and commit
    cursor.execute("PRAGMA foreign_keys = ON")
    conn.commit()
    conn.close()
    
    print("Database schema fix completed successfully!")
except Exception as e:
    print(f"Error fixing database schema: {e}") 