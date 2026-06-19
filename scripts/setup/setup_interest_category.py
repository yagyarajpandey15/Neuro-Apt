import os
import sys

# Run the schema update script first
print("Step 1: Updating database schema for interest categories...")
try:
    from update_schema_interest import update_database_schema
    update_database_schema()
except Exception as e:
    print(f"Error updating schema: {e}")
    sys.exit(1)

# Run the script to add interest category questions
print("\nStep 2: Adding interest category questions...")
try:
    from add_interest_questions import add_interest_questions
    add_interest_questions()
except Exception as e:
    print(f"Error adding interest category questions: {e}")
    sys.exit(1)

print("\nSetup completed successfully!")
print("You can now run the application with the new interest category assessment.")
print("Note: Make sure to restart the application for changes to take effect.") 