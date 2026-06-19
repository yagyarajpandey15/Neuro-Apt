from neuroapt.app import create_app, db
from neuroapt.app.models import Question, QuestionOption
import sys

def debug_test_routes():
    app = create_app()
    with app.app_context():
        # This mimics the test route's way of fetching questions
        section = 'interest_category'
        
        print(f"Checking for questions with category='{section}'...")
        
        # Check if questions exist for this section using filter_by
        questions = Question.query.filter_by(category=section).all()
        count = len(questions)
        
        print(f"Found {count} questions for section '{section}'")
        
        if count == 0:
            print("\nTrying direct SQL query to confirm:")
            result = db.session.execute("SELECT COUNT(*) FROM question WHERE category = 'interest_category'")
            direct_count = result.scalar()
            print(f"Direct SQL query returned {direct_count} questions")
            
            # Check if questions exist with different casing
            result = db.session.execute("SELECT DISTINCT category FROM question WHERE lower(category) LIKE '%interest%'")
            categories = [row[0] for row in result.fetchall()]
            if categories:
                print(f"\nFound similar categories: {categories}")
        else:
            print("\nFirst 3 questions:")
            for i, q in enumerate(questions[:3]):
                print(f"{i+1}. ID: {q.id}, Content: {q.content}")
                
                # Check options
                options = QuestionOption.query.filter_by(question_id=q.id).all()
                print(f"   Options: {len(options)}")
                for j, opt in enumerate(options[:2]):
                    print(f"   {j+1}. {opt.content} ({opt.trait_impact})")
                
                if i < 2:
                    print()

if __name__ == "__main__":
    debug_test_routes() 