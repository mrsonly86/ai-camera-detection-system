#!/usr/bin/env python3
"""
Simple test script to verify the AI Camera Detection System setup
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test that all major components can be imported"""
    print("Testing imports...")
    
    try:
        from backend.app.core.config import get_settings
        print("✓ Config module imported successfully")
        
        from backend.app.core.database import create_tables
        print("✓ Database module imported successfully")
        
        from backend.app.models.database_models import User, Detection
        print("✓ Database models imported successfully")
        
        from backend.app.models.schemas import UserCreate, DetectionResult
        print("✓ Pydantic schemas imported successfully")
        
        print("✓ All core imports successful!")
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


def test_ai_engines():
    """Test AI engine initialization (without requiring models)"""
    print("\nTesting AI engines...")
    
    try:
        # Test detector without loading model
        from backend.app.ai_engine.yolo_detector import YOLOv5Detector
        print("✓ YOLOv5 detector class imported")
        
        # Test camera interface
        from backend.app.ai_engine.camera_interface import CameraInterface
        print("✓ Camera interface class imported")
        
        # Test advanced analysis
        from backend.app.ai_engine.advanced_analysis import AdvancedAIAnalyzer
        print("✓ Advanced AI analyzer class imported")
        
        # Test face recognition
        from backend.app.ai_engine.face_recognition import FaceRecognitionSystem
        print("✓ Face recognition system class imported")
        
        return True
        
    except Exception as e:
        print(f"✗ AI engines test failed: {e}")
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


def main():
    """Run all tests"""
    print("AI Camera Detection System - Setup Verification")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config,
        test_database,
        test_ai_engines,
        test_api_structure
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed! System is ready.")
        return 0
    else:
        print("✗ Some tests failed. Check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())