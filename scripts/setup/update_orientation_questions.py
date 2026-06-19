"""
Script to update orientation questions with more engaging, youth-friendly content.
These questions are derived from the updated orientation style test bash script.
"""

from neuroapt.app import create_app, db
from neuroapt.app.models import Question, QuestionOption
import traceback

def update_orientation_questions():
    """Update orientation questions with more engaging versions"""
    app = create_app()
    
    with app.app_context():
        # New questions with more engaging content
        questions = [
            {
                "content": "Your teacher says, \"Present this topic however you want.\" You…",
                "options": [
                    {"content": "Build a squad, assign roles, and turn the presentation into a group project drama.", "trait_impact": "People", "trait_value": 1},
                    {"content": "Vanish into the internet, reappear with 17 tabs open and 3 conspiracy theories.", "trait_impact": "Information", "trait_value": 1},
                    {"content": "Make a chart, plan the timeline, and colour-code the workload.", "trait_impact": "Administrative", "trait_value": 1},
                    {"content": "Open Canva, blast lo-fi beats, and start turning slides into art.", "trait_impact": "Creative", "trait_value": 1}
                ]
            },
            {
                "content": "School fest is coming up. What's your jam?",
                "options": [
                    {"content": "Hyping people up, MCing, or handling crowds like a boss.", "trait_impact": "People", "trait_value": 1},
                    {"content": "Managing the sound system and Googling \"how to fix mic echo.\"", "trait_impact": "Information", "trait_value": 1},
                    {"content": "Scheduling rehearsals like NASA plans rocket launches.", "trait_impact": "Administrative", "trait_value": 1},
                    {"content": "Designing posters with more sparkle than a K-pop concert.", "trait_impact": "Creative", "trait_value": 1}
                ]
            },
            {
                "content": "A friend's panicking about tomorrow's exam. You…",
                "options": [
                    {"content": "Give them a pep talk and possibly snacks.", "trait_impact": "People", "trait_value": 1},
                    {"content": "Explain concepts like a human search engine.", "trait_impact": "Information", "trait_value": 1},
                    {"content": "Whip out a 2-hour revision plan with snack breaks.", "trait_impact": "Administrative", "trait_value": 1},
                    {"content": "Draw a meme on their notes that somehow helps them remember stuff.", "trait_impact": "Creative", "trait_value": 1}
                ]
            },
            {
                "content": "You suddenly have 30 minutes of free time in school. You...",
                "options": [
                    {"content": "Hunt down your friends like a detective with FOMO.", "trait_impact": "People", "trait_value": 1},
                    {"content": "Watch a documentary or some \"Did You Know?\" rabbit hole on YouTube.", "trait_impact": "Information", "trait_value": 1},
                    {"content": "Rewrite your to-do list for the 3rd time today.", "trait_impact": "Administrative", "trait_value": 1},
                    {"content": "Doodle random quotes that may or may not be from anime.", "trait_impact": "Creative", "trait_value": 1}
                ]
            },
            {
                "content": "A new app drops. What's the first thing you notice?",
                "options": [
                    {"content": "\"Omg, I bet my friends will love this!\"", "trait_impact": "People", "trait_value": 1},
                    {"content": "\"Wait...how does this actually work under the hood?\"", "trait_impact": "Information", "trait_value": 1},
                    {"content": "\"Hmm... the settings are nicely organized.\"", "trait_impact": "Administrative", "trait_value": 1},
                    {"content": "\"Who designed this? The aesthetic is screaming 'slay'!\"", "trait_impact": "Creative", "trait_value": 1}
                ]
            },
            {
                "content": "Group project time. You naturally become the one who…",
                "options": [
                    {"content": "Checks in with everyone like a friendly HR manager.", "trait_impact": "People", "trait_value": 1},
                    {"content": "Does deep research and somehow finds the answer on Reddit.", "trait_impact": "Information", "trait_value": 1},
                    {"content": "Sends the dreaded \"Hey, let's finish this by tonight\" message.", "trait_impact": "Administrative", "trait_value": 1},
                    {"content": "Beautifies the slides till even the teacher says \"Wow!\"", "trait_impact": "Creative", "trait_value": 1}
                ]
            },
            {
                "content": "Imagine life gives you a blank canvas. You…",
                "options": [
                    {"content": "Paint your dream job and tag your friends in it.", "trait_impact": "People", "trait_value": 1},
                    {"content": "Write a flowchart of career options with backup plans A to Z.", "trait_impact": "Information", "trait_value": 1},
                    {"content": "Organize your future into columns, subcolumns, and calendar invites.", "trait_impact": "Administrative", "trait_value": 1},
                    {"content": "Turn it into a comic strip with an existential frog and glitter.", "trait_impact": "Creative", "trait_value": 1}
                ]
            },
            {
                "content": "You get to start a new school club. What's the vibe?",
                "options": [
                    {"content": "A mental health club where everyone talks it out.", "trait_impact": "People", "trait_value": 1},
                    {"content": "A 'Nerd Out' club for coding, chess, and cracking trivia.", "trait_impact": "Information", "trait_value": 1},
                    {"content": "A \"Planner's Paradise\" — because who doesn't love structure?", "trait_impact": "Administrative", "trait_value": 1},
                    {"content": "A meme club where every week ends in an aesthetic meme drop.", "trait_impact": "Creative", "trait_value": 1}
                ]
            },
            {
                "content": "Exam season hits. You prep by…",
                "options": [
                    {"content": "Group studies that mostly turn into roast sessions but help anyway.", "trait_impact": "People", "trait_value": 1},
                    {"content": "Rewatching YouTube lectures like they're Netflix.", "trait_impact": "Information", "trait_value": 1},
                    {"content": "Creating a revision timetable worthy of Harvard.", "trait_impact": "Administrative", "trait_value": 1},
                    {"content": "Drawing concept art of mitochondria as a superhero.", "trait_impact": "Creative", "trait_value": 1}
                ]
            },
            {
                "content": "You enter a room full of strangers. You…",
                "options": [
                    {"content": "Start conversations and somehow know half their names by the end.", "trait_impact": "People", "trait_value": 1},
                    {"content": "Stand quietly... but observe everything.", "trait_impact": "Information", "trait_value": 1},
                    {"content": "Look for someone in charge so you can ask about the agenda.", "trait_impact": "Administrative", "trait_value": 1},
                    {"content": "Silently judge the interior design and imagine a better color palette.", "trait_impact": "Creative", "trait_value": 1}
                ]
            },
            {
                "content": "Your school asks you to run an Instagram account. You'd…",
                "options": [
                    {"content": "Post fun reels with your classmates.", "trait_impact": "People", "trait_value": 1},
                    {"content": "Use insights to track engagement and optimize posts.", "trait_impact": "Information", "trait_value": 1},
                    {"content": "Create a content calendar like a pro.", "trait_impact": "Administrative", "trait_value": 1},
                    {"content": "Go full Picasso on Canva and drop daily aesthetic bombs.", "trait_impact": "Creative", "trait_value": 1}
                ]
            },
            {
                "content": "Your phone storage is full. What do you delete first?",
                "options": [
                    {"content": "Not the group chat memes, never.", "trait_impact": "People", "trait_value": 1},
                    {"content": "Old screenshots of info you already absorbed into your brain.", "trait_impact": "Information", "trait_value": 1},
                    {"content": "Duplicate files and anything not labelled properly.", "trait_impact": "Administrative", "trait_value": 1},
                    {"content": "Umm… nothing. Everything is 'inspiration.'", "trait_impact": "Creative", "trait_value": 1}
                ]
            }
        ]
        
        # Get existing orientation questions
        existing_questions = Question.query.filter_by(category='orientation').all()
        
        if len(existing_questions) != 12:
            print(f"Expected 12 orientation questions, found {len(existing_questions)}.")
            print("Please run add_orientation_questions.py first.")
            return
        
        print("Updating orientation questions with more engaging content...")
        try:
            # Update each question and its options
            for i, q_data in enumerate(questions):
                if i < len(existing_questions):
                    # Update the question content
                    question = existing_questions[i]
                    question.content = q_data["content"]
                    
                    # Update the options
                    options = QuestionOption.query.filter_by(question_id=question.id).all()
                    if len(options) == 4:
                        for j, opt_data in enumerate(q_data["options"]):
                            options[j].content = opt_data["content"]
                            options[j].trait_impact = opt_data["trait_impact"]
                            options[j].trait_value = opt_data["trait_value"]
            
            # Commit all changes
            db.session.commit()
            print("Successfully updated 12 orientation questions with more engaging content.")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error updating orientation questions: {str(e)}")
            traceback.print_exc()

if __name__ == "__main__":
    update_orientation_questions() 