import os
import sqlite3
import sys

# Path to the database file
db_path = os.path.join(os.getcwd(), 'neuroapt', 'app', 'neuroapt.db')
if not os.path.exists(db_path):
    db_path = os.path.join(os.getcwd(), 'neuroapt.db')
if not os.path.exists(db_path):
    print(f"Database file not found at {db_path}")
    sys.exit(1)

print(f"Using database at: {db_path}")

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check if interest category questions exist
    cursor.execute("SELECT COUNT(*) FROM question WHERE category = 'interest_category'")
    count = cursor.fetchone()[0]
    print(f"Found {count} interest_category questions in database")
    
    if count > 0:
        print("\nSample of interest_category questions:")
        cursor.execute("SELECT id, content FROM question WHERE category = 'interest_category' LIMIT 5")
        for row in cursor.fetchall():
            print(f"ID: {row[0]}, Content: {row[1]}")

        print("\nOptions for the first question:")
        cursor.execute("""
            SELECT qo.id, qo.content, qo.trait_impact 
            FROM question_option qo
            JOIN question q ON q.id = qo.question_id
            WHERE q.category = 'interest_category'
            LIMIT 4
        """)
        for row in cursor.fetchall():
            print(f"Option ID: {row[0]}, Content: {row[1]}, Trait Impact: {row[2]}")
    
except Exception as e:
    print(f"Error: {e}")

finally:
    conn.close() 