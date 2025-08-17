#!/usr/bin/env python3
"""
Minimal test script to verify the AI Camera Detection System basic setup
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_basic_imports():
    """Test that basic components can be imported"""
    print("Testing basic imports...")
    
    try:
        from backend.app.core.config import get_settings
        print("✓ Config module imported successfully")
        
        from backend.app.core.database import create_tables
        print("✓ Database module imported successfully")
        
        from backend.app.models.database_models import User, Detection
        print("✓ Database models imported successfully")
        
        from backend.app.models.schemas import UserCreate, DetectionResult
        print("✓ Pydantic schemas imported successfully")
        
        print("✓ All basic imports successful!")
        return True
        
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    try:
        from backend.app.core.config import get_settings
        settings = get_settings()
        
        print(f"✓ App name: {settings.app_name}")
        print(f"✓ App version: {settings.app_version}")
        print(f"✓ Database URL: {settings.database_url}")
        print(f"✓ API host: {settings.api_host}:{settings.api_port}")
        
        return True
        
    except Exception as e:
        print(f"✗ Config test failed: {e}")
        return False


def test_database():
    """Test database creation"""
    print("\nTesting database...")
    
    try:
        from backend.app.core.database import create_tables, get_db
        
        # Create tables
        create_tables()
        print("✓ Database tables created successfully")
        
        # Test database session
        db_gen = get_db()
        db = next(db_gen)
        db.close()
        print("✓ Database session created successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False


def test_api_structure():
    """Test API structure without starting server"""
    print("\nTesting API structure...")
    
    try:
        from backend.main import app
        print("✓ FastAPI app created successfully")
        
        from backend.app.api.api_v1.api import api_router
        print("✓ API router imported successfully")
        
        # Check that routes are included
        routes = [route.path for route in app.routes]
        api_routes = [route for route in routes if route.startswith('/api/v1')]
        
        print(f"✓ Found {len(api_routes)} API routes")
        print("✓ API structure test passed")
        
        return True
        
    except Exception as e:
        print(f"✗ API structure test failed: {e}")
        return False


def test_services():
    """Test service layer"""
    print("\nTesting service layer...")
    
    try:
        from backend.app.services.user_service import UserService
        print("✓ User service imported successfully")
        
        from backend.app.services.detection_service import DetectionService
        print("✓ Detection service imported successfully")
        
        from backend.app.services.system_service import SystemService
        print("✓ System service imported successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Service layer test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("AI Camera Detection System - Basic Setup Verification")
    print("=" * 55)
    
    tests = [
        test_basic_imports,
        test_config,
        test_database,
        test_api_structure,
        test_services
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 55)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All basic tests passed! Core system is ready.")
        print("\nNote: AI engines (YOLOv5, face recognition) require additional dependencies")
        print("Run 'pip install torch ultralytics face-recognition mediapipe' to enable AI features")
        return 0
    else:
        print("✗ Some tests failed. Check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())