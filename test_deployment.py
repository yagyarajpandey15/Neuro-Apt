"""
Test script to verify deployment configuration locally
Run this before deploying to catch any import errors
"""
import sys
import os

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    try:
        from neuroapt.app import create_app
        print("✓ neuroapt.app.create_app imported successfully")
        
        from config import config
        print("✓ config imported successfully")
        
        import wsgi
        print("✓ wsgi module imported successfully")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_app_creation():
    """Test that Flask app can be created"""
    print("\nTesting app creation...")
    try:
        from wsgi import app
        print(f"✓ Flask app created successfully")
        print(f"  App name: {app.name}")
        print(f"  Debug mode: {app.debug}")
        return True
    except Exception as e:
        print(f"✗ App creation error: {e}")
        return False

def test_gunicorn_config():
    """Test gunicorn configuration"""
    print("\nTesting gunicorn config...")
    try:
        import gunicorn_config
        print(f"✓ Gunicorn config loaded successfully")
        print(f"  Workers: {gunicorn_config.workers}")
        print(f"  Timeout: {gunicorn_config.timeout}")
        return True
    except Exception as e:
        print(f"✗ Gunicorn config error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("NEURO-APT DEPLOYMENT VERIFICATION")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_app_creation,
        test_gunicorn_config
    ]
    
    results = [test() for test in tests]
    
    print("\n" + "=" * 60)
    if all(results):
        print("✓ ALL TESTS PASSED - Ready for deployment!")
        print("=" * 60)
        return 0
    else:
        print("✗ SOME TESTS FAILED - Fix errors before deploying")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
