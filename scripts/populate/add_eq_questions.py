"""
Script to add Emotional Quotient (EQ) questions to the database.
These questions are designed to assess emotional intelligence and awareness.
"""

from neuroapt.app import create_app, db
from neuroapt.app.models import Question, QuestionOption
import traceback

def add_eq_questions():
    """Add emotional quotient assessment questions to the database"""
    app = create_app()
    
    with app.app_context():
        # Check if EQ questions already exist
        existing_count = Question.query.filter_by(category='eq').count()
        if existing_count >= 15:
            print(f"Found {existing_count} existing EQ questions. Skipping.")
            return
        
        # Define questions and options
        questions = [
            {
                "content": "When someone is talking about their problems, I usually:",
                "category": "eq",
                "options": [
                    {"content": "Think about what I'll say next", "trait_impact": "empathy", "trait_value": 1, "is_correct": False},
                    {"content": "Listen carefully and try to understand their feelings", "trait_impact": "empathy", "trait_value": 4, "is_correct": True},
                    {"content": "Share similar experiences I've had", "trait_impact": "empathy", "trait_value": 2, "is_correct": False},
                    {"content": "Offer solutions immediately", "trait_impact": "empathy", "trait_value": 2, "is_correct": False}
                ]
            },
            {
                "content": "When I feel angry, I typically:",
                "category": "eq",
                "options": [
                    {"content": "Express it immediately without thinking", "trait_impact": "self_regulation", "trait_value": 1, "is_correct": False},
                    {"content": "Bottle it up until I explode later", "trait_impact": "self_regulation", "trait_value": 1, "is_correct": False},
                    {"content": "Recognize the feeling and take time to calm down", "trait_impact": "self_regulation", "trait_value": 4, "is_correct": True},
                    {"content": "Ignore it and pretend everything is fine", "trait_impact": "self_regulation", "trait_value": 2, "is_correct": False}
                ]
            },
            {
                "content": "I can accurately identify how I'm feeling:",
                "category": "eq",
                "options": [
                    {"content": "Almost never - emotions confuse me", "trait_impact": "self_awareness", "trait_value": 1, "is_correct": False},
                    {"content": "Sometimes, but only with basic emotions", "trait_impact": "self_awareness", "trait_value": 2, "is_correct": False},
                    {"content": "Often, I can name most of my feelings", "trait_impact": "self_awareness", "trait_value": 3, "is_correct": False},
                    {"content": "Most of the time, including complex emotions", "trait_impact": "self_awareness", "trait_value": 4, "is_correct": True}
                ]
            },
            {
                "content": "When I see someone crying, I usually feel:",
                "category": "eq",
                "options": [
                    {"content": "Uncomfortable and try to leave", "trait_impact": "empathy", "trait_value": 1, "is_correct": False},
                    {"content": "A strong urge to make them feel better", "trait_impact": "empathy", "trait_value": 3, "is_correct": False},
                    {"content": "Curious about what happened", "trait_impact": "empathy", "trait_value": 2, "is_correct": False},
                    {"content": "Connected to their emotional state", "trait_impact": "empathy", "trait_value": 4, "is_correct": True}
                ]
            },
            {
                "content": "When facing a difficult challenge, I usually:",
                "category": "eq",
                "options": [
                    {"content": "Give up quickly if I encounter obstacles", "trait_impact": "motivation", "trait_value": 1, "is_correct": False},
                    {"content": "Keep pushing forward no matter what", "trait_impact": "motivation", "trait_value": 3, "is_correct": False},
                    {"content": "Find ways to stay positive and adapt my approach", "trait_impact": "motivation", "trait_value": 4, "is_correct": True},
                    {"content": "Ask someone else to help me complete it", "trait_impact": "motivation", "trait_value": 2, "is_correct": False}
                ]
            },
            {
                "content": "During a disagreement with friends, I typically:",
                "category": "eq",
                "options": [
                    {"content": "Try to understand their perspective", "trait_impact": "social_skills", "trait_value": 4, "is_correct": True},
                    {"content": "Insist on my point until they agree", "trait_impact": "social_skills", "trait_value": 1, "is_correct": False},
                    {"content": "Change the subject to avoid conflict", "trait_impact": "social_skills", "trait_value": 2, "is_correct": False},
                    {"content": "Get defensive about my position", "trait_impact": "social_skills", "trait_value": 1, "is_correct": False}
                ]
            },
            {
                "content": "When someone gives me criticism, I usually:",
                "category": "eq",
                "options": [
                    {"content": "Take it personally and feel hurt", "trait_impact": "self_awareness", "trait_value": 1, "is_correct": False},
                    {"content": "Become defensive immediately", "trait_impact": "self_awareness", "trait_value": 1, "is_correct": False},
                    {"content": "Listen and evaluate if it's valid", "trait_impact": "self_awareness", "trait_value": 4, "is_correct": True},
                    {"content": "Ignore it completely", "trait_impact": "self_awareness", "trait_value": 2, "is_correct": False}
                ]
            },
            {
                "content": "I can tell when someone is upset even if they don't say anything:",
                "category": "eq",
                "options": [
                    {"content": "Rarely - I miss these cues", "trait_impact": "social_awareness", "trait_value": 1, "is_correct": False},
                    {"content": "Sometimes, but only with close friends", "trait_impact": "social_awareness", "trait_value": 2, "is_correct": False},
                    {"content": "Often, I notice subtle changes in behavior", "trait_impact": "social_awareness", "trait_value": 4, "is_correct": True},
                    {"content": "Only if they show obvious signs", "trait_impact": "social_awareness", "trait_value": 2, "is_correct": False}
                ]
            },
            {
                "content": "When I'm stressed about an upcoming deadline, I tend to:",
                "category": "eq",
                "options": [
                    {"content": "Panic and feel overwhelmed", "trait_impact": "stress_management", "trait_value": 1, "is_correct": False},
                    {"content": "Break tasks into manageable steps and prioritize", "trait_impact": "stress_management", "trait_value": 4, "is_correct": True},
                    {"content": "Procrastinate until the last minute", "trait_impact": "stress_management", "trait_value": 1, "is_correct": False},
                    {"content": "Work non-stop without breaks", "trait_impact": "stress_management", "trait_value": 2, "is_correct": False}
                ]
            },
            {
                "content": "After having a strong emotional reaction, I usually:",
                "category": "eq",
                "options": [
                    {"content": "Reflect on why I reacted that way", "trait_impact": "self_reflection", "trait_value": 4, "is_correct": True},
                    {"content": "Try to forget about it quickly", "trait_impact": "self_reflection", "trait_value": 1, "is_correct": False},
                    {"content": "Blame external factors for my reaction", "trait_impact": "self_reflection", "trait_value": 1, "is_correct": False},
                    {"content": "Feel embarrassed about losing control", "trait_impact": "self_reflection", "trait_value": 2, "is_correct": False}
                ]
            },
            {
                "content": "When working in a team, I am most focused on:",
                "category": "eq",
                "options": [
                    {"content": "Making sure everyone feels included and valued", "trait_impact": "relationship_management", "trait_value": 4, "is_correct": True},
                    {"content": "Getting the work done efficiently", "trait_impact": "relationship_management", "trait_value": 2, "is_correct": False},
                    {"content": "Having my ideas recognized", "trait_impact": "relationship_management", "trait_value": 1, "is_correct": False},
                    {"content": "Avoiding any potential conflicts", "trait_impact": "relationship_management", "trait_value": 2, "is_correct": False}
                ]
            },
            {
                "content": "When someone is speaking with strong emotion, I usually:",
                "category": "eq",
                "options": [
                    {"content": "Match their emotional intensity", "trait_impact": "emotional_awareness", "trait_value": 2, "is_correct": False},
                    {"content": "Look for logical flaws in their argument", "trait_impact": "emotional_awareness", "trait_value": 1, "is_correct": False},
                    {"content": "Try to understand the feelings behind their words", "trait_impact": "emotional_awareness", "trait_value": 4, "is_correct": True},
                    {"content": "Wait for them to calm down before engaging", "trait_impact": "emotional_awareness", "trait_value": 2, "is_correct": False}
                ]
            },
            {
                "content": "My friends would describe me as someone who:",
                "category": "eq",
                "options": [
                    {"content": "Is always cheerful and positive", "trait_impact": "emotional_balance", "trait_value": 3, "is_correct": False},
                    {"content": "Understands their feelings", "trait_impact": "emotional_balance", "trait_value": 4, "is_correct": True},
                    {"content": "Gives practical advice", "trait_impact": "emotional_balance", "trait_value": 2, "is_correct": False},
                    {"content": "Keeps emotions private", "trait_impact": "emotional_balance", "trait_value": 1, "is_correct": False}
                ]
            },
            {
                "content": "When I experience failure, I usually:",
                "category": "eq",
                "options": [
                    {"content": "See it as a learning opportunity", "trait_impact": "resilience", "trait_value": 4, "is_correct": True},
                    {"content": "Take it as proof of my inadequacy", "trait_impact": "resilience", "trait_value": 1, "is_correct": False},
                    {"content": "Blame external circumstances", "trait_impact": "resilience", "trait_value": 1, "is_correct": False},
                    {"content": "Try to forget about it quickly", "trait_impact": "resilience", "trait_value": 2, "is_correct": False}
                ]
            },
            {
                "content": "When making important decisions, I:",
                "category": "eq",
                "options": [
                    {"content": "Rely purely on logic and facts", "trait_impact": "decision_making", "trait_value": 2, "is_correct": False},
                    {"content": "Go with my gut feeling", "trait_impact": "decision_making", "trait_value": 2, "is_correct": False},
                    {"content": "Consider both my emotions and rational analysis", "trait_impact": "decision_making", "trait_value": 4, "is_correct": True},
                    {"content": "Ask others what they would do", "trait_impact": "decision_making", "trait_value": 2, "is_correct": False}
                ]
            }
        ]
        
        # Add questions and options to the database
        print("Adding emotional quotient questions to the database...")
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
                        score_value=opt_data.get("score_value", opt_data["trait_value"]),
                        trait_impact=opt_data["trait_impact"],
                        trait_value=opt_data["trait_value"]
                    )
                    db.session.add(option)
                
            # Commit all changes
            db.session.commit()
            print(f"Successfully added {len(questions)} emotional quotient questions with options.")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error adding emotional quotient questions: {str(e)}")
            traceback.print_exc()

if __name__ == "__main__":
    add_eq_questions() 