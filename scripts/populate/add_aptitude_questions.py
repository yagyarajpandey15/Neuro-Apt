"""
Script to add aptitude questions to the database.
These questions are designed to assess cognitive abilities and aptitude.
"""

from neuroapt.app import create_app, db
from neuroapt.app.models import Question, QuestionOption
import traceback

def add_aptitude_questions():
    """Add aptitude assessment questions to the database"""
    app = create_app()
    
    with app.app_context():
        # Check if aptitude questions already exist
        existing_count = Question.query.filter_by(category='aptitude').count()
        if existing_count >= 15:
            print(f"Found {existing_count} existing aptitude questions. Skipping.")
            return
        
        # Define questions and options
        questions = [
            {
                "content": "If a shirt costs ₹800 after a 20% discount, what was its original price?",
                "category": "aptitude",
                "options": [
                    {"content": "₹960", "trait_impact": "numerical_reasoning", "trait_value": 2, "is_correct": False},
                    {"content": "₹1000", "trait_impact": "numerical_reasoning", "trait_value": 2, "is_correct": True},
                    {"content": "₹1020", "trait_impact": "numerical_reasoning", "trait_value": 2, "is_correct": False},
                    {"content": "₹1200", "trait_impact": "numerical_reasoning", "trait_value": 2, "is_correct": False}
                ]
            },
            {
                "content": "Complete the sequence: 2, 6, 12, 20, 30, __",
                "category": "aptitude",
                "options": [
                    {"content": "36", "trait_impact": "pattern_recognition", "trait_value": 2, "is_correct": False},
                    {"content": "40", "trait_impact": "pattern_recognition", "trait_value": 2, "is_correct": False},
                    {"content": "42", "trait_impact": "pattern_recognition", "trait_value": 2, "is_correct": True},
                    {"content": "48", "trait_impact": "pattern_recognition", "trait_value": 2, "is_correct": False}
                ]
            },
            {
                "content": "If CAT is coded as 312, how would DOG be coded?",
                "category": "aptitude",
                "options": [
                    {"content": "415", "trait_impact": "logical_reasoning", "trait_value": 2, "is_correct": False},
                    {"content": "417", "trait_impact": "logical_reasoning", "trait_value": 2, "is_correct": True},
                    {"content": "514", "trait_impact": "logical_reasoning", "trait_value": 2, "is_correct": False},
                    {"content": "715", "trait_impact": "logical_reasoning", "trait_value": 2, "is_correct": False}
                ]
            },
            {
                "content": "Which word is the odd one out?",
                "category": "aptitude",
                "options": [
                    {"content": "Rectangle", "trait_impact": "verbal_reasoning", "trait_value": 2, "is_correct": False},
                    {"content": "Circle", "trait_impact": "verbal_reasoning", "trait_value": 2, "is_correct": True},
                    {"content": "Triangle", "trait_impact": "verbal_reasoning", "trait_value": 2, "is_correct": False},
                    {"content": "Square", "trait_impact": "verbal_reasoning", "trait_value": 2, "is_correct": False}
                ]
            },
            {
                "content": "A train traveling at 60 km/h takes 15 minutes to pass through a tunnel. If the length of the train is 0.25 km, how long is the tunnel?",
                "category": "aptitude",
                "options": [
                    {"content": "14.75 km", "trait_impact": "numerical_reasoning", "trait_value": 2, "is_correct": False},
                    {"content": "15 km", "trait_impact": "numerical_reasoning", "trait_value": 2, "is_correct": False},
                    {"content": "15.25 km", "trait_impact": "numerical_reasoning", "trait_value": 2, "is_correct": True},
                    {"content": "15.75 km", "trait_impact": "numerical_reasoning", "trait_value": 2, "is_correct": False}
                ]
            },
            {
                "content": "Find the next term in the series: 1, 4, 9, 16, 25, __",
                "category": "aptitude",
                "options": [
                    {"content": "30", "trait_impact": "pattern_recognition", "trait_value": 2, "is_correct": False},
                    {"content": "36", "trait_impact": "pattern_recognition", "trait_value": 2, "is_correct": True},
                    {"content": "42", "trait_impact": "pattern_recognition", "trait_value": 2, "is_correct": False},
                    {"content": "49", "trait_impact": "pattern_recognition", "trait_value": 2, "is_correct": False}
                ]
            },
            {
                "content": "If a cube has a volume of 27 cubic cm, what is the length of each edge?",
                "category": "aptitude",
                "options": [
                    {"content": "3 cm", "trait_impact": "spatial_reasoning", "trait_value": 2, "is_correct": True},
                    {"content": "6 cm", "trait_impact": "spatial_reasoning", "trait_value": 2, "is_correct": False},
                    {"content": "9 cm", "trait_impact": "spatial_reasoning", "trait_value": 2, "is_correct": False},
                    {"content": "27 cm", "trait_impact": "spatial_reasoning", "trait_value": 2, "is_correct": False}
                ]
            },
            {
                "content": "Happiness is to sadness as love is to ___",
                "category": "aptitude",
                "options": [
                    {"content": "Affection", "trait_impact": "verbal_reasoning", "trait_value": 2, "is_correct": False},
                    {"content": "Emotion", "trait_impact": "verbal_reasoning", "trait_value": 2, "is_correct": False},
                    {"content": "Hate", "trait_impact": "verbal_reasoning", "trait_value": 2, "is_correct": True},
                    {"content": "Like", "trait_impact": "verbal_reasoning", "trait_value": 2, "is_correct": False}
                ]
            },
            {
                "content": "If 5 workers can build a wall in 8 days, how many days would it take 10 workers to build the same wall?",
                "category": "aptitude",
                "options": [
                    {"content": "3 days", "trait_impact": "numerical_reasoning", "trait_value": 2, "is_correct": False},
                    {"content": "4 days", "trait_impact": "numerical_reasoning", "trait_value": 2, "is_correct": True},
                    {"content": "5 days", "trait_impact": "numerical_reasoning", "trait_value": 2, "is_correct": False},
                    {"content": "16 days", "trait_impact": "numerical_reasoning", "trait_value": 2, "is_correct": False}
                ]
            },
            {
                "content": "Which figure completes the pattern?",
                "category": "aptitude",
                "options": [
                    {"content": "A triangle inside a circle", "trait_impact": "spatial_reasoning", "trait_value": 2, "is_correct": False},
                    {"content": "A circle inside a triangle", "trait_impact": "spatial_reasoning", "trait_value": 2, "is_correct": False},
                    {"content": "A square inside a triangle", "trait_impact": "spatial_reasoning", "trait_value": 2, "is_correct": True},
                    {"content": "A triangle inside a square", "trait_impact": "spatial_reasoning", "trait_value": 2, "is_correct": False}
                ]
            },
            {
                "content": "If the word 'CHAIR' is coded as 'DIBJS', how would you code 'TABLE'?",
                "category": "aptitude",
                "options": [
                    {"content": "UBCMF", "trait_impact": "logical_reasoning", "trait_value": 2, "is_correct": True},
                    {"content": "UCCMI", "trait_impact": "logical_reasoning", "trait_value": 2, "is_correct": False},
                    {"content": "UFCMF", "trait_impact": "logical_reasoning", "trait_value": 2, "is_correct": False},
                    {"content": "ELBAT", "trait_impact": "logical_reasoning", "trait_value": 2, "is_correct": False}
                ]
            },
            {
                "content": "What is the minimum number of straight lines needed to make exactly 5 squares of the same size?",
                "category": "aptitude",
                "options": [
                    {"content": "12", "trait_impact": "spatial_reasoning", "trait_value": 2, "is_correct": False},
                    {"content": "14", "trait_impact": "spatial_reasoning", "trait_value": 2, "is_correct": False},
                    {"content": "16", "trait_impact": "spatial_reasoning", "trait_value": 2, "is_correct": True},
                    {"content": "20", "trait_impact": "spatial_reasoning", "trait_value": 2, "is_correct": False}
                ]
            },
            {
                "content": "If you rearrange the letters 'ANGLED', you would get the name of a:",
                "category": "aptitude",
                "options": [
                    {"content": "Country", "trait_impact": "verbal_reasoning", "trait_value": 2, "is_correct": False},
                    {"content": "Animal", "trait_impact": "verbal_reasoning", "trait_value": 2, "is_correct": True},
                    {"content": "Fruit", "trait_impact": "verbal_reasoning", "trait_value": 2, "is_correct": False},
                    {"content": "City", "trait_impact": "verbal_reasoning", "trait_value": 2, "is_correct": False}
                ]
            },
            {
                "content": "A car travels 300 km in 4 hours and then another 200 km in 3 hours. What is the average speed for the entire journey?",
                "category": "aptitude",
                "options": [
                    {"content": "60 km/h", "trait_impact": "numerical_reasoning", "trait_value": 2, "is_correct": False},
                    {"content": "70 km/h", "trait_impact": "numerical_reasoning", "trait_value": 2, "is_correct": False},
                    {"content": "71.4 km/h", "trait_impact": "numerical_reasoning", "trait_value": 2, "is_correct": True},
                    {"content": "75 km/h", "trait_impact": "numerical_reasoning", "trait_value": 2, "is_correct": False}
                ]
            },
            {
                "content": "What comes next in the pattern? 1, 3, 6, 10, 15, __",
                "category": "aptitude",
                "options": [
                    {"content": "18", "trait_impact": "pattern_recognition", "trait_value": 2, "is_correct": False},
                    {"content": "20", "trait_impact": "pattern_recognition", "trait_value": 2, "is_correct": False},
                    {"content": "21", "trait_impact": "pattern_recognition", "trait_value": 2, "is_correct": True},
                    {"content": "24", "trait_impact": "pattern_recognition", "trait_value": 2, "is_correct": False}
                ]
            }
        ]
        
        # Add questions and options to the database
        print("Adding aptitude questions to the database...")
        try:
            for q_data in questions:
                # Create question
                question = Question(
                    content=q_data["content"],
                    category=q_data["category"]
                )
                db.session.add(question)
                db.session.flush()  # Get the question ID
                
                # Create options for this question
                for i, opt_data in enumerate(q_data["options"]):
                    option = QuestionOption(
                        question_id=question.id,
                        content=opt_data["content"],
                        is_correct=opt_data.get("is_correct", False),
                        score_value=opt_data.get("score_value", 1),
                        trait_impact=opt_data["trait_impact"],
                        trait_value=opt_data["trait_value"]
                    )
                    db.session.add(option)
                
            # Commit all changes
            db.session.commit()
            print(f"Successfully added {len(questions)} aptitude questions with options.")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error adding aptitude questions: {str(e)}")
            traceback.print_exc()

if __name__ == "__main__":
    add_aptitude_questions() 