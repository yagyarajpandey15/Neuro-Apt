#!/usr/bin/env python
"""
Clear AI Analysis Cache
Forces regeneration of AI career recommendations with updated format
"""

import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from neuroapt.app import create_app, db
from neuroapt.app.models import TestResult

def clear_ai_cache():
    """Clear cached AI analysis from all test results"""
    
    app = create_app()
    with app.app_context():
        # Get all test results
        test_results = TestResult.query.all()
        
        if not test_results:
            print("No test results found in database.")
            return False
        
        print(f"Found {len(test_results)} test result(s)")
        print("\nClearing cached AI analysis...")
        
        cleared_count = 0
        for result in test_results:
            if result.ai_analysis:
                result.ai_analysis = None
                cleared_count += 1
                print(f"  ✓ Cleared cache for Test Result ID {result.id}")
        
        if cleared_count > 0:
            db.session.commit()
            print(f"\n✅ Successfully cleared AI cache from {cleared_count} result(s)")
            print("\n📝 What happens next:")
            print("   - Visit any result page")
            print("   - AI analysis will regenerate (5-10 seconds)")
            print("   - Alternative Career Paths will show proper stats")
            print("\n🔗 Test URLs:")
            print("   - Profile 1: http://127.0.0.1:5000/result/combined/3")
            print("   - Profile 2: http://127.0.0.1:5000/result/combined/4")
            print("   - Profile 3: http://127.0.0.1:5000/result/combined/5")
            return True
        else:
            print("\nℹ️  No cached AI analysis found. Nothing to clear.")
            return True

if __name__ == "__main__":
    print("=" * 80)
    print("CLEAR AI ANALYSIS CACHE")
    print("=" * 80)
    print("\nThis will clear cached AI analysis and force regeneration with updated format.")
    print("The Alternative Career Paths section will then show proper ability stats.")
    print("\n" + "=" * 80)
    
    confirm = input("\nProceed? (yes/no): ").strip().lower()
    
    if confirm in ['yes', 'y']:
        success = clear_ai_cache()
        if success:
            print("\n" + "=" * 80)
            print("✅ CACHE CLEARED SUCCESSFULLY!")
            print("=" * 80)
        else:
            print("\n" + "=" * 80)
            print("❌ FAILED TO CLEAR CACHE")
            print("=" * 80)
            sys.exit(1)
    else:
        print("\n❌ Operation cancelled.")
        sys.exit(0)
