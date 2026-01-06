"""
Quick test script to verify AgroVision setup
"""
import sys
import os

# Fix Windows encoding issues
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

print("=" * 60)
print("AgroVision - System Check")
print("=" * 60)

# Check Python version
print(f"\nPython Version: {sys.version.split()[0]}")

# Check required files
print("\n[Checking Required Files]")
required_files = {
    'app.py': 'Main application',
    'plant_disease_model.h5': 'Disease detection model',
    'templates/index.html': 'Home page template',
    'templates/detect.html': 'Detection page template',
    'static/js/chatbot.js': 'Chatbot widget',
    'requirements.txt': 'Dependencies list'
}

all_good = True
for file, desc in required_files.items():
    if os.path.exists(file):
        print(f"  [OK] {file} - {desc}")
    else:
        print(f"  [MISSING] {file} - {desc}")
        all_good = False

# Check Python packages
print("\n[Checking Python Packages]")
packages = ['flask', 'tensorflow', 'numpy', 'PIL', 'h5py', 'google.generativeai']
for pkg in packages:
    try:
        if pkg == 'google.generativeai':
            import google.generativeai
        else:
            __import__(pkg)
        print(f"  [OK] {pkg}")
    except ImportError:
        print(f"  [MISSING] {pkg} - NOT INSTALLED")
        all_good = False

# Check directories
print("\n[Checking Directories]")
dirs = ['templates', 'static', 'static/uploads', 'static/js', 'static/css']
for dir_name in dirs:
    if os.path.exists(dir_name):
        print(f"  [OK] {dir_name}/")
    else:
        print(f"  [MISSING] {dir_name}/")
        if 'uploads' in dir_name:
            print(f"    (Will be created automatically)")

print("\n" + "=" * 60)
if all_good:
    print("\n[SUCCESS] All checks passed! Ready to run.")
    print("\nTo start the server, run:")
    print("  python app.py")
    print("  or")
    print("  python run.py")
else:
    print("\n[WARNING] Some issues found. Please fix them before running.")
print("=" * 60)
