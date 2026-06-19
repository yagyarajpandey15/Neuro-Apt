"""
Script to add interest questions to the database.
These questions are designed to assess user interests in different fields.
"""

from neuroapt.app import create_app, db
from neuroapt.app.models import Question, QuestionOption
import traceback

def add_interest_questions():
    """Add interest assessment questions to the database"""
    app = create_app()
    
    with app.app_context():
        # Check if interest questions already exist
        existing_count = Question.query.filter_by(category='interest').count()
        if existing_count >= 15:
            print(f"Found {existing_count} existing interest questions. Skipping.")
            return
        
        # Define questions and options
        questions = [
            {
                "content": "During your free time, you most enjoy...",
                "category": "interest",
                "options": [
                    {"content": "Working with technology or solving technical problems", "trait_impact": "stem_tech", "trait_value": 2},
                    {"content": "Creating art, music, or exploring new designs", "trait_impact": "creative_media", "trait_value": 2},
                    {"content": "Helping others or engaging in community activities", "trait_impact": "people_oriented", "trait_value": 2},
                    {"content": "Organizing events or planning projects", "trait_impact": "business_management", "trait_value": 2}
                ]
            },
            {
                "content": "What type of YouTube videos do you find yourself watching most often?",
                "category": "interest",
                "options": [
                    {"content": "Educational content about science, engineering or math", "trait_impact": "stem_tech", "trait_value": 2},
                    {"content": "Creative tutorials, music performances, or design showcases", "trait_impact": "creative_media", "trait_value": 2},
                    {"content": "Social experiments, psychology insights, or relationship advice", "trait_impact": "people_oriented", "trait_value": 2},
                    {"content": "Business strategies, entrepreneurship, or leadership content", "trait_impact": "business_management", "trait_value": 2}
                ]
            },
            {
                "content": "If you had to choose one of these school projects, which would you prefer?",
                "category": "interest",
                "options": [
                    {"content": "Building a robot or coding a new application", "trait_impact": "stem_tech", "trait_value": 2},
                    {"content": "Creating a short film or designing a magazine", "trait_impact": "creative_media", "trait_value": 2},
                    {"content": "Organizing a community event or peer counseling program", "trait_impact": "people_oriented", "trait_value": 2},
                    {"content": "Starting a mini-business or developing a marketing campaign", "trait_impact": "business_management", "trait_value": 2}
                ]
            },
            {
                "content": "Your friends would most likely come to you for help with...",
                "category": "interest",
                "options": [
                    {"content": "Fixing their technology or explaining how something works", "trait_impact": "stem_tech", "trait_value": 2},
                    {"content": "Creative ideas or making something look better", "trait_impact": "creative_media", "trait_value": 2},
                    {"content": "Personal problems or understanding others' perspectives", "trait_impact": "people_oriented", "trait_value": 2},
                    {"content": "Organizing an event or managing a group project", "trait_impact": "business_management", "trait_value": 2}
                ]
            },
            {
                "content": "Which of these magazines would you be most interested in reading?",
                "category": "interest",
                "options": [
                    {"content": "Popular Science or Wired", "trait_impact": "stem_tech", "trait_value": 2},
                    {"content": "Creative Arts Magazine or Design Weekly", "trait_impact": "creative_media", "trait_value": 2},
                    {"content": "Psychology Today or Social Impact", "trait_impact": "people_oriented", "trait_value": 2},
                    {"content": "Forbes or Entrepreneur", "trait_impact": "business_management", "trait_value": 2}
                ]
            },
            {
                "content": "In a group project, you naturally take on the role of...",
                "category": "interest",
                "options": [
                    {"content": "The technical expert who solves the complex problems", "trait_impact": "stem_tech", "trait_value": 2},
                    {"content": "The creative mind who makes the presentation stand out", "trait_impact": "creative_media", "trait_value": 2},
                    {"content": "The mediator who ensures everyone works well together", "trait_impact": "people_oriented", "trait_value": 2},
                    {"content": "The leader who organizes tasks and keeps things on track", "trait_impact": "business_management", "trait_value": 2}
                ]
            },
            {
                "content": "If you could shadow a professional for a day, you'd choose...",
                "category": "interest",
                "options": [
                    {"content": "An engineer, scientist, or IT professional", "trait_impact": "stem_tech", "trait_value": 2},
                    {"content": "A filmmaker, graphic designer, or musician", "trait_impact": "creative_media", "trait_value": 2},
                    {"content": "A therapist, teacher, or social worker", "trait_impact": "people_oriented", "trait_value": 2},
                    {"content": "A business executive, entrepreneur, or project manager", "trait_impact": "business_management", "trait_value": 2}
                ]
            },
            {
                "content": "Which TED talk topic would interest you the most?",
                "category": "interest",
                "options": [
                    {"content": "Breakthrough technologies or scientific discoveries", "trait_impact": "stem_tech", "trait_value": 2},
                    {"content": "The power of artistic expression or design thinking", "trait_impact": "creative_media", "trait_value": 2},
                    {"content": "Understanding human behavior or building relationships", "trait_impact": "people_oriented", "trait_value": 2},
                    {"content": "Leadership principles or entrepreneurial success stories", "trait_impact": "business_management", "trait_value": 2}
                ]
            },
            {
                "content": "On a perfect weekend, you would most enjoy...",
                "category": "interest",
                "options": [
                    {"content": "Building something, coding, or exploring how things work", "trait_impact": "stem_tech", "trait_value": 2},
                    {"content": "Creating art, music, or visiting cultural events", "trait_impact": "creative_media", "trait_value": 2},
                    {"content": "Volunteering, connecting with friends, or helping family", "trait_impact": "people_oriented", "trait_value": 2},
                    {"content": "Planning future goals or learning about business strategies", "trait_impact": "business_management", "trait_value": 2}
                ]
            },
            {
                "content": "Which of these extracurricular activities would you be most excited to join?",
                "category": "interest",
                "options": [
                    {"content": "Robotics club or coding competition", "trait_impact": "stem_tech", "trait_value": 2},
                    {"content": "Art club, photography, or theater production", "trait_impact": "creative_media", "trait_value": 2},
                    {"content": "Peer counseling, tutoring, or community service", "trait_impact": "people_oriented", "trait_value": 2},
                    {"content": "Student government, debate, or business competition", "trait_impact": "business_management", "trait_value": 2}
                ]
            },
            {
                "content": "If you were to start a blog, it would most likely be about...",
                "category": "interest",
                "options": [
                    {"content": "Technology reviews, coding tutorials, or scientific explanations", "trait_impact": "stem_tech", "trait_value": 2},
                    {"content": "Art portfolios, creative writing, or design inspiration", "trait_impact": "creative_media", "trait_value": 2},
                    {"content": "Personal growth, relationship advice, or community issues", "trait_impact": "people_oriented", "trait_value": 2},
                    {"content": "Career development, productivity tips, or leadership insights", "trait_impact": "business_management", "trait_value": 2}
                ]
            },
            {
                "content": "Which of these tasks would you find most engaging?",
                "category": "interest",
                "options": [
                    {"content": "Analyzing data or solving complex logical problems", "trait_impact": "stem_tech", "trait_value": 2},
                    {"content": "Designing visuals or creating original content", "trait_impact": "creative_media", "trait_value": 2},
                    {"content": "Mentoring others or facilitating group discussions", "trait_impact": "people_oriented", "trait_value": 2},
                    {"content": "Developing strategies or organizing systems", "trait_impact": "business_management", "trait_value": 2}
                ]
            },
            {
                "content": "If you could excel in any school subject, which would you choose?",
                "category": "interest",
                "options": [
                    {"content": "Math, physics, computer science, or engineering", "trait_impact": "stem_tech", "trait_value": 2},
                    {"content": "Art, music, design, or creative writing", "trait_impact": "creative_media", "trait_value": 2},
                    {"content": "Psychology, sociology, or communications", "trait_impact": "people_oriented", "trait_value": 2},
                    {"content": "Economics, business studies, or political science", "trait_impact": "business_management", "trait_value": 2}
                ]
            },
            {
                "content": "Which career path sounds most appealing to you?",
                "category": "interest",
                "options": [
                    {"content": "Technology, engineering, or scientific research", "trait_impact": "stem_tech", "trait_value": 2},
                    {"content": "Arts, media production, or creative design", "trait_impact": "creative_media", "trait_value": 2},
                    {"content": "Healthcare, education, or social services", "trait_impact": "people_oriented", "trait_value": 2},
                    {"content": "Business, management, or entrepreneurship", "trait_impact": "business_management", "trait_value": 2}
                ]
            },
            {
                "content": "If you had a day to learn something new, you would choose...",
                "category": "interest",
                "options": [
                    {"content": "Coding, electronics, or a scientific experiment", "trait_impact": "stem_tech", "trait_value": 2},
                    {"content": "Digital art, music production, or photography", "trait_impact": "creative_media", "trait_value": 2},
                    {"content": "Coaching techniques, communication skills, or psychology", "trait_impact": "people_oriented", "trait_value": 2},
                    {"content": "Personal finance, marketing strategies, or leadership skills", "trait_impact": "business_management", "trait_value": 2}
                ]
            }
        ]
        
        # Add questions and options to the database
        print("Adding interest questions to the database...")
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
            print(f"Successfully added {len(questions)} interest questions with options.")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error adding interest questions: {str(e)}")
            traceback.print_exc()

if __name__ == "__main__":
    add_interest_questions() 