#!/usr/bin/env python3
"""
Simple test script to verify backend setup
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test that all imports work"""
    print("Testing imports...")
    
    try:
        from app.core.config import settings
        print("✓ Config imported successfully")
    except Exception as e:
        print(f"✗ Config import failed: {e}")
        return False
    
    try:
        from app.core.database import Base, engine
        print("✓ Database imported successfully")
    except Exception as e:
        print(f"✗ Database import failed: {e}")
        return False
    
    try:
        from app.models import User, Company, Project, TestCase, TestExecution, TestReport
        print("✓ Models imported successfully")
    except Exception as e:
        print(f"✗ Models import failed: {e}")
        return False
    
    try:
        from app.core.security import create_access_token, verify_password
        print("✓ Security imported successfully")
    except Exception as e:
        print(f"✗ Security import failed: {e}")
        return False
    
    try:
        from app.api import auth, companies, projects, users, test_cases, test_executions, test_reports
        print("✓ API routes imported successfully")
    except Exception as e:
        print(f"✗ API routes import failed: {e}")
        return False
    
    try:
        from app.services.test_runner import TestRunner
        print("✓ Test runner imported successfully")
    except Exception as e:
        print(f"✗ Test runner import failed: {e}")
        return False
    
    try:
        from app.services.ai_service import ai_service
        print("✓ AI service imported successfully")
    except Exception as e:
        print(f"✗ AI service import failed: {e}")
        return False
    
    return True

def test_config():
    """Test configuration"""
    print("\nTesting configuration...")
    
    from app.core.config import settings
    
    print(f"✓ App name: {settings.APP_NAME}")
    print(f"✓ App version: {settings.APP_VERSION}")
    print(f"✓ Database URL: {settings.DATABASE_URL[:20]}...")
    print(f"✓ Redis URL: {settings.REDIS_URL}")
    print(f"✓ CORS origins: {settings.CORS_ORIGINS}")
    
    return True

def test_models():
    """Test models"""
    print("\nTesting models...")
    
    from app.models import User, Company, Project, TestCase, TestExecution, TestReport
    
    # Check model attributes
    user_attrs = ['id', 'username', 'email', 'password_hash', 'role', 'company_id']
    for attr in user_attrs:
        if hasattr(User, attr):
            print(f"✓ User.{attr} exists")
        else:
            print(f"✗ User.{attr} missing")
            return False
    
    company_attrs = ['id', 'name', 'description']
    for attr in company_attrs:
        if hasattr(Company, attr):
            print(f"✓ Company.{attr} exists")
        else:
            print(f"✗ Company.{attr} missing")
            return False
    
    return True

def main():
    """Main test function"""
    print("=" * 50)
    print("AI Test Platform - Backend Verification")
    print("=" * 50)
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
    
    # Test config
    if not test_config():
        all_passed = False
    
    # Test models
    if not test_models():
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✓ All backend tests passed!")
        print("\nTo start the backend:")
        print("  cd backend")
        print("  pip install -r requirements.txt")
        print("  uvicorn app.main:app --reload")
    else:
        print("✗ Some tests failed!")
    print("=" * 50)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())