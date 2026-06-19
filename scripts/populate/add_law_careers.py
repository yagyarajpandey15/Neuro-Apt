import sqlite3
import os
from datetime import datetime

# Path to the SQLite database
db_path = os.path.join('neuroapt', 'app', 'neuroapt.db')

# Sample law careers data
law_careers = [
    {
        "title": "Corporate Lawyer",
        "category": "Law",
        "description": "Corporate lawyers advise businesses on legal matters related to corporate law, contracts, mergers, acquisitions, and regulatory compliance. They ensure business activities comply with relevant laws and regulations, draft and review legal documents, and represent companies in legal proceedings.",
        "work_environment": "Corporate lawyers typically work in law firms, corporate legal departments, or as independent consultants. Work environments are usually formal office settings with regular business hours, though extended hours are common when preparing for transactions or during litigation.",
        "job_outlook": "The job outlook for corporate lawyers remains steady, with growth expected in areas of regulatory compliance, intellectual property, healthcare, and international business law. Demand fluctuates with economic conditions, with increased activity during economic growth."
    },
    {
        "title": "Criminal Defense Attorney",
        "category": "Law",
        "description": "Criminal defense attorneys represent individuals accused of crimes, protecting their rights throughout the legal process. They build defense strategies, investigate cases, challenge evidence, negotiate plea bargains, and advocate for clients in court trials.",
        "work_environment": "Criminal defense attorneys work in private practices, public defender offices, or legal aid organizations. The environment can be high-pressure with irregular hours, court appearances, and prison visits to meet with clients.",
        "job_outlook": "Employment for criminal defense attorneys remains stable, though public defender positions often face resource constraints. Career opportunities exist in both public and private sectors, with experienced attorneys establishing their own practices."
    },
    {
        "title": "Immigration Lawyer",
        "category": "Law",
        "description": "Immigration lawyers help individuals, families, and businesses navigate the complex immigration legal system. They assist with visa applications, green cards, citizenship processes, asylum claims, deportation defense, and compliance with immigration regulations.",
        "work_environment": "Immigration lawyers work in private practices, non-profit organizations, government agencies, or corporate legal departments. The work setting varies from offices to courtrooms, with some travel required for client meetings or immigration hearings.",
        "job_outlook": "Demand for immigration lawyers remains strong due to ongoing policy changes and the complexity of immigration law. Career growth is expected as global mobility increases and immigration policies continue to evolve."
    },
    {
        "title": "Intellectual Property Attorney",
        "category": "Law",
        "description": "Intellectual property attorneys specialize in legal matters related to creative works, inventions, and brand identity. They help clients secure patents, trademarks, and copyrights, and represent clients in IP litigation.",
        "work_environment": "IP attorneys work in law firms, corporate legal departments, and government agencies. The work environment typically involves office settings with client meetings and occasional court appearances.",
        "job_outlook": "The demand for IP attorneys continues to grow as innovation and digital content creation accelerate. Opportunities are particularly strong in technology, entertainment, and pharmaceutical sectors."
    },
    {
        "title": "Environmental Lawyer",
        "category": "Law",
        "description": "Environmental lawyers focus on legal issues related to environmental regulations, compliance, and litigation. They represent clients in matters involving pollution, land use, natural resources, and sustainability.",
        "work_environment": "Environmental lawyers work in law firms, government agencies, non-profit organizations, and corporate legal departments. Work may involve both office settings and field visits to affected sites.",
        "job_outlook": "As environmental concerns remain a global priority, demand for environmental lawyers is expected to grow. Opportunities exist in regulatory compliance, renewable energy, and climate change policy."
    }
]

def main():
    print(f"Database path: {os.path.abspath(db_path)}")
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        exit(1)
    
    # Connect to the database
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Adding law careers to database...")
        for career in law_careers:
            # Check if career already exists
            cursor.execute("SELECT id FROM career WHERE title = ?", (career["title"],))
            existing = cursor.fetchone()
            
            current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            
            if existing:
                # Update existing career
                cursor.execute("""
                UPDATE career 
                SET category = ?, description = ?, work_environment = ?, job_outlook = ?, updated_at = ?
                WHERE title = ?
                """, (
                    career["category"], 
                    career["description"], 
                    career["work_environment"],
                    career["job_outlook"],
                    current_time,
                    career["title"]
                ))
                print(f"Updated existing career: {career['title']}")
            else:
                # Insert new career
                cursor.execute("""
                INSERT INTO career (title, category, description, work_environment, job_outlook, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    career["title"],
                    career["category"],
                    career["description"],
                    career["work_environment"],
                    career["job_outlook"],
                    current_time,
                    current_time
                ))
                print(f"Added new career: {career['title']}")
        
        # Commit changes
        conn.commit()
        print(f"Successfully added {len(law_careers)} law careers to the database!")
        
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main() 