#!/usr/bin/env python3
"""
Verification script for AI Test Platform
"""

import sys
import os

def verify_project_structure():
    """Verify project structure"""
    print("Verifying project structure...")
    
    required_dirs = [
        'backend',
        'backend/app',
        'backend/app/api',
        'backend/app/core',
        'backend/app/models',
        'backend/app/services',
        'backend/app/utils',
        'frontend',
        'frontend/src',
        'frontend/src/api',
        'frontend/src/components',
        'frontend/src/views',
        'frontend/src/router',
        'frontend/src/stores',
        'frontend/src/utils',
        'nginx'
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if os.path.isdir(dir_path):
            print(f"✓ {dir_path}/")
        else:
            print(f"✗ {dir_path}/ - MISSING")
            all_exist = False
    
    return all_exist

def verify_backend_files():
    """Verify backend files"""
    print("\nVerifying backend files...")
    
    required_files = [
        'backend/Dockerfile',
        'backend/requirements.txt',
        'backend/app/main.py',
        'backend/app/__init__.py',
        'backend/app/core/__init__.py',
        'backend/app/core/config.py',
        'backend/app/core/database.py',
        'backend/app/core/security.py',
        'backend/app/core/redis.py',
        'backend/app/models/__init__.py',
        'backend/app/models/user.py',
        'backend/app/models/company.py',
        'backend/app/models/project.py',
        'backend/app/models/test_case.py',
        'backend/app/models/test_execution.py',
        'backend/app/models/test_report.py',
        'backend/app/api/__init__.py',
        'backend/app/api/auth.py',
        'backend/app/api/companies.py',
        'backend/app/api/projects.py',
        'backend/app/api/users.py',
        'backend/app/api/test_cases.py',
        'backend/app/api/test_executions.py',
        'backend/app/api/test_reports.py',
        'backend/app/services/__init__.py',
        'backend/app/services/test_runner.py',
        'backend/app/services/report_generator.py',
        'backend/app/services/ai_service.py'
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - MISSING")
            all_exist = False
    
    return all_exist

def verify_frontend_files():
    """Verify frontend files"""
    print("\nVerifying frontend files...")
    
    required_files = [
        'frontend/Dockerfile',
        'frontend/Dockerfile.prod',
        'frontend/package.json',
        'frontend/vite.config.ts',
        'frontend/tsconfig.json',
        'frontend/tsconfig.node.json',
        'frontend/index.html',
        'frontend/nginx.conf',
        'frontend/src/main.ts',
        'frontend/src/App.vue',
        'frontend/src/env.d.ts',
        'frontend/src/router/index.ts',
        'frontend/src/stores/auth.ts',
        'frontend/src/utils/api.ts',
        'frontend/src/utils/index.ts',
        'frontend/src/components/PageHeader.vue',
        'frontend/src/components/StatCard.vue',
        'frontend/src/views/Login.vue',
        'frontend/src/views/Layout.vue',
        'frontend/src/views/Dashboard.vue',
        'frontend/src/views/Companies.vue',
        'frontend/src/views/Projects.vue',
        'frontend/src/views/ProjectDetail.vue',
        'frontend/src/views/TestCases.vue',
        'frontend/src/views/TestCaseDetail.vue',
        'frontend/src/views/TestExecutions.vue',
        'frontend/src/views/TestReports.vue',
        'frontend/src/views/TestReportDetail.vue',
        'frontend/src/views/Users.vue',
        'frontend/src/views/Profile.vue',
        'frontend/src/views/NotFound.vue'
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - MISSING")
            all_exist = False
    
    return all_exist

def verify_config_files():
    """Verify configuration files"""
    print("\nVerifying configuration files...")
    
    required_files = [
        'docker-compose.yml',
        'docker-compose.prod.yml',
        'nginx/nginx.conf',
        '.env.example',
        '.env.production',
        '.gitignore',
        'README.md',
        'start.bat',
        'stop.bat'
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - MISSING")
            all_exist = False
    
    return all_exist

def main():
    """Main verification function"""
    print("=" * 60)
    print("AI Test Platform - Project Verification")
    print("=" * 60)
    
    all_passed = True
    
    # Verify project structure
    if not verify_project_structure():
        all_passed = False
    
    # Verify backend files
    if not verify_backend_files():
        all_passed = False
    
    # Verify frontend files
    if not verify_frontend_files():
        all_passed = False
    
    # Verify configuration files
    if not verify_config_files():
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All verifications passed!")
        print("\nProject is ready to use!")
        print("\nQuick Start:")
        print("  1. Start with Docker: start.bat")
        print("  2. Or manually:")
        print("     - Backend: cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload")
        print("     - Frontend: cd frontend && npm install && npm run dev")
        print("\nDefault admin credentials:")
        print("  Username: admin")
        print("  Password: admin123")
    else:
        print("✗ Some verifications failed!")
        print("Please check the missing files and try again.")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())