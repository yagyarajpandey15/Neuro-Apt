import os
import sqlite3
from datetime import datetime

print("Script started!")

def add_work_style_questions():
    """
    Add new work style assessment questions to the database
    """
    print("Adding work style assessment questions...")
    
    # Path to the database file
    db_path = os.path.join('neuroapt', 'app', 'neuroapt.db')
    
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        return
    
    print(f"Database found at {db_path}")
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # First, check if the work_style category exists in any questions
        cursor.execute("SELECT COUNT(*) FROM question WHERE category = 'work_style'")
        count = cursor.fetchone()[0]
        
        print(f"Found {count} existing work_style questions")
        
        if count > 0:
            print("Work style questions already exist in the database. Skipping...")
            return
        
        print("Adding 12 new work style questions...")
        
        # Define the questions and options
        questions = [
            {
                "content": "Your teacher says, \"Present this topic however you want.\" You…",
                "options": [
                    {"content": "Build a squad, assign roles, and turn the presentation into a group project drama.", "trait_impact": "teamwork", "trait_value": 10},
                    {"content": "Vanish into the internet, reappear with 17 tabs open and 3 conspiracy theories.", "trait_impact": "analytical", "trait_value": 10},
                    {"content": "Make a chart, plan the timeline, and colour-code the workload.", "trait_impact": "conscientiousness", "trait_value": 10},
                    {"content": "Open Canva, blast lo-fi beats, and start turning slides into art.", "trait_impact": "creativity", "trait_value": 10}
                ]
            },
            {
                "content": "School fest is coming up. What's your jam?",
                "options": [
                    {"content": "Hyping people up, MCing, or handling crowds like a boss.", "trait_impact": "extraversion", "trait_value": 10},
                    {"content": "Managing the sound system and Googling \"how to fix mic echo.\"", "trait_impact": "analytical", "trait_value": 10},
                    {"content": "Scheduling rehearsals like NASA plans rocket launches.", "trait_impact": "conscientiousness", "trait_value": 10},
                    {"content": "Designing posters with more sparkle than a K-pop concert.", "trait_impact": "creativity", "trait_value": 10}
                ]
            },
            {
                "content": "A friend's panicking about tomorrow's exam. You…",
                "options": [
                    {"content": "Give them a pep talk and possibly snacks.", "trait_impact": "agreeableness", "trait_value": 10},
                    {"content": "Explain concepts like a human search engine.", "trait_impact": "analytical", "trait_value": 10},
                    {"content": "Whip out a 2-hour revision plan with snack breaks.", "trait_impact": "conscientiousness", "trait_value": 10},
                    {"content": "Draw a meme on their notes that somehow helps them remember stuff.", "trait_impact": "creativity", "trait_value": 10}
                ]
            },
            {
                "content": "You suddenly have 30 minutes of free time in school. You...",
                "options": [
                    {"content": "Hunt down your friends like a detective with FOMO.", "trait_impact": "extraversion", "trait_value": 10},
                    {"content": "Watch a documentary or some \"Did You Know?\" rabbit hole on YouTube.", "trait_impact": "openness", "trait_value": 10},
                    {"content": "Rewrite your to-do list for the 3rd time today.", "trait_impact": "conscientiousness", "trait_value": 10},
                    {"content": "Doodle random quotes that may or may not be from anime.", "trait_impact": "creativity", "trait_value": 10}
                ]
            },
            {
                "content": "A new app drops. What's the first thing you notice?",
                "options": [
                    {"content": "\"Omg, I bet my friends will love this!\"", "trait_impact": "extraversion", "trait_value": 10},
                    {"content": "\"Wait...how does this actually work under the hood?\"", "trait_impact": "analytical", "trait_value": 10},
                    {"content": "\"Hmm... the settings are nicely organized.\"", "trait_impact": "conscientiousness", "trait_value": 10},
                    {"content": "\"Who designed this? The aesthetic is screaming 'slay'!\"", "trait_impact": "creativity", "trait_value": 10}
                ]
            },
            {
                "content": "Group project time. You naturally become the one who…",
                "options": [
                    {"content": "Checks in with everyone like a friendly HR manager.", "trait_impact": "leadership", "trait_value": 10},
                    {"content": "Does deep research and somehow finds the answer on Reddit.", "trait_impact": "analytical", "trait_value": 10},
                    {"content": "Sends the dreaded \"Hey, let's finish this by tonight\" message.", "trait_impact": "conscientiousness", "trait_value": 10},
                    {"content": "Beautifies the slides till even the teacher says \"Wow!\"", "trait_impact": "creativity", "trait_value": 10}
                ]
            },
            {
                "content": "Imagine life gives you a blank canvas. You…",
                "options": [
                    {"content": "Paint your dream job and tag your friends in it.", "trait_impact": "extraversion", "trait_value": 10},
                    {"content": "Write a flowchart of career options with backup plans A to Z.", "trait_impact": "analytical", "trait_value": 10},
                    {"content": "Organize your future into columns, subcolumns, and calendar invites.", "trait_impact": "conscientiousness", "trait_value": 10},
                    {"content": "Turn it into a comic strip with an existential frog and glitter.", "trait_impact": "creativity", "trait_value": 10}
                ]
            },
            {
                "content": "You get to start a new school club. What's the vibe?",
                "options": [
                    {"content": "A mental health club where everyone talks it out.", "trait_impact": "agreeableness", "trait_value": 10},
                    {"content": "A 'Nerd Out' club for coding, chess, and cracking trivia.", "trait_impact": "analytical", "trait_value": 10},
                    {"content": "A \"Planner's Paradise\" — because who doesn't love structure?", "trait_impact": "conscientiousness", "trait_value": 10},
                    {"content": "A meme club where every week ends in an aesthetic meme drop.", "trait_impact": "creativity", "trait_value": 10}
                ]
            },
            {
                "content": "Exam season hits. You prep by…",
                "options": [
                    {"content": "Group studies that mostly turn into roast sessions but help anyway.", "trait_impact": "teamwork", "trait_value": 10},
                    {"content": "Rewatching YouTube lectures like they're Netflix.", "trait_impact": "analytical", "trait_value": 10},
                    {"content": "Creating a revision timetable worthy of Harvard.", "trait_impact": "conscientiousness", "trait_value": 10},
                    {"content": "Drawing concept art of mitochondria as a superhero.", "trait_impact": "creativity", "trait_value": 10}
                ]
            },
            {
                "content": "You enter a room full of strangers. You…",
                "options": [
                    {"content": "Start conversations and somehow know half their names by the end.", "trait_impact": "extraversion", "trait_value": 10},
                    {"content": "Stand quietly... but observe everything.", "trait_impact": "openness", "trait_value": 10},
                    {"content": "Look for someone in charge so you can ask about the agenda.", "trait_impact": "conscientiousness", "trait_value": 10},
                    {"content": "Silently judge the interior design and imagine a better color palette.", "trait_impact": "creativity", "trait_value": 10}
                ]
            },
            {
                "content": "Your school asks you to run an Instagram account. You'd…",
                "options": [
                    {"content": "Post fun reels with your classmates.", "trait_impact": "extraversion", "trait_value": 10},
                    {"content": "Use insights to track engagement and optimize posts.", "trait_impact": "analytical", "trait_value": 10},
                    {"content": "Create a content calendar like a pro.", "trait_impact": "conscientiousness", "trait_value": 10},
                    {"content": "Go full Picasso on Canva and drop daily aesthetic bombs.", "trait_impact": "creativity", "trait_value": 10}
                ]
            },
            {
                "content": "Your phone storage is full. What do you delete first?",
                "options": [
                    {"content": "Not the group chat memes, never.", "trait_impact": "teamwork", "trait_value": 10},
                    {"content": "Old screenshots of info you already absorbed into your brain.", "trait_impact": "analytical", "trait_value": 10},
                    {"content": "Duplicate files and anything not labelled properly.", "trait_impact": "conscientiousness", "trait_value": 10},
                    {"content": "Umm… nothing. Everything is 'inspiration.'", "trait_impact": "creativity", "trait_value": 10}
                ]
            }
        ]
        
        # Insert the questions and options
        for question in questions:
            # Insert the question
            cursor.execute(
                "INSERT INTO question (category, content) VALUES (?, ?)",
                ('work_style', question['content'])
            )
            question_id = cursor.lastrowid
            print(f"Added question ID {question_id}: {question['content'][:30]}...")
            
            # Insert the options for this question
            for option in question['options']:
                cursor.execute(
                    "INSERT INTO question_option (question_id, content, is_correct, score_value, trait_impact, trait_value) VALUES (?, ?, ?, ?, ?, ?)",
                    (question_id, option['content'], False, 1, option['trait_impact'], option['trait_value'])
                )
                option_id = cursor.lastrowid
                print(f"  - Added option ID {option_id}: {option['content'][:20]}... ({option['trait_impact']})")
        
        # Update the test flow to include the work_style section
        # First, check if test.py has the work_style section in the test_sections list
        print("Note: You may need to update the test_sections list in neuroapt/app/routes/test.py to include 'work_style'")
        
        # Commit the changes
        conn.commit()
        print("Work style questions added successfully")
        
    except Exception as e:
        print(f"Error adding work style questions: {e}")
        conn.rollback()
    finally:
        conn.close()

print("Calling add_work_style_questions function...")
if __name__ == "__main__":
    add_work_style_questions()
print("Script finished!") 