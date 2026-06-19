#!/usr/bin/env python
"""
Script to populate the career categories in the database.
This will add basic career entries for all the categories.
"""

from neuroapt.app import create_app, db
from neuroapt.app.models import Career
from datetime import datetime

# Create app context
app = create_app()

# List of career categories
CAREER_CATEGORIES = [
    "Actuarial Sciences",
    "Animation & Graphics",
    "Architecture",
    "Cabin Crew",
    "Commerce & Accounts",
    "Culinary Arts",
    "Defense",
    "Distribution & Logistics",
    "Education & Training",
    "Entrepreneurship",
    "Film Making",
    "Food & Agriculture",
    "Hotel Management",
    "Language",
    "Life Science & Environment",
    "Marketing & Advertising",
    "Allied Medicine",
    "Applied Arts",
    "Aviation",
    "Civil Services",
    "Computer Application & IT",
    "Data Science & Artificial Intelligence",
    "Design",
    "Economics",
    "Engineering",
    "Ethical Hacking",
    "Finance & Banking",
    "Geography",
    "International Relations",
    "Law",
    "Management",
    "Maths & Statistics"
]

def populate_career_categories():
    """Add career categories to the database."""
    print("Starting to populate career categories...")
    
    with app.app_context():
        # First, check which categories already exist
        existing_categories = set()
        for career in Career.query.all():
            existing_categories.add(career.category)
        
        categories_added = 0
        categories_skipped = 0
        
        for category in CAREER_CATEGORIES:
            if category in existing_categories:
                print(f"Category already exists: {category}")
                categories_skipped += 1
                continue
            
            # Create a placeholder career for this category
            career = Career(
                title=f"{category} Career",
                category=category,
                description=f"This is a placeholder for careers in the {category} field. More detailed information will be added later.",
                work_environment="Various work environments depending on specific roles.",
                job_outlook="Varies by specific role and market conditions.",
                created_at=datetime.utcnow()
            )
            
            db.session.add(career)
            categories_added += 1
            print(f"Added category: {category}")
        
        # Commit changes
        db.session.commit()
        
        print(f"\nSummary:")
        print(f"- Categories added: {categories_added}")
        print(f"- Categories skipped (already exist): {categories_skipped}")
        print(f"- Total categories processed: {len(CAREER_CATEGORIES)}")

if __name__ == "__main__":
    populate_career_categories() 