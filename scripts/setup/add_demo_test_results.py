#!/usr/bin/env python
"""
Add Demo Test Results
Creates realistic demo test result data for testing the AI-powered features
"""

import os
import sys
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from neuroapt.app import create_app, db
from neuroapt.app.models import User, TestResult
import json

def create_demo_results():
    """Create 3 demo test results with different profiles"""
    
    app = create_app()
    with app.app_context():
        # Get or create admin user
        admin_user = User.query.filter_by(email='admin@neuroapt.com').first()
        if not admin_user:
            print("Error: Admin user not found. Please create admin user first.")
            return False
        
        # Check if demo results already exist
        existing = TestResult.query.filter_by(user_id=admin_user.id).all()
        if len(existing) >= 3:
            print(f"Demo results already exist ({len(existing)} results found).")
            print("Delete existing results if you want to regenerate.")
            return True
        
        print(f"Creating demo test results for user: {admin_user.email}")
        
        # Demo Result 1: STEM/Tech-Oriented Student
        demo1 = TestResult(
            user_id=admin_user.id,
            test_date=datetime.utcnow() - timedelta(days=30),
            
            # Section scores
            orientation_score=85,
            interest_score=88,
            personality_score=75,
            aptitude_score=90,
            eq_score=70,
            work_style_score=80,
            total_score=488,
            
            # Personality traits (Big Five)
            openness_score=35,  # High - curious, creative
            conscientiousness_score=30,  # Moderate - organized
            extraversion_score=20,  # Low - introverted
            agreeableness_score=25,  # Moderate
            neuroticism_score=15,  # Low - stable
            
            # Work attributes
            leadership_score=25,
            teamwork_score=30,
            creativity_score=32,
            analytical_score=38,  # Strong analytical
            communication_score=28,
            adaptability_score=30,
            
            # Aptitude breakdown
            verbal_score=28,
            numerical_score=35,  # Strong math
            abstract_score=32,  # Strong logical reasoning
            
            # Interest categories
            stem_tech_score=40,  # Highest interest
            creative_media_score=25,
            people_oriented_score=15,
            business_management_score=20,
            legal_governance_score=10,
            logistics_distribution_score=12,
            
            # AI metadata
            confidence_level="HIGH",
            answer_pattern_flag="decisive",
            interest_intersection="STEM+Creative"
        )
        
        # Demo Result 2: Creative/People-Oriented Student
        demo2 = TestResult(
            user_id=admin_user.id,
            test_date=datetime.utcnow() - timedelta(days=15),
            
            # Section scores
            orientation_score=78,
            interest_score=85,
            personality_score=88,
            aptitude_score=72,
            eq_score=92,  # High emotional intelligence
            work_style_score=85,
            total_score=500,
            
            # Personality traits (Big Five)
            openness_score=38,  # Very high - creative
            conscientiousness_score=28,
            extraversion_score=35,  # High - extroverted
            agreeableness_score=36,  # High - empathetic
            neuroticism_score=20,
            
            # Work attributes
            leadership_score=32,
            teamwork_score=38,  # Strong teamwork
            creativity_score=40,  # Very creative
            analytical_score=25,
            communication_score=38,  # Strong communication
            adaptability_score=35,
            
            # Aptitude breakdown
            verbal_score=32,  # Good verbal
            numerical_score=22,
            abstract_score=25,
            
            # Interest categories
            stem_tech_score=18,
            creative_media_score=38,  # Highest interest
            people_oriented_score=40,  # Highest interest
            business_management_score=25,
            legal_governance_score=15,
            logistics_distribution_score=8,
            
            # AI metadata
            confidence_level="HIGH",
            answer_pattern_flag="decisive",
            interest_intersection="Creative+People"
        )
        
        # Demo Result 3: Business/Management-Oriented Student
        demo3 = TestResult(
            user_id=admin_user.id,
            test_date=datetime.utcnow() - timedelta(days=2),
            
            # Section scores
            orientation_score=82,
            interest_score=80,
            personality_score=85,
            aptitude_score=78,
            eq_score=85,
            work_style_score=88,
            total_score=498,
            
            # Personality traits (Big Five)
            openness_score=30,
            conscientiousness_score=36,  # Very organized
            extraversion_score=32,  # Moderately extroverted
            agreeableness_score=28,
            neuroticism_score=12,  # Very stable
            
            # Work attributes
            leadership_score=38,  # Strong leader
            teamwork_score=35,
            creativity_score=28,
            analytical_score=32,
            communication_score=36,  # Good communicator
            adaptability_score=38,  # Very adaptable
            
            # Aptitude breakdown
            verbal_score=30,
            numerical_score=30,  # Balanced
            abstract_score=28,
            
            # Interest categories
            stem_tech_score=25,
            creative_media_score=20,
            people_oriented_score=30,
            business_management_score=42,  # Highest interest
            legal_governance_score=25,
            logistics_distribution_score=20,
            
            # AI metadata
            confidence_level="HIGH",
            answer_pattern_flag="decisive",
            interest_intersection="Business+People"
        )
        
        # Add to database
        try:
            db.session.add(demo1)
            db.session.add(demo2)
            db.session.add(demo3)
            db.session.commit()
            
            print("\n✅ Successfully created 3 demo test results:")
            print(f"\n1. STEM/Tech Profile (ID: {demo1.id})")
            print(f"   - Date: {demo1.test_date.strftime('%Y-%m-%d')}")
            print(f"   - Total Score: {demo1.total_score}/600")
            print(f"   - Top Interest: STEM/Tech")
            print(f"   - Strengths: Analytical, Logical, Technical")
            
            print(f"\n2. Creative/People Profile (ID: {demo2.id})")
            print(f"   - Date: {demo2.test_date.strftime('%Y-%m-%d')}")
            print(f"   - Total Score: {demo2.total_score}/600")
            print(f"   - Top Interest: Creative + People-Oriented")
            print(f"   - Strengths: Communication, Teamwork, Creativity")
            
            print(f"\n3. Business/Management Profile (ID: {demo3.id})")
            print(f"   - Date: {demo3.test_date.strftime('%Y-%m-%d')}")
            print(f"   - Total Score: {demo3.total_score}/600")
            print(f"   - Top Interest: Business/Management")
            print(f"   - Strengths: Leadership, Adaptability, Communication")
            
            print("\n📊 Test Results URLs:")
            print(f"   - Combined Results 1: http://127.0.0.1:5000/result/combined/{demo1.id}")
            print(f"   - Combined Results 2: http://127.0.0.1:5000/result/combined/{demo2.id}")
            print(f"   - Combined Results 3: http://127.0.0.1:5000/result/combined/{demo3.id}")
            
            print("\n💡 What to Test:")
            print("   1. View each result - see if AI recommendations generate")
            print("   2. Check Career Insights - http://127.0.0.1:5000/careers/insights")
            print("   3. Download PDF reports from any result")
            print("   4. View Results History - http://127.0.0.1:5000/results/history")
            
            print("\n⚠️  NOTE:")
            print("   AI analysis will be generated on first view (may take 5-10 seconds)")
            print("   Subsequent views will use cached results")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error creating demo results: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    print("=" * 80)
    print("DEMO TEST RESULTS GENERATOR")
    print("=" * 80)
    print("\nThis script creates 3 realistic test results for testing AI features.")
    print("The results represent different student profiles:")
    print("  1. STEM/Tech-oriented (analytical, logical)")
    print("  2. Creative/People-oriented (empathetic, communicative)")
    print("  3. Business/Management-oriented (leadership, adaptable)")
    
    print("\n" + "=" * 80)
    
    confirm = input("\nProceed with creating demo data? (yes/no): ").strip().lower()
    
    if confirm in ['yes', 'y']:
        success = create_demo_results()
        if success:
            print("\n" + "=" * 80)
            print("✅ DEMO DATA CREATED SUCCESSFULLY!")
            print("=" * 80)
            print("\nLogin with: admin@neuroapt.com / Admin123!")
            print("Navigate to Results History to see all demo results.")
            print("\n" + "=" * 80)
        else:
            print("\n" + "=" * 80)
            print("❌ FAILED TO CREATE DEMO DATA")
            print("=" * 80)
            sys.exit(1)
    else:
        print("\n❌ Operation cancelled by user.")
        sys.exit(0)
