#!/usr/bin/env python3
"""
Simple test script to verify frontend setup
"""

import sys
import os

def test_files():
    """Test that all required files exist"""
    print("Testing frontend files...")
    
    required_files = [
        'frontend/package.json',
        'frontend/vite.config.ts',
        'frontend/tsconfig.json',
        'frontend/index.html',
        'frontend/src/main.ts',
        'frontend/src/App.vue',
        'frontend/src/router/index.ts',
        'frontend/src/stores/auth.ts',
        'frontend/src/views/Login.vue',
        'frontend/src/views/Layout.vue',
        'frontend/src/views/Dashboard.vue',
        'frontend/src/views/Projects.vue',
        'frontend/src/views/TestCases.vue',
        'frontend/src/views/TestExecutions.vue',
        'frontend/src/views/TestReports.vue',
        'frontend/src/views/Users.vue',
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - MISSING")
            all_exist = False
    
    return all_exist

def test_package_json():
    """Test package.json content"""
    print("\nTesting package.json...")
    
    import json
    
    try:
        with open('frontend/package.json', 'r') as f:
            package_data = json.load(f)
        
        # Check required dependencies
        required_deps = ['vue', 'vue-router', 'pinia', 'axios', 'element-plus']
        dependencies = package_data.get('dependencies', {})
        
        for dep in required_deps:
            if dep in dependencies:
                print(f"✓ {dep}: {dependencies[dep]}")
            else:
                print(f"✗ {dep} - MISSING")
                return False
        
        # Check scripts
        scripts = package_data.get('scripts', {})
        required_scripts = ['dev', 'build']
        
        for script in required_scripts:
            if script in scripts:
                print(f"✓ Script '{script}': {scripts[script]}")
            else:
                print(f"✗ Script '{script}' - MISSING")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Error reading package.json: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 50)
    print("AI Test Platform - Frontend Verification")
    print("=" * 50)
    
    all_passed = True
    
    # Test files
    if not test_files():
        all_passed = False
    
    # Test package.json
    if not test_package_json():
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✓ All frontend tests passed!")
        print("\nTo start the frontend:")
        print("  cd frontend")
        print("  npm install")
        print("  npm run dev")
    else:
        print("✗ Some tests failed!")
    print("=" * 50)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())