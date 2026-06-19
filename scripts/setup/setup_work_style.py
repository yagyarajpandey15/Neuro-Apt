import os
import sys

# Run the schema update script first
print("Step 1: Updating database schema...")
try:
    from update_schema import update_database_schema
    update_database_schema()
except Exception as e:
    print(f"Error updating schema: {e}")
    sys.exit(1)

# Run the script to add work style questions
print("\nStep 2: Adding work style questions...")
try:
    from add_work_style_questions import add_work_style_questions
    add_work_style_questions()
except Exception as e:
    print(f"Error adding work style questions: {e}")
    sys.exit(1)

print("\nSetup completed successfully!")
print("You can now run the application with the new work style assessment.")
print("Note: Make sure to restart the application for changes to take effect.") 