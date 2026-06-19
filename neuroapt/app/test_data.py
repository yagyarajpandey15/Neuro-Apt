"""
This file contains sample test questions for the psychometric assessment.
Used to populate the database with initial test questions.
"""

import json
from neuroapt.app import db
from neuroapt.app.models import Question, QuestionOption

# Sample test questions by category
SAMPLE_QUESTIONS = {
    # Orientation Assessment Questions
    "orientation": [
        {
            "content": "How do you typically prefer to learn new information?",
            "options": [
                {"content": "Reading books and articles", "score_value": 5, "trait_impact": "analytical"},
                {"content": "Watching videos or demonstrations", "score_value": 5, "trait_impact": "visual"},
                {"content": "Hands-on practice and experimentation", "score_value": 5, "trait_impact": "practical"},
                {"content": "Discussion and verbal explanation", "score_value": 5, "trait_impact": "social"}
            ]
        },
        {
            "content": "When tackling a complex problem, what is your usual first step?",
            "options": [
                {"content": "Break it down into smaller components", "score_value": 5, "trait_impact": "analytical"},
                {"content": "Look for similar problems I've solved before", "score_value": 5, "trait_impact": "experiential"},
                {"content": "Brainstorm multiple possible solutions", "score_value": 5, "trait_impact": "creative"},
                {"content": "Research what others have done in similar situations", "score_value": 5, "trait_impact": "methodical"}
            ]
        },
        {
            "content": "How do you prefer your workspace to be organized?",
            "options": [
                {"content": "Meticulously organized with everything in its place", "score_value": 5, "trait_impact": "conscientiousness"},
                {"content": "Generally tidy but with some creative chaos", "score_value": 4, "trait_impact": "balanced"},
                {"content": "Minimal organization, focusing on what I'm currently working on", "score_value": 3, "trait_impact": "present-focused"},
                {"content": "Flexible arrangement that changes based on what I'm doing", "score_value": 3, "trait_impact": "adaptability"}
            ]
        }
    ],
    
    # Interest Assessment Questions
    "interest": [
        {
            "content": "Which of these activities would you most enjoy doing on a regular basis?",
            "options": [
                {"content": "Analyzing data and finding patterns", "score_value": 5, "trait_impact": "stem_tech"},
                {"content": "Creating visual designs or artwork", "score_value": 5, "trait_impact": "creative_media"},
                {"content": "Leading a team or organizing group activities", "score_value": 5, "trait_impact": "people_oriented"},
                {"content": "Planning financial strategies or business models", "score_value": 5, "trait_impact": "business_management"}
            ]
        },
        {
            "content": "Which subject would you be most interested in studying further?",
            "options": [
                {"content": "Computer Science or Engineering", "score_value": 5, "trait_impact": "stem_tech"},
                {"content": "Arts, Design, or Literature", "score_value": 5, "trait_impact": "creative_media"},
                {"content": "Psychology or Education", "score_value": 5, "trait_impact": "people_oriented"},
                {"content": "Business, Economics, or Law", "score_value": 5, "trait_impact": "business_management"}
            ]
        },
        {
            "content": "What type of project would most energize you?",
            "options": [
                {"content": "Building or fixing something technical", "score_value": 5, "trait_impact": "stem_tech"},
                {"content": "Creating something artistic or expressive", "score_value": 5, "trait_impact": "creative_media"},
                {"content": "Helping others develop or solve personal problems", "score_value": 5, "trait_impact": "people_oriented"},
                {"content": "Organizing resources or managing operations", "score_value": 5, "trait_impact": "logistics_distribution"}
            ]
        }
    ],
    
    # Personality Assessment Questions
    "personality": [
        {
            "content": "How do you typically react to unexpected changes to plans?",
            "options": [
                {"content": "I embrace change and quickly adapt", "score_value": 5, "trait_impact": "adaptability"},
                {"content": "I carefully evaluate the new situation before proceeding", "score_value": 4, "trait_impact": "analytical"},
                {"content": "I prefer to stick with the original plan when possible", "score_value": 3, "trait_impact": "conscientiousness"},
                {"content": "I find changes stressful but manage to adjust", "score_value": 2, "trait_impact": "neuroticism"}
            ]
        },
        {
            "content": "In social situations, you tend to be:",
            "options": [
                {"content": "The center of attention, energized by interaction", "score_value": 5, "trait_impact": "extraversion"},
                {"content": "Selective about interactions, enjoying meaningful conversations", "score_value": 4, "trait_impact": "balanced"},
                {"content": "Observant, preferring to listen more than speak", "score_value": 3, "trait_impact": "introversion"},
                {"content": "Reserved, feeling drained by too much social interaction", "score_value": 2, "trait_impact": "introversion"}
            ]
        },
        {
            "content": "When making decisions, what factors do you prioritize?",
            "options": [
                {"content": "Logical analysis and objective reasoning", "score_value": 5, "trait_impact": "analytical"},
                {"content": "Values and how it affects people involved", "score_value": 5, "trait_impact": "agreeableness"},
                {"content": "Practical outcomes and efficiency", "score_value": 4, "trait_impact": "conscientiousness"},
                {"content": "Creative possibilities and future potential", "score_value": 4, "trait_impact": "openness"}
            ]
        }
    ],
    
    # Aptitude Assessment Questions
    "aptitude": [
        {
            "content": "If a shirt costs $24 after a 25% discount, what was the original price?",
            "options": [
                {"content": "$30", "score_value": 5, "trait_impact": "numerical", "is_correct": False},
                {"content": "$32", "score_value": 10, "trait_impact": "numerical", "is_correct": True},
                {"content": "$28", "score_value": 0, "trait_impact": "numerical", "is_correct": False},
                {"content": "$36", "score_value": 0, "trait_impact": "numerical", "is_correct": False}
            ]
        },
        {
            "content": "Which word is most similar in meaning to 'Frugal'?",
            "options": [
                {"content": "Wasteful", "score_value": 0, "trait_impact": "verbal", "is_correct": False},
                {"content": "Generous", "score_value": 0, "trait_impact": "verbal", "is_correct": False},
                {"content": "Economical", "score_value": 10, "trait_impact": "verbal", "is_correct": True},
                {"content": "Demanding", "score_value": 0, "trait_impact": "verbal", "is_correct": False}
            ]
        },
        {
            "content": "What comes next in the sequence: 2, 6, 12, 20, ?",
            "options": [
                {"content": "30", "score_value": 10, "trait_impact": "abstract", "is_correct": True},
                {"content": "28", "score_value": 0, "trait_impact": "abstract", "is_correct": False},
                {"content": "32", "score_value": 0, "trait_impact": "abstract", "is_correct": False},
                {"content": "42", "score_value": 0, "trait_impact": "abstract", "is_correct": False}
            ]
        }
    ],
    
    # Emotional Intelligence Questions
    "eq": [
        {
            "content": "When someone on your team is visibly upset, what is your typical response?",
            "options": [
                {"content": "Give them space to process their emotions alone", "score_value": 3, "trait_impact": "eq_awareness"},
                {"content": "Ask if they want to talk about what's bothering them", "score_value": 5, "trait_impact": "eq_management"},
                {"content": "Try to cheer them up right away", "score_value": 3, "trait_impact": "eq_social"},
                {"content": "Acknowledge their feelings and offer practical help", "score_value": 4, "trait_impact": "eq_empathy"}
            ]
        },
        {
            "content": "When you make a significant mistake at work, how do you typically react?",
            "options": [
                {"content": "Take immediate responsibility and work on a solution", "score_value": 5, "trait_impact": "eq_management"},
                {"content": "Feel embarrassed but try to hide it from others", "score_value": 2, "trait_impact": "eq_awareness"},
                {"content": "Get frustrated with myself but use it as a learning opportunity", "score_value": 4, "trait_impact": "eq_awareness"},
                {"content": "Worry about how others will perceive me after the mistake", "score_value": 2, "trait_impact": "eq_social"}
            ]
        },
        {
            "content": "How do you handle situations where you disagree with a colleague's approach?",
            "options": [
                {"content": "Directly confront them about why they're wrong", "score_value": 1, "trait_impact": "eq_social"},
                {"content": "Respectfully explain my perspective and listen to theirs", "score_value": 5, "trait_impact": "eq_empathy"},
                {"content": "Avoid the conflict and work around them", "score_value": 2, "trait_impact": "eq_management"},
                {"content": "Try to find common ground and a compromise", "score_value": 4, "trait_impact": "eq_social"}
            ]
        }
    ],
    
    # Work Style Assessment Questions
    "work_style": [
        {
            "content": "When working on a team project, which role do you typically find yourself in?",
            "options": [
                {"content": "The leader who organizes and directs the team", "score_value": 5, "trait_impact": "leadership"},
                {"content": "The creative who generates new ideas", "score_value": 5, "trait_impact": "creativity"},
                {"content": "The analyzer who evaluates options critically", "score_value": 5, "trait_impact": "analytical"},
                {"content": "The mediator who ensures everyone works well together", "score_value": 5, "trait_impact": "teamwork"}
            ]
        },
        {
            "content": "How do you prefer to approach deadlines?",
            "options": [
                {"content": "Work steadily and finish well ahead of time", "score_value": 5, "trait_impact": "conscientiousness"},
                {"content": "Create a detailed schedule and stick to it", "score_value": 5, "trait_impact": "organized"},
                {"content": "Focus intensely as the deadline approaches", "score_value": 3, "trait_impact": "pressure"},
                {"content": "Remain flexible and adapt based on changing priorities", "score_value": 4, "trait_impact": "adaptability"}
            ]
        },
        {
            "content": "What environment helps you work most effectively?",
            "options": [
                {"content": "A quiet, private space with minimal distractions", "score_value": 4, "trait_impact": "focused"},
                {"content": "A collaborative space where I can interact with others", "score_value": 4, "trait_impact": "teamwork"},
                {"content": "A flexible environment that can change based on the task", "score_value": 5, "trait_impact": "adaptability"},
                {"content": "A structured environment with clear expectations", "score_value": 4, "trait_impact": "organized"}
            ]
        }
    ],
    
    # Interest Category Assessment Questions
    "interest_category": [
        {
            "content": "Which career field interests you the most?",
            "options": [
                {"content": "Technology, Engineering or Science", "score_value": 5, "trait_impact": "stem_tech"},
                {"content": "Arts, Media or Design", "score_value": 5, "trait_impact": "creative_media"},
                {"content": "Healthcare, Education or Social Services", "score_value": 5, "trait_impact": "people_oriented"},
                {"content": "Business, Finance or Law", "score_value": 5, "trait_impact": "business_management"}
            ]
        },
        {
            "content": "What type of problems do you enjoy solving?",
            "options": [
                {"content": "Technical or scientific challenges", "score_value": 5, "trait_impact": "stem_tech"},
                {"content": "Creative or artistic challenges", "score_value": 5, "trait_impact": "creative_media"},
                {"content": "Interpersonal or social challenges", "score_value": 5, "trait_impact": "people_oriented"},
                {"content": "Strategic or organizational challenges", "score_value": 5, "trait_impact": "business_management"}
            ]
        },
        {
            "content": "Which of these values is most important to you in a career?",
            "options": [
                {"content": "Innovation and technological advancement", "score_value": 5, "trait_impact": "stem_tech"},
                {"content": "Creative expression and originality", "score_value": 5, "trait_impact": "creative_media"},
                {"content": "Helping others and making a social impact", "score_value": 5, "trait_impact": "people_oriented"},
                {"content": "Structure, stability and clear procedures", "score_value": 5, "trait_impact": "legal_governance"}
            ]
        }
    ]
}

def populate_sample_questions():
    """Add sample questions to the database for each category"""
    
    questions_added = 0
    options_added = 0
    
    for category, questions in SAMPLE_QUESTIONS.items():
        for question_data in questions:
            # Check if question already exists
            existing_question = Question.query.filter_by(content=question_data["content"]).first()
            
            if not existing_question:
                # Create new question
                question = Question(
                    category=category,
                    content=question_data["content"]
                )
                db.session.add(question)
                db.session.commit()  # Commit to get the question ID
                questions_added += 1
                
                # Add options
                for option_data in question_data["options"]:
                    option = QuestionOption(
                        question_id=question.id,
                        content=option_data["content"],
                        score_value=option_data["score_value"],
                        trait_impact=option_data["trait_impact"],
                        is_correct=option_data.get("is_correct", False)
                    )
                    db.session.add(option)
                    options_added += 1
            
    db.session.commit()
    return questions_added, options_added

if __name__ == "__main__":
    # This allows running this file directly to populate the database
    from neuroapt.app import create_app
    app = create_app()
    with app.app_context():
        questions, options = populate_sample_questions()
        print(f"Added {questions} questions and {options} options to the database.") 