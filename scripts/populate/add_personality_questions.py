"""
Script to add personality questions to the database.
These questions are designed to assess various personality traits.
"""

from neuroapt.app import create_app, db
from neuroapt.app.models import Question, QuestionOption
import traceback

def add_personality_questions():
    """Add personality assessment questions to the database"""
    app = create_app()
    
    with app.app_context():
        # Check if personality questions already exist
        existing_count = Question.query.filter_by(category='personality').count()
        if existing_count >= 15:
            print(f"Found {existing_count} existing personality questions. Skipping.")
            return
        
        # Define questions and options
        questions = [
            {
                "content": "At parties and social gatherings, you usually...",
                "category": "personality",
                "options": [
                    {"content": "Talk to as many people as possible", "trait_impact": "extraversion", "trait_value": 2},
                    {"content": "Have a few deep conversations", "trait_impact": "introversion", "trait_value": 2},
                    {"content": "Enjoy observing others and the atmosphere", "trait_impact": "observant", "trait_value": 2},
                    {"content": "Feel comfortable only with close friends", "trait_impact": "reserved", "trait_value": 2}
                ]
            },
            {
                "content": "When making decisions, you tend to rely more on...",
                "category": "personality",
                "options": [
                    {"content": "Logic, facts, and objective analysis", "trait_impact": "thinking", "trait_value": 2},
                    {"content": "Personal values and how it affects others", "trait_impact": "feeling", "trait_value": 2},
                    {"content": "What has worked in the past", "trait_impact": "sensing", "trait_value": 2},
                    {"content": "Your intuition about what feels right", "trait_impact": "intuition", "trait_value": 2}
                ]
            },
            {
                "content": "How do you typically handle stress?",
                "category": "personality",
                "options": [
                    {"content": "Make a plan and tackle problems systematically", "trait_impact": "conscientiousness", "trait_value": 2},
                    {"content": "Talk it out with friends or family", "trait_impact": "agreeableness", "trait_value": 2},
                    {"content": "Try new approaches or creative solutions", "trait_impact": "openness", "trait_value": 2},
                    {"content": "Feel overwhelmed and worry about outcomes", "trait_impact": "neuroticism", "trait_value": 2}
                ]
            },
            {
                "content": "How do you approach deadlines and tasks?",
                "category": "personality",
                "options": [
                    {"content": "Start early and finish ahead of schedule", "trait_impact": "conscientiousness", "trait_value": 2},
                    {"content": "Work steadily with regular breaks", "trait_impact": "balanced", "trait_value": 2},
                    {"content": "Wait until inspiration strikes", "trait_impact": "intuition", "trait_value": 2},
                    {"content": "Work best under last-minute pressure", "trait_impact": "perceiving", "trait_value": 2}
                ]
            },
            {
                "content": "When someone disagrees with you, your typical reaction is to...",
                "category": "personality",
                "options": [
                    {"content": "Listen and try to understand their perspective", "trait_impact": "agreeableness", "trait_value": 2},
                    {"content": "Defend your position with facts and logic", "trait_impact": "thinking", "trait_value": 2},
                    {"content": "Consider if there might be middle ground", "trait_impact": "diplomacy", "trait_value": 2},
                    {"content": "Feel personally attacked or upset", "trait_impact": "neuroticism", "trait_value": 2}
                ]
            },
            {
                "content": "Your idea of a perfect weekend would include...",
                "category": "personality",
                "options": [
                    {"content": "Socializing with many friends or at events", "trait_impact": "extraversion", "trait_value": 2},
                    {"content": "Quiet time alone with books, movies, or hobbies", "trait_impact": "introversion", "trait_value": 2},
                    {"content": "A mix of planned activities and free time", "trait_impact": "balanced", "trait_value": 2},
                    {"content": "Spontaneous adventures and new experiences", "trait_impact": "openness", "trait_value": 2}
                ]
            },
            {
                "content": "How organized is your personal space?",
                "category": "personality",
                "options": [
                    {"content": "Very organized, with everything in its proper place", "trait_impact": "conscientiousness", "trait_value": 2},
                    {"content": "Reasonably tidy with some organization", "trait_impact": "balanced", "trait_value": 2},
                    {"content": "Cluttered but I know where things are", "trait_impact": "perceiving", "trait_value": 2},
                    {"content": "Chaotic, but it works for me", "trait_impact": "openness", "trait_value": 2}
                ]
            },
            {
                "content": "When working in a group, you prefer to...",
                "category": "personality",
                "options": [
                    {"content": "Take charge and direct the group", "trait_impact": "assertiveness", "trait_value": 2},
                    {"content": "Contribute ideas but let others lead", "trait_impact": "balanced", "trait_value": 2},
                    {"content": "Support the group and maintain harmony", "trait_impact": "agreeableness", "trait_value": 2},
                    {"content": "Work independently on your assigned part", "trait_impact": "introversion", "trait_value": 2}
                ]
            },
            {
                "content": "How do you typically approach new challenges?",
                "category": "personality",
                "options": [
                    {"content": "With enthusiasm and excitement", "trait_impact": "openness", "trait_value": 2},
                    {"content": "With careful planning and preparation", "trait_impact": "conscientiousness", "trait_value": 2},
                    {"content": "By seeking advice from others", "trait_impact": "agreeableness", "trait_value": 2},
                    {"content": "With caution and concern about potential problems", "trait_impact": "neuroticism", "trait_value": 2}
                ]
            },
            {
                "content": "When telling a story, you tend to...",
                "category": "personality",
                "options": [
                    {"content": "Focus on facts and specific details", "trait_impact": "sensing", "trait_value": 2},
                    {"content": "Describe the feelings and atmosphere", "trait_impact": "feeling", "trait_value": 2},
                    {"content": "Get to the point quickly and efficiently", "trait_impact": "thinking", "trait_value": 2},
                    {"content": "Use colorful descriptions and analogies", "trait_impact": "intuition", "trait_value": 2}
                ]
            },
            {
                "content": "How do you feel about change?",
                "category": "personality",
                "options": [
                    {"content": "Love it and actively seek out new experiences", "trait_impact": "openness", "trait_value": 2},
                    {"content": "Accept it when necessary but prefer stability", "trait_impact": "balanced", "trait_value": 2},
                    {"content": "Need time to adjust and prepare", "trait_impact": "conscientiousness", "trait_value": 2},
                    {"content": "Find it stressful and prefer routines", "trait_impact": "neuroticism", "trait_value": 2}
                ]
            },
            {
                "content": "How do you typically make friends?",
                "category": "personality",
                "options": [
                    {"content": "Easily connect with many people quickly", "trait_impact": "extraversion", "trait_value": 2},
                    {"content": "Develop a few deep, meaningful relationships", "trait_impact": "introversion", "trait_value": 2},
                    {"content": "Let others initiate and then respond warmly", "trait_impact": "agreeableness", "trait_value": 2},
                    {"content": "Bond with people through shared interests", "trait_impact": "openness", "trait_value": 2}
                ]
            },
            {
                "content": "When you receive criticism, you typically...",
                "category": "personality",
                "options": [
                    {"content": "Analyze it objectively and learn from it", "trait_impact": "thinking", "trait_value": 2},
                    {"content": "Feel hurt initially but try to improve", "trait_impact": "feeling", "trait_value": 2},
                    {"content": "Defend yourself and point out inaccuracies", "trait_impact": "assertiveness", "trait_value": 2},
                    {"content": "Worry about it for a long time afterward", "trait_impact": "neuroticism", "trait_value": 2}
                ]
            },
            {
                "content": "In a group discussion, you are most likely to...",
                "category": "personality",
                "options": [
                    {"content": "Speak up confidently with your opinions", "trait_impact": "extraversion", "trait_value": 2},
                    {"content": "Listen carefully and speak when you have something valuable to add", "trait_impact": "introversion", "trait_value": 2},
                    {"content": "Ensure everyone gets a chance to speak", "trait_impact": "agreeableness", "trait_value": 2},
                    {"content": "Challenge ideas to improve the final outcome", "trait_impact": "thinking", "trait_value": 2}
                ]
            },
            {
                "content": "How do you approach rules and procedures?",
                "category": "personality",
                "options": [
                    {"content": "Follow them carefully and expect others to do the same", "trait_impact": "conscientiousness", "trait_value": 2},
                    {"content": "Follow the important ones but are flexible about minor rules", "trait_impact": "balanced", "trait_value": 2},
                    {"content": "Question them and follow only those that make sense to you", "trait_impact": "openness", "trait_value": 2},
                    {"content": "See them as general guidelines that can be adapted", "trait_impact": "perceiving", "trait_value": 2}
                ]
            }
        ]
        
        # Add questions and options to the database
        print("Adding personality questions to the database...")
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
                        score_value=1,
                        trait_impact=opt_data["trait_impact"],
                        trait_value=opt_data["trait_value"]
                    )
                    db.session.add(option)
                
            # Commit all changes
            db.session.commit()
            print(f"Successfully added {len(questions)} personality questions with options.")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error adding personality questions: {str(e)}")
            traceback.print_exc()

if __name__ == "__main__":
    add_personality_questions() 