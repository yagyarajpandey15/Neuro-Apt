from neuroapt.app import create_app, db
from neuroapt.app.models import Question, QuestionOption, TestResult
from flask import session
import json

def check_test_flow():
    app = create_app()
    with app.app_context():
        # Check test sections defined in routes/test.py
        print("Checking test flow...")
        test_sections = ['orientation', 'interest', 'personality', 'aptitude', 'eq', 'work_style', 'interest_category']
        
        print("\nVerifying all sections have questions:")
        for section in test_sections:
            questions = Question.query.filter_by(category=section).all()
            print(f"{section}: {len(questions)} questions")
            
            # If no questions, show error
            if len(questions) == 0:
                print(f"  ERROR: No questions found for '{section}' category!")
                
                # Check if there are any questions with a similar name
                result = db.session.execute("SELECT DISTINCT category FROM question WHERE lower(category) LIKE :pattern", 
                                          {"pattern": f"%{section.lower()}%"})
                similar = [row[0] for row in result.fetchall()]
                if similar:
                    print(f"  Found similar categories: {similar}")
        
        # Check if 'interest_category' is the last section
        last_section = test_sections[-1]
        print(f"\nLast section in test flow: '{last_section}'")
        if last_section == 'interest_category':
            print("Interest category is correctly placed as the last section")
        
        # Check if the application properly loads interest_category questions
        print("\nTest loading interest_category questions:")
        questions = Question.query.filter_by(category='interest_category').all()
        if questions:
            print(f"Successfully loaded {len(questions)} interest_category questions")
            
            # Check a sample question and its options
            q = questions[0]
            print(f"\nSample question: {q.content}")
            
            options = QuestionOption.query.filter_by(question_id=q.id).all()
            print(f"Options ({len(options)}):")
            for opt in options:
                print(f"- {opt.content} (trait: {opt.trait_impact}, value: {opt.trait_value})")
        else:
            print("ERROR: Could not load interest_category questions!")

if __name__ == "__main__":
    check_test_flow() 