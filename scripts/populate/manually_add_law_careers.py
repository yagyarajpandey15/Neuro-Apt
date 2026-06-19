from neuroapt.app import create_app, db
from neuroapt.app.models import Career, CareerSkill, CareerEducation, CareerSalary
from datetime import datetime

# Create sample law careers data
law_careers = [
    {
        "title": "Corporate Lawyer",
        "category": "Law",
        "description": "Corporate lawyers advise businesses on legal matters related to corporate law, contracts, mergers, acquisitions, and regulatory compliance. They ensure business activities comply with relevant laws and regulations, draft and review legal documents, and represent companies in legal proceedings.",
        "work_environment": "Corporate lawyers typically work in law firms, corporate legal departments, or as independent consultants. Work environments are usually formal office settings with regular business hours, though extended hours are common when preparing for transactions or during litigation.",
        "job_outlook": "The job outlook for corporate lawyers remains steady, with growth expected in areas of regulatory compliance, intellectual property, healthcare, and international business law. Demand fluctuates with economic conditions, with increased activity during economic growth.",
        "skills": [
            {"name": "Legal Research", "description": "Ability to research complex legal issues and precedents"},
            {"name": "Contract Drafting", "description": "Expert skill in drafting and reviewing legal contracts"},
            {"name": "Negotiation", "description": "Strong negotiation skills for deals and settlements"},
            {"name": "Regulatory Knowledge", "description": "Understanding of corporate regulations and compliance requirements"}
        ],
        "education": [
            {"level": "Juris Doctor (J.D.)", "field": "Law", "description": "Required legal education from an accredited law school"},
            {"level": "Bachelor's Degree", "field": "Business, Economics, or related field", "description": "Foundation in business principles helpful for corporate law practice"},
            {"level": "Master of Laws (LL.M.)", "field": "Corporate Law, Securities Regulation, or similar", "description": "Optional advanced specialization"}
        ],
        "salary": {
            "entry_level": "$80,000-$130,000",
            "mid_level": "$130,000-$200,000",
            "senior_level": "$200,000-$400,000+",
            "currency": "USD"
        }
    },
    {
        "title": "Criminal Defense Attorney",
        "category": "Law",
        "description": "Criminal defense attorneys represent individuals accused of crimes, protecting their rights throughout the legal process. They build defense strategies, investigate cases, challenge evidence, negotiate plea bargains, and advocate for clients in court trials.",
        "work_environment": "Criminal defense attorneys work in private practices, public defender offices, or legal aid organizations. The environment can be high-pressure with irregular hours, court appearances, and prison visits to meet with clients.",
        "job_outlook": "Employment for criminal defense attorneys remains stable, though public defender positions often face resource constraints. Career opportunities exist in both public and private sectors, with experienced attorneys establishing their own practices.",
        "skills": [
            {"name": "Trial Advocacy", "description": "Strong courtroom presentation and argumentation skills"},
            {"name": "Case Strategy", "description": "Ability to develop effective defense strategies"},
            {"name": "Evidence Analysis", "description": "Critical evaluation of evidence and identification of weaknesses"},
            {"name": "Client Management", "description": "Strong interpersonal skills and ability to work with diverse clients"}
        ],
        "education": [
            {"level": "Juris Doctor (J.D.)", "field": "Law", "description": "Required legal education with focus on criminal law courses"},
            {"level": "Bachelor's Degree", "field": "Any field, often Criminal Justice or Political Science", "description": "Foundation for legal education"},
            {"level": "Continuing Legal Education", "field": "Criminal Law", "description": "Ongoing education in criminal defense tactics and law changes"}
        ],
        "salary": {
            "entry_level": "$50,000-$80,000",
            "mid_level": "$80,000-$150,000",
            "senior_level": "$150,000-$300,000+",
            "currency": "USD"
        }
    },
    {
        "title": "Immigration Lawyer",
        "category": "Law",
        "description": "Immigration lawyers help individuals, families, and businesses navigate the complex immigration legal system. They assist with visa applications, green cards, citizenship processes, asylum claims, deportation defense, and compliance with immigration regulations.",
        "work_environment": "Immigration lawyers work in private practices, non-profit organizations, government agencies, or corporate legal departments. The work setting varies from offices to courtrooms, with some travel required for client meetings or immigration hearings.",
        "job_outlook": "Demand for immigration lawyers remains strong due to ongoing policy changes and the complexity of immigration law. Career growth is expected as global mobility increases and immigration policies continue to evolve.",
        "skills": [
            {"name": "Immigration Law Expertise", "description": "Deep understanding of immigration statutes, regulations, and policies"},
            {"name": "Document Preparation", "description": "Meticulous attention to detail in preparing applications and petitions"},
            {"name": "Cultural Sensitivity", "description": "Ability to work with diverse clients from varied cultural backgrounds"},
            {"name": "Language Skills", "description": "Proficiency in multiple languages is highly valued"}
        ],
        "education": [
            {"level": "Juris Doctor (J.D.)", "field": "Law", "description": "Required legal education with focus on immigration law"},
            {"level": "Bachelor's Degree", "field": "Any field, often International Relations or Political Science", "description": "Foundation for legal education"},
            {"level": "Certificate Programs", "field": "Immigration Law", "description": "Specialized training in immigration procedures and regulations"}
        ],
        "salary": {
            "entry_level": "$60,000-$90,000",
            "mid_level": "$90,000-$140,000",
            "senior_level": "$140,000-$250,000+",
            "currency": "USD"
        }
    }
]

def main():
    app = create_app()
    with app.app_context():
        print("Adding law careers to database...")
        
        for career_data in law_careers:
            # Check if career already exists
            existing_career = Career.query.filter_by(title=career_data["title"]).first()
            
            if existing_career:
                print(f"Career '{career_data['title']}' already exists, updating...")
                career = existing_career
            else:
                print(f"Creating new career: {career_data['title']}")
                career = Career(
                    title=career_data["title"],
                    category=career_data["category"],
                    description=career_data["description"],
                    work_environment=career_data["work_environment"],
                    job_outlook=career_data["job_outlook"],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.session.add(career)
                db.session.commit()  # Commit to get the career ID
                
            # Clear existing related data to avoid duplicates
            if existing_career:
                # Delete existing skills
                CareerSkill.query.filter_by(career_id=career.id).delete()
                
                # Delete existing education paths
                CareerEducation.query.filter_by(career_id=career.id).delete()
                
                # Delete existing salary information
                CareerSalary.query.filter_by(career_id=career.id).delete()
            
            # Add skills
            for skill_data in career_data["skills"]:
                skill = CareerSkill(
                    career_id=career.id,
                    name=skill_data["name"],
                    description=skill_data["description"]
                )
                db.session.add(skill)
            
            # Add education paths
            for edu_data in career_data["education"]:
                education = CareerEducation(
                    career_id=career.id,
                    level=edu_data["level"],
                    field=edu_data["field"],
                    description=edu_data["description"]
                )
                db.session.add(education)
            
            # Add salary information
            salary = CareerSalary(
                career_id=career.id,
                entry_level=career_data["salary"]["entry_level"],
                mid_level=career_data["salary"]["mid_level"],
                senior_level=career_data["salary"]["senior_level"],
                currency=career_data["salary"]["currency"]
            )
            db.session.add(salary)
            
            # Save all changes
            db.session.commit()
            
        print(f"Successfully added {len(law_careers)} law careers to the database!")

if __name__ == "__main__":
    main() 