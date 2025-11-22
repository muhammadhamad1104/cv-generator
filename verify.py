"""
Quick verification script for MCP Python server
Checks all components are working correctly
"""

import os
import sys

def check_file_structure():
    """Check if all required files exist"""
    print("🔍 Checking file structure...")
    
    required_files = [
        "server.py",
        "client.py",
        "requirements.txt",
        ".env",
        "config/database.py",
        "models/profile.py",
        "models/cv.py",
        "models/user.py",
        "services/cv_service.py",
        "services/storage_service.py",
        "tools/generate_cv.py",
        "tools/profile_tools.py",
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - MISSING!")
            all_exist = False
    
    return all_exist

def check_imports():
    """Check if all required packages can be imported"""
    print("\n🔍 Checking Python packages...")
    
    required_packages = {
        'mcp': 'mcp',
        'motor': 'motor',
        'pymongo': 'pymongo',
        'dotenv': 'python-dotenv',
        'reportlab': 'reportlab',
        'PIL': 'Pillow',
    }
    
    all_installed = True
    for module, package in required_packages.items():
        try:
            __import__(module)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - NOT INSTALLED!")
            all_installed = False
    
    return all_installed

def check_env():
    """Check environment configuration"""
    print("\n🔍 Checking environment configuration...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['MONGO_URI']
    all_set = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive data
            if 'mongodb' in value.lower():
                display = value[:20] + '...' + value[-10:]
            else:
                display = value
            print(f"  ✅ {var} = {display}")
        else:
            print(f"  ❌ {var} - NOT SET!")
            all_set = False
    
    return all_set

def check_tools():
    """Check if all tools are properly defined"""
    print("\n🔍 Checking MCP tools...")
    
    try:
        from tools.generate_cv import GenerateCVTool
        from tools.profile_tools import (
            GetProfileTool,
            CreateProfileTool,
            UpdateProfileTool,
            DeleteProfileTool,
        )
        
        tools = [
            GenerateCVTool(),
            GetProfileTool(),
            CreateProfileTool(),
            UpdateProfileTool(),
            DeleteProfileTool(),
        ]
        
        for tool in tools:
            print(f"  ✅ {tool.name}: {tool.description[:50]}...")
        
        return True
    except Exception as e:
        print(f"  ❌ Error loading tools: {e}")
        return False

def check_backend_connection():
    """Check if backend is reachable"""
    print("\n🔍 Checking backend connection...")
    
    try:
        import requests
        from dotenv import load_dotenv
        load_dotenv()
        
        backend_url = os.getenv('BACKEND_URL', 'http://localhost:3000')
        response = requests.get(f"{backend_url}/health", timeout=5)
        
        if response.status_code == 200:
            print(f"  ✅ Backend is running at {backend_url}")
            return True
        else:
            print(f"  ⚠️  Backend responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"  ❌ Cannot connect to backend at {backend_url}")
        print("     Make sure the Node.js backend is running: cd ../backend && npm start")
        return False
    except Exception as e:
        print(f"  ⚠️  Error checking backend: {e}")
        return False

def main():
    """Run all checks"""
    print("=" * 70)
    print("CV Generator MCP Python - Verification Script")
    print("=" * 70)
    print()
    
    results = {
        "File Structure": check_file_structure(),
        "Python Packages": check_imports(),
        "Environment Config": check_env(),
        "MCP Tools": check_tools(),
    }
    
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    
    all_passed = True
    for check, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}  {check}")
        if not passed:
            all_passed = False
    
    print("=" * 70)
    
    if all_passed:
        print("\n🎉 All checks passed! MCP server is ready to use.")
        print("\nNext steps:")
        print("  1. Test locally: python client.py")
        print("  2. Configure Claude Desktop (see README.md)")
        print("  3. Deploy to FastMCP Cloud")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  • Install packages: pip install -r requirements.txt")
        print("  • Configure .env file with MONGO_URI")
        sys.exit(1)

if __name__ == "__main__":
    main()
