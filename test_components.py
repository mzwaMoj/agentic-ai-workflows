#!/usr/bin/env python
"""
Test script to identify specific import and initialization issues.
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path (mimicking the app structure)
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

print("=== Testing Specific App Components ===")

def test_component(description, test_func):
    """Helper to test a component and report results."""
    try:
        result = test_func()
        print(f"✅ {description}")
        return True
    except Exception as e:
        print(f"❌ {description}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

# Test 1: Settings configuration
def test_settings():
    from app.config.settings import settings
    return f"Settings loaded: {settings.app_name}"

# Test 2: Service initialization
def test_services():
    from app.services import ServiceContainer
    from app.config.settings import settings
    container = ServiceContainer(settings)
    return "Service container created"

# Test 3: OpenAI service (critical for the app)
def test_openai_service():
    from app.services.openai_service import OpenAIService
    from app.config.settings import settings
    service = OpenAIService(settings)
    return "OpenAI service created"

# Test 4: Vector service
def test_vector_service():
    from app.services.vector_service import VectorService
    from app.config.settings import settings
    service = VectorService(settings)
    return "Vector service created"

# Test 5: Core Text2SQL engine
def test_text2sql_engine():
    from app.core.text2sql_engine import Text2SQLEngine
    # Create mock services dict
    services = {}
    engine = Text2SQLEngine(services)
    return "Text2SQL engine created"

# Test 6: API routers
def test_api_routers():
    from app.api.v1 import health_router, text2sql_router, chat_router
    return f"Routers imported: {len([health_router, text2sql_router, chat_router])}"

# Test 7: Main app creation (without running)
def test_main_app():
    from app.main import create_app
    app = create_app()
    return f"App created: {app.title}"

print("\n--- Running Component Tests ---")
tests = [
    ("Settings Configuration", test_settings),
    ("Service Container", test_services),
    ("OpenAI Service", test_openai_service),
    ("Vector Service", test_vector_service),
    ("Text2SQL Engine", test_text2sql_engine),
    ("API Routers", test_api_routers),
    ("Main App Creation", test_main_app)
]

results = []
for description, test_func in tests:
    results.append(test_component(description, test_func))

print(f"\n=== Test Summary ===")
passed = sum(results)
total = len(results)
print(f"Passed: {passed}/{total}")

if passed < total:
    print("\n⚠️ Some components failed. Check errors above.")
else:
    print("\n🎉 All components passed basic tests.")
