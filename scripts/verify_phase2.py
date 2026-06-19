"""
Phase 2 Verification Script
Tests that all components are properly installed and configured
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    try:
        import openai
        print("  ✅ openai package installed")
    except ImportError:
        print("  ❌ openai package NOT installed - Run: pip install openai")
        return False
    
    try:
        from neuroapt.app.utils.openai_api import (
            get_openai_client, 
            generate_ai_career_analysis,
            generate_skill_suggestions
        )
        print("  ✅ openai_api.py imports successful")
    except ImportError as e:
        print(f"  ❌ openai_api.py import failed: {e}")
        return False
    
    try:
        from neuroapt.app.utils.recommendation_engine import (
            get_career_recommendations,
            get_skill_development_recommendations,
            build_student_profile
        )
        print("  ✅ recommendation_engine.py imports successful")
    except ImportError as e:
        print(f"  ❌ recommendation_engine.py import failed: {e}")
        return False
    
    try:
        from neuroapt.app.models import TestResult
        print("  ✅ models.py imports successful")
    except ImportError as e:
        print(f"  ❌ models.py import failed: {e}")
        return False
    
    return True

def test_env_config():
    """Test environment configuration"""
    print("\nTesting environment configuration...")
    
    # Check .env file exists
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    if os.path.exists(env_path):
        print("  ✅ .env file exists")
    else:
        print("  ⚠️  .env file NOT found - Copy from .env.example and add API key")
        return False
    
    # Check for OpenAI API key
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.environ.get('OPENAI_API_KEY')
    if api_key and api_key.startswith('sk-'):
        print("  ✅ OPENAI_API_KEY is set")
        return True
    else:
        print("  ⚠️  OPENAI_API_KEY not set or invalid in .env file")
        return False

def test_database_schema():
    """Test that database has required fields"""
    print("\nTesting database schema...")
    
    try:
        from neuroapt.app import create_app, db
        from neuroapt.app.models import TestResult
        
        app = create_app()
        with app.app_context():
            # Check if ai_analysis column exists
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('test_result')]
            
            required_columns = [
                'ai_analysis',
                'confidence_level',
                'answer_pattern_flag',
                'contradictions_detected',
                'interest_intersection'
            ]
            
            missing = [col for col in required_columns if col not in columns]
            
            if not missing:
                print("  ✅ All AI fields exist in database")
                return True
            else:
                print(f"  ⚠️  Missing database fields: {', '.join(missing)}")
                print("     Run: python scripts\\setup\\migrate_add_ai_fields.py")
                return False
    
    except Exception as e:
        print(f"  ❌ Database check failed: {e}")
        return False

def test_openai_connection():
    """Test OpenAI API connection"""
    print("\nTesting OpenAI API connection...")
    
    try:
        from neuroapt.app import create_app
        from neuroapt.app.utils.openai_api import get_openai_client
        
        app = create_app()
        with app.app_context():
            client = get_openai_client()
            
            if client:
                print("  ✅ OpenAI client initialized successfully")
                
                # Try a minimal API call
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": "Say 'test'"}],
                        max_tokens=10
                    )
                    print("  ✅ OpenAI API connection verified")
                    return True
                except Exception as e:
                    print(f"  ⚠️  OpenAI API call failed: {str(e)}")
                    print("     Check your API key and internet connection")
                    return False
            else:
                print("  ❌ OpenAI client NOT initialized")
                return False
    
    except Exception as e:
        print(f"  ❌ OpenAI connection test failed: {e}")
        return False

def test_recommendation_engine():
    """Test recommendation engine functionality"""
    print("\nTesting recommendation engine...")
    
    try:
        from neuroapt.app import create_app, db
        from neuroapt.app.models import TestResult
        from neuroapt.app.utils.recommendation_engine import build_student_profile
        
        app = create_app()
        with app.app_context():
            # Get any test result from database
            test_result = TestResult.query.first()
            
            if not test_result:
                print("  ⚠️  No test results in database - Complete a test first")
                return False
            
            # Try building student profile
            profile = build_student_profile(test_result)
            
            if profile and 'scores' in profile and 'cognitive_abilities' in profile:
                print("  ✅ Student profile builder works")
                
                # Check if helper methods exist
                if hasattr(test_result, 'get_ai_analysis_dict'):
                    print("  ✅ TestResult helper methods exist")
                    return True
                else:
                    print("  ⚠️  TestResult missing helper methods")
                    return False
            else:
                print("  ❌ Student profile builder returned invalid data")
                return False
    
    except Exception as e:
        print(f"  ❌ Recommendation engine test failed: {e}")
        return False

def main():
    """Run all verification tests"""
    print("="*60)
    print("Phase 2 Verification Script")
    print("="*60)
    
    results = {
        'Imports': test_imports(),
        'Environment': test_env_config(),
        'Database Schema': test_database_schema(),
        'OpenAI Connection': test_openai_connection(),
        'Recommendation Engine': test_recommendation_engine()
    }
    
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:.<50} {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! System is ready.")
        print("\nNext steps:")
        print("1. Start Flask server: python run.py")
        print("2. Login and take a test")
        print("3. View results to see AI-powered recommendations")
    else:
        print("⚠️  SOME TESTS FAILED - Follow instructions above to fix")
    print("="*60)
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
