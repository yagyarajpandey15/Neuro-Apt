"""
Script to add orientation questions to the database.
These questions are derived from the orientation style test bash script.
"""

from neuroapt.app import create_app, db
from neuroapt.app.models import Question, QuestionOption
import traceback

def add_orientation_questions():
    """Add orientation questions to the database"""
    app = create_app()
    
    with app.app_context():
        # Check if orientation questions already exist
        existing_count = Question.query.filter_by(category='orientation').count()
        if existing_count >= 15:
            print(f"Found {existing_count} existing orientation questions. Skipping.")
            return
        
        # Define questions and options
        questions = [
            {
                "content": "Your teacher says, \"Present this topic however you want.\" You…",
                "category": "orientation",
                "options": [
                    {"content": "Create a group discussion activity", "trait_impact": "People", "trait_value": 1},
                    {"content": "Make a detailed research presentation", "trait_impact": "Information", "trait_value": 1},
                    {"content": "Create a step-by-step guide", "trait_impact": "Administrative", "trait_value": 1},
                    {"content": "Design something artistic and unconventional", "trait_impact": "Creative", "trait_value": 1}
                ]
            },
            {
                "content": "School fest is coming up. What's your jam?",
                "category": "orientation",
                "options": [
                    {"content": "Coordinating people and managing volunteers", "trait_impact": "People", "trait_value": 1},
                    {"content": "Planning the schedule and analyzing what worked last year", "trait_impact": "Information", "trait_value": 1},
                    {"content": "Creating schedules and tracking sign-ups", "trait_impact": "Administrative", "trait_value": 1},
                    {"content": "Designing posters and theme ideas", "trait_impact": "Creative", "trait_value": 1}
                ]
            },
            {
                "content": "A friend's panicking about tomorrow's exam. You…",
                "category": "orientation",
                "options": [
                    {"content": "Listen and offer emotional support", "trait_impact": "People", "trait_value": 1},
                    {"content": "Analyze which topics they're struggling with most", "trait_impact": "Information", "trait_value": 1},
                    {"content": "Help them make a structured study plan for the night", "trait_impact": "Administrative", "trait_value": 1},
                    {"content": "Suggest a new study approach they haven't considered", "trait_impact": "Creative", "trait_value": 1}
                ]
            },
            {
                "content": "You suddenly have 30 minutes of free time in school. You...",
                "category": "orientation",
                "options": [
                    {"content": "Catch up with friends or help someone with homework", "trait_impact": "People", "trait_value": 1},
                    {"content": "Read something interesting or research a topic", "trait_impact": "Information", "trait_value": 1},
                    {"content": "Organize your notes or plan your schedule", "trait_impact": "Administrative", "trait_value": 1},
                    {"content": "Sketch, write, or come up with ideas", "trait_impact": "Creative", "trait_value": 1}
                ]
            },
            {
                "content": "A new app drops. What's the first thing you notice?",
                "category": "orientation",
                "options": [
                    {"content": "How it connects people and builds community", "trait_impact": "People", "trait_value": 1},
                    {"content": "The data and functionality it provides", "trait_impact": "Information", "trait_value": 1},
                    {"content": "How organized and user-friendly it is", "trait_impact": "Administrative", "trait_value": 1},
                    {"content": "Its innovative design and unique features", "trait_impact": "Creative", "trait_value": 1}
                ]
            },
            {
                "content": "Group project time. You naturally become the one who…",
                "category": "orientation",
                "options": [
                    {"content": "Makes sure everyone feels included and heard", "trait_impact": "People", "trait_value": 1},
                    {"content": "Researches and provides the key information", "trait_impact": "Information", "trait_value": 1},
                    {"content": "Creates timelines and keeps everyone on track", "trait_impact": "Administrative", "trait_value": 1},
                    {"content": "Comes up with the original concept and design", "trait_impact": "Creative", "trait_value": 1}
                ]
            },
            {
                "content": "Imagine life gives you a blank canvas. You…",
                "category": "orientation",
                "options": [
                    {"content": "Paint a scene of people connecting and helping each other", "trait_impact": "People", "trait_value": 1},
                    {"content": "Create a detailed map or diagram of something important", "trait_impact": "Information", "trait_value": 1},
                    {"content": "Design an organized, balanced composition with structure", "trait_impact": "Administrative", "trait_value": 1},
                    {"content": "Let your imagination run wild with colors and abstract forms", "trait_impact": "Creative", "trait_value": 1}
                ]
            },
            {
                "content": "You get to start a new school club. What's the vibe?",
                "category": "orientation",
                "options": [
                    {"content": "Community service or peer support", "trait_impact": "People", "trait_value": 1},
                    {"content": "Debate, research, or academic enrichment", "trait_impact": "Information", "trait_value": 1},
                    {"content": "Planning events or school improvement initiatives", "trait_impact": "Administrative", "trait_value": 1},
                    {"content": "Arts, innovation, or creative projects", "trait_impact": "Creative", "trait_value": 1}
                ]
            },
            {
                "content": "Exam season hits. You prep by…",
                "category": "orientation",
                "options": [
                    {"content": "Forming study groups and learning by discussion", "trait_impact": "People", "trait_value": 1},
                    {"content": "Deep diving into concepts and connecting ideas", "trait_impact": "Information", "trait_value": 1},
                    {"content": "Making detailed study schedules and checklists", "trait_impact": "Administrative", "trait_value": 1},
                    {"content": "Creating mind maps and unique memory techniques", "trait_impact": "Creative", "trait_value": 1}
                ]
            },
            {
                "content": "You enter a room full of strangers. You…",
                "category": "orientation",
                "options": [
                    {"content": "Start introducing yourself and connecting people", "trait_impact": "People", "trait_value": 1},
                    {"content": "Observe and analyze the social dynamics", "trait_impact": "Information", "trait_value": 1},
                    {"content": "Look for the agenda or purpose of the gathering", "trait_impact": "Administrative", "trait_value": 1},
                    {"content": "Notice the unique atmosphere and possibilities", "trait_impact": "Creative", "trait_value": 1}
                ]
            },
            {
                "content": "Your school asks you to run an Instagram account. You'd…",
                "category": "orientation",
                "options": [
                    {"content": "Focus on student stories and community engagement", "trait_impact": "People", "trait_value": 1},
                    {"content": "Share educational content and interesting facts", "trait_impact": "Information", "trait_value": 1},
                    {"content": "Create consistent posting schedules and organized themes", "trait_impact": "Administrative", "trait_value": 1},
                    {"content": "Design eye-catching graphics and unique content", "trait_impact": "Creative", "trait_value": 1}
                ]
            },
            {
                "content": "Your phone storage is full. What do you delete first?",
                "category": "orientation",
                "options": [
                    {"content": "Fewer social apps - you prefer in-person connections anyway", "trait_impact": "People", "trait_value": 1},
                    {"content": "Games or entertainment apps but keep your research tools", "trait_impact": "Information", "trait_value": 1},
                    {"content": "Duplicate photos and unused apps to maintain order", "trait_impact": "Administrative", "trait_value": 1},
                    {"content": "Productivity apps - you'd rather keep your creative tools", "trait_impact": "Creative", "trait_value": 1}
                ]
            },
            {
                "content": "When solving a difficult problem, your first instinct is to...",
                "category": "orientation",
                "options": [
                    {"content": "Talk it through with others to get different perspectives", "trait_impact": "People", "trait_value": 1},
                    {"content": "Research and gather as much information as possible", "trait_impact": "Information", "trait_value": 1},
                    {"content": "Break it down into smaller, manageable steps", "trait_impact": "Administrative", "trait_value": 1},
                    {"content": "Think outside the box for an innovative solution", "trait_impact": "Creative", "trait_value": 1}
                ]
            },
            {
                "content": "Your dream workspace would be...",
                "category": "orientation",
                "options": [
                    {"content": "An open collaborative space with areas for group discussions", "trait_impact": "People", "trait_value": 1},
                    {"content": "A quiet library with access to extensive resources", "trait_impact": "Information", "trait_value": 1},
                    {"content": "A well-organized office with clear systems and structure", "trait_impact": "Administrative", "trait_value": 1},
                    {"content": "A flexible, inspiring environment with visual stimulation", "trait_impact": "Creative", "trait_value": 1}
                ]
            },
            {
                "content": "Your favorite class project would involve...",
                "category": "orientation",
                "options": [
                    {"content": "Interviewing people and gathering personal stories", "trait_impact": "People", "trait_value": 1},
                    {"content": "Creating a detailed analysis backed by solid research", "trait_impact": "Information", "trait_value": 1},
                    {"content": "Developing a systematic approach with measurable outcomes", "trait_impact": "Administrative", "trait_value": 1},
                    {"content": "Building something unique that hasn't been tried before", "trait_impact": "Creative", "trait_value": 1}
                ]
            },
            {
                "content": "When learning something new, you prefer to...",
                "category": "orientation",
                "options": [
                    {"content": "Join a group class or find a study buddy", "trait_impact": "People", "trait_value": 1},
                    {"content": "Read extensively about the theory and concepts", "trait_impact": "Information", "trait_value": 1},
                    {"content": "Follow a structured curriculum step by step", "trait_impact": "Administrative", "trait_value": 1},
                    {"content": "Explore and experiment with your own approach", "trait_impact": "Creative", "trait_value": 1}
                ]
            },
            {
                "content": "Your ideal role in a team project would be...",
                "category": "orientation",
                "options": [
                    {"content": "The facilitator who ensures everyone works well together", "trait_impact": "People", "trait_value": 1},
                    {"content": "The researcher who gathers and analyzes all necessary information", "trait_impact": "Information", "trait_value": 1},
                    {"content": "The organizer who creates timelines and tracks progress", "trait_impact": "Administrative", "trait_value": 1},
                    {"content": "The innovator who comes up with original ideas", "trait_impact": "Creative", "trait_value": 1}
                ]
            },
            {
                "content": "When making decisions, you primarily consider...",
                "category": "orientation",
                "options": [
                    {"content": "How it will affect others and their feelings", "trait_impact": "People", "trait_value": 1},
                    {"content": "What the facts and data suggest is the best choice", "trait_impact": "Information", "trait_value": 1},
                    {"content": "Which option provides the most structure and certainty", "trait_impact": "Administrative", "trait_value": 1},
                    {"content": "What unique possibilities or opportunities might emerge", "trait_impact": "Creative", "trait_value": 1}
                ]
            },
            {
                "content": "Your approach to a new technology is to...",
                "category": "orientation",
                "options": [
                    {"content": "Ask friends how they use it and share experiences", "trait_impact": "People", "trait_value": 1},
                    {"content": "Read the manual and understand all the features thoroughly", "trait_impact": "Information", "trait_value": 1},
                    {"content": "Set up a systematic way to incorporate it into your routine", "trait_impact": "Administrative", "trait_value": 1},
                    {"content": "Immediately explore unusual ways to use it", "trait_impact": "Creative", "trait_value": 1}
                ]
            },
            {
                "content": "If you could improve your school, you would focus on...",
                "category": "orientation",
                "options": [
                    {"content": "Creating more opportunities for social connection and teamwork", "trait_impact": "People", "trait_value": 1},
                    {"content": "Enhancing research facilities and information resources", "trait_impact": "Information", "trait_value": 1},
                    {"content": "Implementing better systems and organizational structures", "trait_impact": "Administrative", "trait_value": 1},
                    {"content": "Adding more arts programs and creative spaces", "trait_impact": "Creative", "trait_value": 1}
                ]
            },
            {
                "content": "Your preferred way to plan a vacation is to...",
                "category": "orientation",
                "options": [
                    {"content": "Ask friends for recommendations and plan activities everyone will enjoy", "trait_impact": "People", "trait_value": 1},
                    {"content": "Research destinations thoroughly and create an information guide", "trait_impact": "Information", "trait_value": 1},
                    {"content": "Create a detailed itinerary with times and reservations", "trait_impact": "Administrative", "trait_value": 1},
                    {"content": "Choose a destination that inspires and leave room for spontaneous adventures", "trait_impact": "Creative", "trait_value": 1}
                ]
            },
            {
                "content": "When faced with a challenge, your greatest strength is...",
                "category": "orientation",
                "options": [
                    {"content": "Bringing people together to collaborate on solutions", "trait_impact": "People", "trait_value": 1},
                    {"content": "Analyzing complex information to find hidden patterns", "trait_impact": "Information", "trait_value": 1},
                    {"content": "Creating systems and processes to address the problem", "trait_impact": "Administrative", "trait_value": 1},
                    {"content": "Finding unexpected and creative approaches", "trait_impact": "Creative", "trait_value": 1}
                ]
            },
            {
                "content": "Your communication style tends to be...",
                "category": "orientation",
                "options": [
                    {"content": "Warm and focused on building rapport with others", "trait_impact": "People", "trait_value": 1},
                    {"content": "Clear, precise, and information-rich", "trait_impact": "Information", "trait_value": 1},
                    {"content": "Well-structured and following a logical sequence", "trait_impact": "Administrative", "trait_value": 1},
                    {"content": "Expressive, with vivid descriptions and stories", "trait_impact": "Creative", "trait_value": 1}
                ]
            }
        ]
        
        # Add questions and options to the database
        print("Adding orientation questions to the database...")
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
            print(f"Successfully added {len(questions)} orientation questions with options.")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error adding orientation questions: {str(e)}")
            traceback.print_exc()

if __name__ == "__main__":
    add_orientation_questions() 