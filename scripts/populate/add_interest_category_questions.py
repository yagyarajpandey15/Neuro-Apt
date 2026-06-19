#!/usr/bin/env python
from neuroapt.app import create_app, db
from neuroapt.app.models import Question, QuestionOption
import traceback

def add_interest_category_questions():
    app = create_app()
    with app.app_context():
        try:
            # Check if questions already exist
            existing_count = Question.query.filter_by(category='interest_category').count()
            print(f"Found {existing_count} existing interest category questions")
            
            if existing_count > 0:
                print(f"Interest category questions already exist ({existing_count} found). Do you want to delete and recreate them? (y/n)")
                choice = input().lower()
                if choice == 'y':
                    print("Deleting existing interest category questions...")
                    # Delete existing questions and their options
                    interest_questions = Question.query.filter_by(category='interest_category').all()
                    for question in interest_questions:
                        QuestionOption.query.filter_by(question_id=question.id).delete()
                    Question.query.filter_by(category='interest_category').delete()
                    db.session.commit()
                    print(f"Deleted {existing_count} interest category questions")
                else:
                    print("Skipping question creation...")
                    return
            
            # Define clusters and questions
            clusters = [
                "STEM & Tech",
                "Creative & Media",
                "People-Oriented",
                "Business & Management",
                "Legal & Governance",
                "Logistics & Distribution"
            ]
            
            questions = [
                {
                    "content": "You just aced a math problem that no one else could solve. What's your next move?",
                    "options": [
                        {"content": "Look for an even harder problem to solve", "trait_impact": "STEM & Tech", "trait_value": 1},
                        {"content": "Create a visual guide to explain your solution", "trait_impact": "Creative & Media", "trait_value": 1},
                        {"content": "Offer to help classmates who are struggling", "trait_impact": "People-Oriented", "trait_value": 1},
                        {"content": "Think of how this skill could be valuable in a job", "trait_impact": "Business & Management", "trait_value": 1}
                    ]
                },
                {
                    "content": "Your school is hosting a talent show. What do you sign up for?",
                    "options": [
                        {"content": "Performing an original song or comedy routine", "trait_impact": "Creative & Media", "trait_value": 1},
                        {"content": "A science demonstration with cool effects", "trait_impact": "STEM & Tech", "trait_value": 1},
                        {"content": "Organizing and emceeing the event", "trait_impact": "Business & Management", "trait_value": 1},
                        {"content": "Ensuring the event follows all school policies", "trait_impact": "Legal & Governance", "trait_value": 1}
                    ]
                },
                {
                    "content": "A friend is crying over a breakup. What do you do?",
                    "options": [
                        {"content": "Listen and offer emotional support", "trait_impact": "People-Oriented", "trait_value": 1},
                        {"content": "Suggest creative ways to express their feelings", "trait_impact": "Creative & Media", "trait_value": 1},
                        {"content": "Analyze the relationship objectively to identify issues", "trait_impact": "STEM & Tech", "trait_value": 1},
                        {"content": "Help them create a plan to move forward", "trait_impact": "Business & Management", "trait_value": 1}
                    ]
                },
                {
                    "content": "You're assigned to plan a school trip. What's your role?",
                    "options": [
                        {"content": "Creating a memorable theme and activities", "trait_impact": "Creative & Media", "trait_value": 1},
                        {"content": "Arranging transportation and accommodations", "trait_impact": "Logistics & Distribution", "trait_value": 1},
                        {"content": "Managing the budget and finances", "trait_impact": "Business & Management", "trait_value": 1},
                        {"content": "Ensuring safety protocols and permissions are in place", "trait_impact": "Legal & Governance", "trait_value": 1}
                    ]
                },
                {
                    "content": "You catch two students cheating. You...",
                    "options": [
                        {"content": "Create an alternative assignment that's harder to cheat on", "trait_impact": "Creative & Media", "trait_value": 1},
                        {"content": "Report them according to school policy", "trait_impact": "Legal & Governance", "trait_value": 1},
                        {"content": "Talk to them privately to understand why they cheated", "trait_impact": "People-Oriented", "trait_value": 1},
                        {"content": "Analyze how to improve the testing system to prevent cheating", "trait_impact": "STEM & Tech", "trait_value": 1}
                    ]
                },
                {
                    "content": "If you had an hour of free time daily, what would you do?",
                    "options": [
                        {"content": "Learn coding or work on a science project", "trait_impact": "STEM & Tech", "trait_value": 1},
                        {"content": "Mentor younger students", "trait_impact": "People-Oriented", "trait_value": 1},
                        {"content": "Research investment strategies", "trait_impact": "Business & Management", "trait_value": 1},
                        {"content": "Work on your photography or writing", "trait_impact": "Creative & Media", "trait_value": 1}
                    ]
                },
                {
                    "content": "Your school received 50 new lab kits. You are asked to...",
                    "options": [
                        {"content": "Create an inventory system and distribution plan", "trait_impact": "Logistics & Distribution", "trait_value": 1},
                        {"content": "Test them out and suggest experiment ideas", "trait_impact": "STEM & Tech", "trait_value": 1},
                        {"content": "Design a promotional poster for the new equipment", "trait_impact": "Creative & Media", "trait_value": 1},
                        {"content": "Develop a business case for more educational resources", "trait_impact": "Business & Management", "trait_value": 1}
                    ]
                },
                {
                    "content": "You're the MC at an event. What's your vibe?",
                    "options": [
                        {"content": "Warm and engaging, making everyone feel welcome", "trait_impact": "People-Oriented", "trait_value": 1},
                        {"content": "Creative and entertaining, with jokes and stories", "trait_impact": "Creative & Media", "trait_value": 1},
                        {"content": "Efficient and organized, keeping everything on schedule", "trait_impact": "Logistics & Distribution", "trait_value": 1},
                        {"content": "Professional and proper, following protocol", "trait_impact": "Legal & Governance", "trait_value": 1}
                    ]
                },
                {
                    "content": "You started a small candy shop in your school. What excites you the most?",
                    "options": [
                        {"content": "Analyzing sales data to optimize your stock", "trait_impact": "Business & Management", "trait_value": 1},
                        {"content": "Creating unique packaging and marketing", "trait_impact": "Creative & Media", "trait_value": 1},
                        {"content": "Using math to calculate profits and growth", "trait_impact": "STEM & Tech", "trait_value": 1},
                        {"content": "Managing inventory and supply chain", "trait_impact": "Logistics & Distribution", "trait_value": 1}
                    ]
                },
                {
                    "content": "You are asked to give a motivational speech. What's your theme?",
                    "options": [
                        {"content": "Innovation and technology's power to change the world", "trait_impact": "STEM & Tech", "trait_value": 1},
                        {"content": "Finding your creative voice and unique vision", "trait_impact": "Creative & Media", "trait_value": 1},
                        {"content": "The importance of empathy and human connection", "trait_impact": "People-Oriented", "trait_value": 1},
                        {"content": "Justice and standing up for what's right", "trait_impact": "Legal & Governance", "trait_value": 1}
                    ]
                },
                {
                    "content": "You're part of a team project. What do you naturally take over?",
                    "options": [
                        {"content": "Planning the budget and timeline", "trait_impact": "Business & Management", "trait_value": 1},
                        {"content": "Making the presentation visually appealing", "trait_impact": "Creative & Media", "trait_value": 1},
                        {"content": "Researching and analyzing data", "trait_impact": "STEM & Tech", "trait_value": 1},
                        {"content": "Ensuring everyone's ideas are heard", "trait_impact": "People-Oriented", "trait_value": 1}
                    ]
                },
                {
                    "content": "A major shipment of supplies got delayed. You are...",
                    "options": [
                        {"content": "Quickly revising logistics to manage the delay", "trait_impact": "Logistics & Distribution", "trait_value": 1},
                        {"content": "Calculating the impact on project timelines", "trait_impact": "STEM & Tech", "trait_value": 1},
                        {"content": "Finding creative alternatives in the meantime", "trait_impact": "Creative & Media", "trait_value": 1},
                        {"content": "Reviewing contracts for possible recourse", "trait_impact": "Legal & Governance", "trait_value": 1}
                    ]
                },
                {
                    "content": "A teacher gives your class an unfair punishment. You...",
                    "options": [
                        {"content": "Research school policy to challenge the decision", "trait_impact": "Legal & Governance", "trait_value": 1},
                        {"content": "Talk to the teacher to understand their perspective", "trait_impact": "People-Oriented", "trait_value": 1},
                        {"content": "Write a persuasive letter to present your case", "trait_impact": "Creative & Media", "trait_value": 1},
                        {"content": "Gather data on how the punishment affects learning", "trait_impact": "Business & Management", "trait_value": 1}
                    ]
                },
                {
                    "content": "Your friend is confused about future careers. You...",
                    "options": [
                        {"content": "Share videos and articles about interesting jobs", "trait_impact": "Creative & Media", "trait_value": 1},
                        {"content": "Discuss what makes them happy and fulfilled", "trait_impact": "People-Oriented", "trait_value": 1},
                        {"content": "Suggest exploring STEM fields with good prospects", "trait_impact": "STEM & Tech", "trait_value": 1},
                        {"content": "Help them analyze salary and job growth data", "trait_impact": "Business & Management", "trait_value": 1}
                    ]
                },
                {
                    "content": "You're leading the school cabinet. What's your first agenda?",
                    "options": [
                        {"content": "Updating the student code of conduct", "trait_impact": "Legal & Governance", "trait_value": 1},
                        {"content": "Improving inventory of school supplies", "trait_impact": "Logistics & Distribution", "trait_value": 1},
                        {"content": "Planning a creative fundraising campaign", "trait_impact": "Creative & Media", "trait_value": 1},
                        {"content": "Starting a student mentorship program", "trait_impact": "Business & Management", "trait_value": 1}
                    ]
                },
                {
                    "content": "A teacher's absent and you're in charge. What's your plan?",
                    "options": [
                        {"content": "Lead a discussion on how everyone's feeling", "trait_impact": "People-Oriented", "trait_value": 1},
                        {"content": "Set up a challenging problem for everyone to solve", "trait_impact": "STEM & Tech", "trait_value": 1},
                        {"content": "Organize group work with clear deliverables", "trait_impact": "Business & Management", "trait_value": 1},
                        {"content": "Start a creative brainstorming session", "trait_impact": "Creative & Media", "trait_value": 1}
                    ]
                },
                {
                    "content": "You've invented a new gadget. What next?",
                    "options": [
                        {"content": "Research patents and intellectual property laws", "trait_impact": "Business & Management", "trait_value": 1},
                        {"content": "Refine the technology and add features", "trait_impact": "STEM & Tech", "trait_value": 1},
                        {"content": "Design sleek packaging and marketing materials", "trait_impact": "Creative & Media", "trait_value": 1},
                        {"content": "Consult legal experts about regulations", "trait_impact": "Legal & Governance", "trait_value": 1}
                    ]
                },
                {
                    "content": "You won a free trip to a career fair. What booth excites you most?",
                    "options": [
                        {"content": "Technology companies showcasing new gadgets", "trait_impact": "STEM & Tech", "trait_value": 1},
                        {"content": "Design and media agencies with interactive displays", "trait_impact": "Creative & Media", "trait_value": 1},
                        {"content": "Healthcare and education organizations helping people", "trait_impact": "People-Oriented", "trait_value": 1},
                        {"content": "Logistics companies with global supply chain solutions", "trait_impact": "Logistics & Distribution", "trait_value": 1}
                    ]
                }
            ]

            print(f"Adding {len(questions)} interest category questions to database...")
            # Add questions and options to the database
            added_questions = 0
            added_options = 0
            
            # Add questions and options to the database
            for question_data in questions:
                question = Question(
                    category='interest_category',
                    content=question_data['content']
                )
                db.session.add(question)
                db.session.flush()  # To get the question ID
                added_questions += 1
                
                for option_data in question_data['options']:
                    option = QuestionOption(
                        question_id=question.id,
                        content=option_data['content'],
                        trait_impact=option_data['trait_impact'],
                        trait_value=option_data['trait_value'],
                        score_value=1  # Set a default score value
                    )
                    db.session.add(option)
                    added_options += 1
            
            db.session.commit()
            print(f"Successfully added {added_questions} questions with {added_options} options.")
            
            # Verify questions were added
            verify_count = Question.query.filter_by(category='interest_category').count()
            print(f"Verified: {verify_count} interest category questions now in database")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error adding interest category questions: {str(e)}")
            print(traceback.format_exc())

if __name__ == "__main__":
    add_interest_category_questions() 