from neuroapt.app import create_app, db
from neuroapt.app.models import TestResult
from flask import session, redirect, url_for
from flask_login import current_user

def create_direct_interest_test():
    """Create a test that jumps directly to the interest_category section"""
    app = create_app()
    
    with app.test_request_context():
        with app.app_context():
            # Create a user context - we'd need to run this script logged in as a user
            if not current_user or not current_user.is_authenticated:
                print("This script must be run while logged in to the application.")
                return
            
            # Create a new test result
            test_result = TestResult(user_id=current_user.id)
            db.session.add(test_result)
            db.session.commit()
            test_result_id = test_result.id
            
            print(f"Created new test result with ID: {test_result_id}")
            print(f"Please use the URL: http://localhost:5000/test/section/interest_category/0?test_result_id={test_result_id}")
            print("This will take you directly to the first interest_category question.")
            
            # Note: We can't actually redirect here because this is a script
            # You'll need to visit the URL manually

if __name__ == "__main__":
    create_direct_interest_test() 