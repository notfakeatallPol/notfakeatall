import os
import sys
import subprocess
import shutil

def build_executable():
    print("Building Secure Submission System Executable...")
    
    # Ensure static and templates directories exist
    if not os.path.exists('static'):
        os.makedirs('static')
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Build command
    pyinstaller_command = [
        'pyinstaller',
        '--name=SecureSubmissionSystem',
        '--onefile',
        '--windowed',
        '--icon=static/favicon.ico' if os.path.exists('static/favicon.ico') else None,
        '--add-data=templates:templates',
        '--add-data=static:static',
        'secure_submission_app.py'
    ]
    
    # Remove None values
    pyinstaller_command = [cmd for cmd in pyinstaller_command if cmd is not None]
    
    # Adjust command for Windows vs Unix
    if sys.platform.startswith('win'):
        # Windows uses semicolons as path separators
        pyinstaller_command = [cmd.replace(':', ';') if ':' in cmd and cmd.startswith('--add-data') else cmd 
                               for cmd in pyinstaller_command]
    
    # Run PyInstaller
    try:
        subprocess.check_call(pyinstaller_command)
        print("Build completed successfully!")
        print(f"Executable created at: {os.path.join('dist', 'SecureSubmissionSystem.exe')}")
    except subprocess.CalledProcessError as e:
        print(f"Error building executable: {e}")
        return False
    
    return True

if __name__ == "__main__":
    build_executable()