"""
Seed script to create 10 realistic test results for Indian students
"""
import sys
import os
from datetime import datetime, timedelta
import random

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from neuroapt.app import create_app, db, bcrypt
from neuroapt.app.models import User, TestResult

def seed_test_results():
    """Create 10 test results with realistic student profiles"""
    
    app = create_app()
    
    with app.app_context():
        print("Starting test results seed...")
        
        # Student profiles with realistic data
        students = [
            {
                'name': 'Aarav Sharma',
                'age': 17,
                'email': 'aarav.sharma@student.neuroapt.com',
                'total_score': 423,
                'aptitude_score': 88,
                'verbal_score': 78,
                'numerical_score': 92,
                'abstract_score': 89,  # Using abstract_score instead of logical_score
                'orientation_score': 85,
                'interest_score': 84,
                'personality_score': 74,
                'eq_score': 68,
                'work_style_score': 79,
                # Interest categories (using stem_tech_score for interest_stem)
                'stem_tech_score': 91,
                'creative_media_score': 32,
                'business_management_score': 45,
                'people_oriented_score': 38,
                'legal_governance_score': 29,
                'logistics_distribution_score': 25,
                # Personality traits
                'openness_score': 75,
                'conscientiousness_score': 82,
                'extraversion_score': 65,
                'agreeableness_score': 70,
                'neuroticism_score': 45,
                # Work attributes
                'leadership_score': 78,
                'teamwork_score': 72,
                'creativity_score': 68,
                'analytical_score': 92,
                'communication_score': 74,
                'adaptability_score': 76,
                # AI fields
                'answer_pattern_flag': 'DECISIVE',
                'confidence_level': 'HIGH',
                'contradictions_detected': '[]',
                'interest_intersection': None,
                'ai_analysis': None,
            },
            {
                'name': 'Priya Nair',
                'age': 18,
                'email': 'priya.nair@student.neuroapt.com',
                'total_score': 387,
                'aptitude_score': 72,
                'verbal_score': 81,
                'numerical_score': 61,
                'abstract_score': 69,
                'orientation_score': 78,
                'interest_score': 82,
                'personality_score': 85,
                'eq_score': 89,
                'work_style_score': 67,
                # Interest categories
                'stem_tech_score': 58,
                'creative_media_score': 88,
                'business_management_score': 41,
                'people_oriented_score': 76,
                'legal_governance_score': 33,
                'logistics_distribution_score': 28,
                # Personality traits
                'openness_score': 91,
                'conscientiousness_score': 78,
                'extraversion_score': 82,
                'agreeableness_score': 88,
                'neuroticism_score': 38,
                # Work attributes
                'leadership_score': 65,
                'teamwork_score': 85,
                'creativity_score': 93,
                'analytical_score': 64,
                'communication_score': 87,
                'adaptability_score': 79,
                # AI fields
                'answer_pattern_flag': 'DECISIVE',
                'confidence_level': 'HIGH',
                'contradictions_detected': '[]',
                'interest_intersection': 'Creative+People-Oriented',
                'ai_analysis': None,
            },
            {
                'name': 'Rohan Mehta',
                'age': 17,
                'email': 'rohan.mehta@student.neuroapt.com',
                'total_score': 441,
                'aptitude_score': 84,
                'verbal_score': 85,
                'numerical_score': 87,
                'abstract_score': 82,
                'orientation_score': 88,
                'interest_score': 86,
                'personality_score': 88,
                'eq_score': 77,
                'work_style_score': 91,
                # Interest categories
                'stem_tech_score': 62,
                'creative_media_score': 28,
                'business_management_score': 93,
                'people_oriented_score': 55,
                'legal_governance_score': 21,
                'logistics_distribution_score': 45,
                # Personality traits
                'openness_score': 84,
                'conscientiousness_score': 93,
                'extraversion_score': 88,
                'agreeableness_score': 72,
                'neuroticism_score': 32,
                # Work attributes
                'leadership_score': 94,
                'teamwork_score': 81,
                'creativity_score': 75,
                'analytical_score': 89,
                'communication_score': 90,
                'adaptability_score': 88,
                # AI fields
                'answer_pattern_flag': 'DECISIVE',
                'confidence_level': 'HIGH',
                'contradictions_detected': '[]',
                'interest_intersection': None,
                'ai_analysis': None,
            },
            {
                'name': 'Sneha Gupta',
                'age': 16,
                'email': 'sneha.gupta@student.neuroapt.com',
                'total_score': 412,
                'aptitude_score': 81,
                'verbal_score': 77,
                'numerical_score': 84,
                'abstract_score': 78,
                'orientation_score': 82,
                'interest_score': 85,
                'personality_score': 76,
                'eq_score': 91,
                'work_style_score': 70,
                # Interest categories (using people_oriented_score for interest_social, no direct healthcare score)
                'stem_tech_score': 79,
                'creative_media_score': 35,
                'business_management_score': 29,
                'people_oriented_score': 72,
                'legal_governance_score': 42,
                'logistics_distribution_score': 22,
                # Personality traits
                'openness_score': 73,
                'conscientiousness_score': 88,
                'extraversion_score': 68,
                'agreeableness_score': 92,
                'neuroticism_score': 41,
                # Work attributes
                'leadership_score': 71,
                'teamwork_score': 88,
                'creativity_score': 62,
                'analytical_score': 82,
                'communication_score': 89,
                'adaptability_score': 74,
                # AI fields
                'answer_pattern_flag': 'DECISIVE',
                'confidence_level': 'HIGH',
                'contradictions_detected': '[]',
                'interest_intersection': None,
                'ai_analysis': None,
            },
            {
                'name': 'Karan Joshi',
                'age': 18,
                'email': 'karan.joshi@student.neuroapt.com',
                'total_score': 361,
                'aptitude_score': 63,
                'verbal_score': 74,
                'numerical_score': 58,
                'abstract_score': 62,
                'orientation_score': 68,
                'interest_score': 69,
                'personality_score': 69,
                'eq_score': 72,
                'work_style_score': 61,
                # Interest categories
                'stem_tech_score': 44,
                'creative_media_score': 71,
                'business_management_score': 68,
                'people_oriented_score': 59,
                'legal_governance_score': 38,
                'logistics_distribution_score': 35,
                # Personality traits
                'openness_score': 68,
                'conscientiousness_score': 62,
                'extraversion_score': 71,
                'agreeableness_score': 67,
                'neuroticism_score': 58,
                # Work attributes
                'leadership_score': 61,
                'teamwork_score': 70,
                'creativity_score': 74,
                'analytical_score': 59,
                'communication_score': 72,
                'adaptability_score': 65,
                # AI fields
                'answer_pattern_flag': 'AMBIVALENT',
                'confidence_level': 'MODERATE',
                'contradictions_detected': '[]',
                'interest_intersection': None,
                'ai_analysis': None,
            },
            {
                'name': 'Divya Krishnan',
                'age': 17,
                'email': 'divya.krishnan@student.neuroapt.com',
                'total_score': 457,
                'aptitude_score': 90,
                'verbal_score': 80,
                'numerical_score': 94,
                'abstract_score': 91,
                'orientation_score': 89,
                'interest_score': 88,
                'personality_score': 71,
                'eq_score': 65,
                'work_style_score': 83,
                # Interest categories
                'stem_tech_score': 87,
                'creative_media_score': 82,
                'business_management_score': 38,
                'people_oriented_score': 41,
                'legal_governance_score': 27,
                'logistics_distribution_score': 30,
                # Personality traits
                'openness_score': 92,
                'conscientiousness_score': 79,
                'extraversion_score': 58,
                'agreeableness_score': 64,
                'neuroticism_score': 42,
                # Work attributes
                'leadership_score': 68,
                'teamwork_score': 72,
                'creativity_score': 91,
                'analytical_score': 93,
                'communication_score': 70,
                'adaptability_score': 85,
                # AI fields
                'answer_pattern_flag': 'DECISIVE',
                'confidence_level': 'HIGH',
                'contradictions_detected': '[]',
                'interest_intersection': 'STEM+Creative',
                'ai_analysis': None,
            },
            {
                'name': 'Arjun Patel',
                'age': 18,
                'email': 'arjun.patel@student.neuroapt.com',
                'total_score': 378,
                'aptitude_score': 70,
                'verbal_score': 82,
                'numerical_score': 63,
                'abstract_score': 67,
                'orientation_score': 76,
                'interest_score': 81,
                'personality_score': 91,
                'eq_score': 94,
                'work_style_score': 68,
                # Interest categories
                'stem_tech_score': 41,
                'creative_media_score': 49,
                'business_management_score': 33,
                'people_oriented_score': 89,
                'legal_governance_score': 52,
                'logistics_distribution_score': 25,
                # Personality traits
                'openness_score': 81,
                'conscientiousness_score': 76,
                'extraversion_score': 85,
                'agreeableness_score': 95,
                'neuroticism_score': 35,
                # Work attributes
                'leadership_score': 72,
                'teamwork_score': 93,
                'creativity_score': 68,
                'analytical_score': 71,
                'communication_score': 94,
                'adaptability_score': 82,
                # AI fields
                'answer_pattern_flag': 'DECISIVE',
                'confidence_level': 'HIGH',
                'contradictions_detected': '[]',
                'interest_intersection': 'Business+People-Oriented',
                'ai_analysis': None,
            },
            {
                'name': 'Ishaan Verma',
                'age': 17,
                'email': 'ishaan.verma@student.neuroapt.com',
                'total_score': 354,
                'aptitude_score': 58,
                'verbal_score': 69,
                'numerical_score': 61,
                'abstract_score': 57,
                'orientation_score': 62,
                'interest_score': 63,
                'personality_score': 61,
                'eq_score': 58,
                'work_style_score': 54,
                # Interest categories
                'stem_tech_score': 55,
                'creative_media_score': 52,
                'business_management_score': 61,
                'people_oriented_score': 58,
                'legal_governance_score': 49,
                'logistics_distribution_score': 51,
                # Personality traits
                'openness_score': 59,
                'conscientiousness_score': 55,
                'extraversion_score': 62,
                'agreeableness_score': 64,
                'neuroticism_score': 68,
                # Work attributes
                'leadership_score': 57,
                'teamwork_score': 63,
                'creativity_score': 59,
                'analytical_score': 56,
                'communication_score': 61,
                'adaptability_score': 58,
                # AI fields
                'answer_pattern_flag': 'AMBIVALENT',
                'confidence_level': 'LOW',
                'contradictions_detected': '[]',
                'interest_intersection': None,
                'ai_analysis': None,
            },
            {
                'name': 'Ananya Singh',
                'age': 18,
                'email': 'ananya.singh@student.neuroapt.com',
                'total_score': 468,
                'aptitude_score': 93,
                'verbal_score': 88,
                'numerical_score': 96,
                'abstract_score': 94,
                'orientation_score': 92,
                'interest_score': 89,
                'personality_score': 67,
                'eq_score': 62,
                'work_style_score': 85,
                # Interest categories
                'stem_tech_score': 95,
                'creative_media_score': 31,
                'business_management_score': 28,
                'people_oriented_score': 44,
                'legal_governance_score': 38,
                'logistics_distribution_score': 24,
                # Personality traits
                'openness_score': 96,
                'conscientiousness_score': 88,
                'extraversion_score': 48,
                'agreeableness_score': 61,
                'neuroticism_score': 39,
                # Work attributes
                'leadership_score': 71,
                'teamwork_score': 68,
                'creativity_score': 79,
                'analytical_score': 97,
                'communication_score': 65,
                'adaptability_score': 81,
                # AI fields
                'answer_pattern_flag': 'DECISIVE',
                'confidence_level': 'HIGH',
                'contradictions_detected': '[]',
                'interest_intersection': None,
                'ai_analysis': None,
            },
            {
                'name': 'Meera Iyer',
                'age': 17,
                'email': 'meera.iyer@student.neuroapt.com',
                'total_score': 396,
                'aptitude_score': 75,
                'verbal_score': 79,
                'numerical_score': 71,
                'abstract_score': 68,
                'orientation_score': 79,
                'interest_score': 83,
                'personality_score': 83,
                'eq_score': 86,
                'work_style_score': 74,
                # Interest categories
                'stem_tech_score': 37,
                'creative_media_score': 54,
                'business_management_score': 84,
                'people_oriented_score': 81,
                'legal_governance_score': 42,
                'logistics_distribution_score': 38,
                # Personality traits
                'openness_score': 78,
                'conscientiousness_score': 82,
                'extraversion_score': 87,
                'agreeableness_score': 85,
                'neuroticism_score': 36,
                # Work attributes
                'leadership_score': 80,
                'teamwork_score': 88,
                'creativity_score': 73,
                'analytical_score': 72,
                'communication_score': 91,
                'adaptability_score': 79,
                # AI fields
                'answer_pattern_flag': 'DECISIVE',
                'confidence_level': 'MODERATE',
                'contradictions_detected': '[]',
                'interest_intersection': 'Business+People-Oriented',
                'ai_analysis': None,
            },
        ]
        
        # Create or find users and their test results
        created_count = 0
        for student_data in students:
            # Check if user exists
            user = User.query.filter_by(email=student_data['email']).first()
            
            if not user:
                # Create new user
                username = student_data['name'].lower().replace(' ', '_')
                hashed_password = bcrypt.generate_password_hash('password123').decode('utf-8')
                
                user = User(
                    username=username,
                    email=student_data['email'],
                    password=hashed_password,
                    is_admin=False
                )
                db.session.add(user)
                db.session.flush()  # Get user ID
                print(f"Created user: {student_data['name']} ({student_data['email']})")
            else:
                print(f"Found existing user: {student_data['name']} ({student_data['email']})")
            
            # Check if test result already exists for this user
            existing_result = TestResult.query.filter_by(user_id=user.id).first()
            if existing_result:
                print(f"  Test result already exists for {student_data['name']}, skipping...")
                continue
            
            # Create test result with random completion date in last 30 days
            days_ago = random.randint(1, 30)
            test_date = datetime.utcnow() - timedelta(days=days_ago)
            
            # Create test result with all fields from student profile
            test_result = TestResult(
                user_id=user.id,
                test_date=test_date,
                total_score=student_data['total_score'],
                aptitude_score=student_data['aptitude_score'],
                verbal_score=student_data['verbal_score'],
                numerical_score=student_data['numerical_score'],
                abstract_score=student_data['abstract_score'],
                orientation_score=student_data['orientation_score'],
                interest_score=student_data['interest_score'],
                personality_score=student_data['personality_score'],
                eq_score=student_data['eq_score'],
                work_style_score=student_data['work_style_score'],
                # Interest categories
                stem_tech_score=student_data['stem_tech_score'],
                creative_media_score=student_data['creative_media_score'],
                business_management_score=student_data['business_management_score'],
                people_oriented_score=student_data['people_oriented_score'],
                legal_governance_score=student_data['legal_governance_score'],
                logistics_distribution_score=student_data['logistics_distribution_score'],
                # Personality traits
                openness_score=student_data['openness_score'],
                conscientiousness_score=student_data['conscientiousness_score'],
                extraversion_score=student_data['extraversion_score'],
                agreeableness_score=student_data['agreeableness_score'],
                neuroticism_score=student_data['neuroticism_score'],
                # Work attributes
                leadership_score=student_data['leadership_score'],
                teamwork_score=student_data['teamwork_score'],
                creativity_score=student_data['creativity_score'],
                analytical_score=student_data['analytical_score'],
                communication_score=student_data['communication_score'],
                adaptability_score=student_data['adaptability_score'],
                # AI fields
                answer_pattern_flag=student_data['answer_pattern_flag'],
                confidence_level=student_data['confidence_level'],
                contradictions_detected=student_data['contradictions_detected'],
                interest_intersection=student_data['interest_intersection'],
                ai_analysis=student_data['ai_analysis']
            )
            
            db.session.add(test_result)
            created_count += 1
            print(f"  Created test result for {student_data['name']} (Score: {student_data['total_score']}/500)")
        
        # Commit all changes
        db.session.commit()
        print(f"\n✓ Successfully seeded {created_count} test results!")
        return created_count


if __name__ == "__main__":
    seed_test_results()
    print("10 test results seeded successfully")
