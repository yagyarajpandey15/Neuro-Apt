#!/usr/bin/env python
"""
Script to populate example careers for each category in the database.
This adds specific career examples for each category.
"""

from neuroapt.app import create_app, db
from neuroapt.app.models import Career, CareerSkill, CareerEducation, CareerSalary
from datetime import datetime

# Create app context
app = create_app()

# Dictionary mapping career categories to lists of example careers
CAREER_EXAMPLES = {
    "Actuarial Sciences": ["Actuary", "Risk Analyst", "Insurance Underwriter"],
    "Animation & Graphics": ["3D Animator", "Graphic Designer", "Visual Effects Artist"],
    "Architecture": ["Architect", "Interior Designer", "Urban Planner"],
    "Cabin Crew": ["Flight Attendant", "Airline Customer Service Manager", "Ground Staff Supervisor"],
    "Commerce & Accounts": ["Accountant", "Financial Analyst", "Auditor"],
    "Culinary Arts": ["Chef", "Food Critic", "Restaurant Manager"],
    "Defense": ["Military Officer", "Defense Analyst", "Security Consultant"],
    "Distribution & Logistics": ["Supply Chain Manager", "Logistics Coordinator", "Inventory Manager"],
    "Education & Training": ["Teacher", "Educational Consultant", "Corporate Trainer"],
    "Entrepreneurship": ["Startup Founder", "Business Developer", "Venture Capitalist"],
    "Film Making": ["Director", "Cinematographer", "Film Producer"],
    "Food & Agriculture": ["Agricultural Scientist", "Food Technologist", "Farm Manager"],
    "Hotel Management": ["Hotel Manager", "Event Coordinator", "Hospitality Consultant"],
    "Language": ["Translator", "Interpreter", "Language Teacher"],
    "Life Science & Environment": ["Environmental Scientist", "Biologist", "Ecologist"],
    "Marketing & Advertising": ["Marketing Manager", "Brand Strategist", "Social Media Specialist"],
    "Allied Medicine": ["Physiotherapist", "Occupational Therapist", "Dietitian"],
    "Applied Arts": ["Fashion Designer", "Industrial Designer", "Textile Designer"],
    "Aviation": ["Pilot", "Air Traffic Controller", "Aviation Maintenance Technician"],
    "Civil Services": ["Civil Servant", "Government Administrator", "Public Policy Analyst"],
    "Computer Application & IT": ["Software Developer", "IT Project Manager", "System Administrator"],
    "Data Science & Artificial Intelligence": ["Data Scientist", "Machine Learning Engineer", "AI Researcher"],
    "Design": ["UX/UI Designer", "Product Designer", "Web Designer"],
    "Economics": ["Economist", "Economic Researcher", "Policy Analyst"],
    "Engineering": ["Mechanical Engineer", "Civil Engineer", "Electrical Engineer"],
    "Ethical Hacking": ["Ethical Hacker", "Cybersecurity Consultant", "Penetration Tester"],
    "Finance & Banking": ["Investment Banker", "Financial Advisor", "Portfolio Manager"],
    "Geography": ["Geographer", "GIS Specialist", "Cartographer"],
    "International Relations": ["Diplomat", "Foreign Affairs Analyst", "NGO Program Manager"],
    "Law": ["Lawyer", "Legal Consultant", "Corporate Counsel"],
    "Management": ["Business Manager", "Operations Director", "Management Consultant"],
    "Maths & Statistics": ["Statistician", "Mathematician", "Data Analyst"]
}

def populate_career_examples():
    """Add example careers for each category to the database."""
    print("Starting to populate example careers...")
    
    with app.app_context():
        # Track careers added and skipped
        careers_added = 0
        careers_skipped = 0
        
        for category, examples in CAREER_EXAMPLES.items():
            print(f"\nProcessing category: {category}")
            
            for career_title in examples:
                # Check if career already exists
                existing_career = Career.query.filter_by(title=career_title).first()
                
                if existing_career:
                    print(f"  - Career already exists: {career_title}")
                    careers_skipped += 1
                    continue
                
                # Create a new career entry
                career = Career(
                    title=career_title,
                    category=category,
                    description=f"{career_title} is a professional career in the {category} field. "
                                f"This is a placeholder description that would typically contain details "
                                f"about the nature of work, responsibilities, and growth opportunities.",
                    work_environment="Work environments vary but typically include office settings, remote work options, "
                                    "and field work depending on specialization.",
                    job_outlook="The job outlook is generally positive with growth opportunities in specialized areas."
                )
                
                db.session.add(career)
                db.session.flush()  # Get the ID without committing
                
                # Add some sample skills
                skills = [
                    CareerSkill(
                        career_id=career.id,
                        name=f"Technical {category} Knowledge",
                        description=f"Specialized knowledge related to {category}"
                    ),
                    CareerSkill(
                        career_id=career.id,
                        name="Communication",
                        description="Effective verbal and written communication skills"
                    ),
                    CareerSkill(
                        career_id=career.id,
                        name="Problem Solving",
                        description="Analytical thinking and creative problem-solving abilities"
                    )
                ]
                
                for skill in skills:
                    db.session.add(skill)
                
                # Add education requirements
                education = CareerEducation(
                    career_id=career.id,
                    level="Bachelor's Degree",
                    field=category,
                    description=f"A degree in {category} or related field is typically required."
                )
                db.session.add(education)
                
                # Add salary information
                salary = CareerSalary(
                    career_id=career.id,
                    entry_level="$40,000 - $60,000",
                    mid_level="$60,000 - $90,000",
                    senior_level="$90,000 - $120,000+",
                    currency="USD"
                )
                db.session.add(salary)
                
                careers_added += 1
                print(f"  + Added career: {career_title}")
        
        # Commit all changes
        db.session.commit()
        
        print(f"\nSummary:")
        print(f"- Careers added: {careers_added}")
        print(f"- Careers skipped (already exist): {careers_skipped}")
        print(f"- Total careers processed: {sum(len(examples) for examples in CAREER_EXAMPLES.values())}")

if __name__ == "__main__":
    populate_career_examples() 