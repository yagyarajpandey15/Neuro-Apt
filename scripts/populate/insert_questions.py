import sqlite3
import os

# Path to the SQLite database
db_path = os.path.join('neuroapt', 'app', 'neuroapt.db')

print(f"Database path: {os.path.abspath(db_path)}")
if os.path.exists(db_path):
    print(f"Database file exists at {db_path}")
else:
    print(f"Database file does not exist at {db_path}")
    exit(1)

# Define questions for each section
orientation_questions = [
    "How do you prefer to learn new concepts?",
    "Do you enjoy working with visual aids like diagrams or charts?",
    "Do you retain information better when listening to lectures or podcasts?",
    "Do you prefer hands-on activities?",
    "Do you need quiet surroundings to focus?",
    "Do you like studying in groups?",
    "Are you comfortable with multitasking?",
    "Do you like following structured routines?",
    "Can you adapt quickly to changing plans?",
    "Do you prefer theoretical knowledge or practical work?",
    "Do you take detailed notes during lectures?",
    "Are you a morning person or a night owl?",
    "Do you plan tasks ahead or go with the flow?",
    "Can you manage deadlines easily?",
    "Do you prefer independent or collaborative work?",
    "Do you enjoy problem-solving over execution?",
    "Are you more comfortable using a computer or physical tools?",
    "Do you prefer visuals over text?",
    "Do you revise by teaching others?",
    "Are you more productive under pressure?"
]

interest_questions = [
    "Do you enjoy solving puzzles?",
    "Are you interested in how machines work?",
    "Do you like drawing or painting?",
    "Do you read about finance or investing?",
    "Are you interested in helping others?",
    "Do you enjoy working with data and graphs?",
    "Do you write stories or blogs?",
    "Do you like coding or building apps?",
    "Are you interested in space and astronomy?",
    "Do you like leading teams or organizing events?",
    "Are you curious about how people think?",
    "Do you play strategy games?",
    "Are you interested in animals and nature?",
    "Do you like experimenting in a lab?",
    "Are you drawn to history and culture?",
    "Do you follow news about new technologies?",
    "Do you enjoy public speaking?",
    "Do you enjoy working with numbers?",
    "Do you like analyzing business trends?",
    "Do you prefer fieldwork or office work?"
]

personality_questions = [
    "Do you consider yourself an introvert or extrovert?",
    "Are you detail-oriented?",
    "Do you enjoy taking initiative?",
    "Are you comfortable in leadership roles?",
    "Do you prefer routine or variety in tasks?",
    "Do you often empathize with others?",
    "Are you driven by goals or values?",
    "Do you handle criticism well?",
    "Are you more logical or emotional?",
    "Can you stay calm under stress?",
    "Do you prefer planning over spontaneity?",
    "Are you easily distracted?",
    "Are you comfortable with ambiguity?",
    "Are you optimistic by nature?",
    "Do you seek approval from peers?",
    "Are you competitive?",
    "Are you generally patient?",
    "Are you more practical or idealistic?",
    "Do you enjoy mentoring others?",
    "Do you get bored easily with repetition?"
]

aptitude_questions = [
    "Can you solve basic math problems quickly?",
    "Are you good at spotting patterns?",
    "Do you find it easy to understand graphs and charts?",
    "Can you mentally calculate percentages and ratios?",
    "Do you perform well in timed tests?",
    "Can you solve riddles logically?",
    "Are you good at estimating quantities?",
    "Do you enjoy doing mental math?",
    "Can you easily follow algorithmic steps?",
    "Are you good at grammar and sentence construction?",
    "Do you find puzzles fun and engaging?",
    "Can you visualize shapes and objects in 3D?",
    "Are you confident in identifying errors in data?",
    "Do you learn new software tools quickly?",
    "Do you understand programming logic easily?",
    "Can you analyze trends in a dataset?",
    "Do you enjoy solving word problems?",
    "Are you comfortable interpreting tables and figures?",
    "Can you apply formulas to solve real-world problems?",
    "Do you grasp complex instructions easily?"
]

eq_questions = [
    "Can you recognize when you're stressed?",
    "Are you aware of how your emotions affect others?",
    "Can you stay calm in arguments?",
    "Do you empathize with people easily?",
    "Can you handle failure without losing motivation?",
    "Do you take responsibility for your actions?",
    "Do you forgive others easily?",
    "Are you open to feedback?",
    "Do you understand body language well?",
    "Can you manage your anger constructively?",
    "Do you motivate yourself to finish tasks?",
    "Can you resolve conflicts without escalation?",
    "Are you patient when things go wrong?",
    "Do you seek help when needed?",
    "Do you offer help even when not asked?",
    "Are you sensitive to others' needs?",
    "Can you adjust your behavior based on the situation?",
    "Do you maintain relationships easily?",
    "Can you inspire or cheer up others?",
    "Are you able to reflect on your own behavior?"
]

# Standard options for personality-type questions
standard_options = [
    {"content": "Strongly Disagree", "is_correct": False, "score_value": 1},
    {"content": "Disagree", "is_correct": False, "score_value": 2},
    {"content": "Neutral", "is_correct": False, "score_value": 3},
    {"content": "Agree", "is_correct": False, "score_value": 4},
    {"content": "Strongly Agree", "is_correct": False, "score_value": 5}
]

# Connect to the database
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if questions already exist
    cursor.execute("SELECT COUNT(*) FROM question")
    question_count = cursor.fetchone()[0]
    
    if question_count > 0:
        print(f"Database already has {question_count} questions.")
        print("Clearing existing questions...")
        cursor.execute("DELETE FROM question_option")
        cursor.execute("DELETE FROM question")
        conn.commit()
    
    print("Inserting questions...")
    
    # Insert orientation questions
    for question in orientation_questions:
        cursor.execute("INSERT INTO question (category, content) VALUES (?, ?)", ("orientation", question))
        question_id = cursor.lastrowid
        
        # Insert options for this question
        for option in standard_options:
            cursor.execute(
                "INSERT INTO question_option (question_id, content, is_correct, score_value) VALUES (?, ?, ?, ?)",
                (question_id, option["content"], option["is_correct"], option["score_value"])
            )
    
    # Insert interest questions
    for question in interest_questions:
        cursor.execute("INSERT INTO question (category, content) VALUES (?, ?)", ("interest", question))
        question_id = cursor.lastrowid
        
        # Insert options for this question
        for option in standard_options:
            cursor.execute(
                "INSERT INTO question_option (question_id, content, is_correct, score_value) VALUES (?, ?, ?, ?)",
                (question_id, option["content"], option["is_correct"], option["score_value"])
            )
    
    # Insert personality questions
    for question in personality_questions:
        cursor.execute("INSERT INTO question (category, content) VALUES (?, ?)", ("personality", question))
        question_id = cursor.lastrowid
        
        # Insert options for this question
        for option in standard_options:
            cursor.execute(
                "INSERT INTO question_option (question_id, content, is_correct, score_value) VALUES (?, ?, ?, ?)",
                (question_id, option["content"], option["is_correct"], option["score_value"])
            )
    
    # Insert aptitude questions
    for question in aptitude_questions:
        cursor.execute("INSERT INTO question (category, content) VALUES (?, ?)", ("aptitude", question))
        question_id = cursor.lastrowid
        
        # Insert options for this question
        for option in standard_options:
            cursor.execute(
                "INSERT INTO question_option (question_id, content, is_correct, score_value) VALUES (?, ?, ?, ?)",
                (question_id, option["content"], option["is_correct"], option["score_value"])
            )
    
    # Insert EQ questions
    for question in eq_questions:
        cursor.execute("INSERT INTO question (category, content) VALUES (?, ?)", ("eq", question))
        question_id = cursor.lastrowid
        
        # Insert options for this question
        for option in standard_options:
            cursor.execute(
                "INSERT INTO question_option (question_id, content, is_correct, score_value) VALUES (?, ?, ?, ?)",
                (question_id, option["content"], option["is_correct"], option["score_value"])
            )
    
    # Commit changes and close connection
    conn.commit()
    
    # Verify the number of questions inserted
    cursor.execute("SELECT category, COUNT(*) FROM question GROUP BY category")
    category_counts = cursor.fetchall()
    print("Questions inserted by category:")
    for category, count in category_counts:
        print(f"  {category}: {count} questions")
    
    cursor.execute("SELECT COUNT(*) FROM question_option")
    option_count = cursor.fetchone()[0]
    print(f"Total options inserted: {option_count}")
    
    conn.close()
    
    print("Questions inserted successfully!")
except Exception as e:
    print(f"Error inserting questions: {e}") 