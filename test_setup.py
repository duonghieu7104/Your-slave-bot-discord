"""
Test script to verify bot setup and configuration
"""
import sys
import os

def test_python_version():
    """Check Python version"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 11:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (need 3.11+)")
        return False

def test_dependencies():
    """Check if required packages are installed"""
    print("\n📦 Checking dependencies...")
    required = ['discord', 'dotenv', 'google.generativeai', 'aiohttp']
    missing = []
    
    for package in required:
        try:
            if package == 'dotenv':
                __import__('dotenv')
            elif package == 'google.generativeai':
                __import__('google.generativeai')
            else:
                __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} (not installed)")
            missing.append(package)
    
    return len(missing) == 0

def test_env_file():
    """Check if .env file exists and has required variables"""
    print("\n⚙️  Checking .env file...")
    
    if not os.path.exists('.env'):
        print("   ❌ .env file not found")
        print("   💡 Run: cp .env.example .env")
        return False
    
    print("   ✅ .env file exists")
    
    # Try to load config
    try:
        from config import Config
        
        required_vars = {
            'DISCORD_TOKEN': Config.DISCORD_TOKEN,
            'GEMINI_API_KEY': Config.GEMINI_API_KEY
        }
        
        all_set = True
        for var_name, var_value in required_vars.items():
            if not var_value or var_value.startswith('your_'):
                print(f"   ❌ {var_name} not set")
                all_set = False
            else:
                # Show partial value for security
                masked = var_value[:8] + '...' if len(var_value) > 8 else '***'
                print(f"   ✅ {var_name} = {masked}")
        
        return all_set
    
    except Exception as e:
        print(f"   ❌ Error loading config: {e}")
        return False

def test_modules():
    """Check if bot modules can be imported"""
    print("\n🔧 Checking bot modules...")
    
    modules = [
        'config',
        'message_buffer',
        'task_note_manager',
        'gemini_service',
        'persistence'
    ]
    
    all_ok = True
    for module in modules:
        try:
            __import__(module)
            print(f"   ✅ {module}.py")
        except Exception as e:
            print(f"   ❌ {module}.py - {str(e)}")
            all_ok = False
    
    return all_ok

def test_data_directory():
    """Check if data directory exists"""
    print("\n📁 Checking data directory...")
    
    if not os.path.exists('data'):
        print("   ⚠️  data/ directory not found (will be created on first run)")
        try:
            os.makedirs('data')
            print("   ✅ Created data/ directory")
        except Exception as e:
            print(f"   ❌ Could not create data/ directory: {e}")
            return False
    else:
        print("   ✅ data/ directory exists")
    
    return True

def main():
    """Run all tests"""
    print("=" * 50)
    print("🤖 Discord Task & Note Manager Bot - Setup Test")
    print("=" * 50)
    
    results = []
    
    results.append(("Python Version", test_python_version()))
    results.append(("Dependencies", test_dependencies()))
    results.append(("Environment File", test_env_file()))
    results.append(("Bot Modules", test_modules()))
    results.append(("Data Directory", test_data_directory()))
    
    print("\n" + "=" * 50)
    print("📊 Test Results")
    print("=" * 50)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
        if not passed:
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("\n🎉 All tests passed! You're ready to run the bot.")
        print("\n▶️  Run: python bot.py")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        print("\n💡 Quick fixes:")
        print("   - Install dependencies: pip install -r requirements.txt")
        print("   - Create .env file: cp .env.example .env")
        print("   - Edit .env and add your DISCORD_TOKEN and GEMINI_API_KEY")
    
    print()
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

