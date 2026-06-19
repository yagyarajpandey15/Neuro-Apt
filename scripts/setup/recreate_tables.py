from neuroapt.app import create_app, db
from neuroapt.app.models import User, TestResult, Question, QuestionOption, UserAnswer, Career
import os

def recreate_tables():
    """
    Recreate database tables with updated relationships
    """
    app = create_app()
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        
        print("Creating tables with updated relationships...")
        db.create_all()
        
        print("Tables recreated successfully!")
        
        # Print a message about the User-TestResult relationship
        print("\nRelationship details:")
        print("- User.test_results has backref='user_account'")
        print("- TestResult.user_id points to User.id")
        print("- To access the user from a TestResult: test_result.user_account")

if __name__ == "__main__":
    recreate_tables() 