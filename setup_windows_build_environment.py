import os
import sys
import subprocess
import platform

def setup_windows_build_environment():
    """
    Setup the Windows build environment by installing required Python packages.
    """
    print("=" * 70)
    print(" SECURE SUBMISSION SYSTEM - WINDOWS BUILD ENVIRONMENT SETUP")
    print("=" * 70)
    
    # Check Python version
    python_version = platform.python_version()
    print(f"Detected Python version: {python_version}")
    
    required_major = 3
    required_minor = 6
    
    major, minor, _ = map(int, python_version.split('.'))
    
    if major < required_major or (major == required_major and minor < required_minor):
        print(f"Error: Python {required_major}.{required_minor} or newer is required.")
        print(f"Please install a newer version of Python from https://www.python.org/downloads/")
        return
    
    # Install required Python packages
    print("\nInstalling required Python packages...")
    
    required_packages = [
        "pyinstaller",        # For creating the executable
        "pillow",             # For image processing
        "flask",              # Web framework
        "flask-login",        # Authentication
        "flask-wtf",          # Forms
        "cryptography",       # Encryption
        "email-validator",    # Email validation
        "werkzeug",           # WSGI utilities
    ]
    
    for package in required_packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"Successfully installed {package}")
        except subprocess.CalledProcessError as e:
            print(f"Error installing {package}: {e}")
            print("Please try to install it manually:")
            print(f"  pip install {package}")
    
    # Check for NSIS (for building installer)
    print("\nChecking for NSIS (Nullsoft Scriptable Install System)...")
    
    nsis_found = False
    common_paths = [
        r"C:\Program Files\NSIS\makensis.exe",
        r"C:\Program Files (x86)\NSIS\makensis.exe"
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            nsis_found = True
            print(f"NSIS found at: {path}")
            break
    
    if not nsis_found:
        print("NSIS not found. You need to install it to build the Windows installer.")
        print("Please download and install NSIS from https://nsis.sourceforge.io/Download")
        print("Install it to the default location.")
    
    # Final instructions
    print("\n" + "=" * 70)
    print(" SETUP COMPLETE")
    print("=" * 70)
    
    print("\nYour build environment is now set up!")
    print("\nNext steps:")
    
    if not nsis_found:
        print("1. Install NSIS from https://nsis.sourceforge.io/Download")
    
    print("2. Run the build script:")
    print("   python build_windows_app.py")
    
    print("\nThis will create a Windows installer in the 'releases' directory.")

if __name__ == "__main__":
    setup_windows_build_environment()