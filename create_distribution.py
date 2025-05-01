import os
import sys
import shutil
import subprocess

def create_distribution():
    """
    Creates a complete distribution package with the executable and all required files.
    """
    print("Creating Secure Submission System Distribution Package...")
    
    # Define distribution directory
    dist_dir = 'distribution'
    
    # Create distribution directory if it doesn't exist
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir)
    
    # Build the executable using PyInstaller
    print("Building executable...")
    pyinstaller_command = [
        'pyinstaller',
        '--name=SecureSubmissionSystem',
        '--onefile',
        '--windowed',
        '--icon=static/favicon.ico',
        '--add-data=templates:templates',
        '--add-data=static:static',
        'secure_submission_app.py'
    ]
    
    # Adjust path separator for Windows
    if sys.platform.startswith('win'):
        pyinstaller_command = [
            cmd.replace(':', ';') if ':' in cmd and cmd.startswith('--add-data') else cmd 
            for cmd in pyinstaller_command
        ]
    
    # Run PyInstaller
    try:
        subprocess.check_call(pyinstaller_command)
        print("Executable built successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error building executable: {e}")
        return False
    
    # Copy the executable to the distribution directory
    shutil.copy(os.path.join('dist', 'SecureSubmissionSystem.exe' if sys.platform.startswith('win') else 'SecureSubmissionSystem'), 
               os.path.join(dist_dir, 'SecureSubmissionSystem.exe' if sys.platform.startswith('win') else 'SecureSubmissionSystem'))
    
    # Copy the batch file to the distribution directory
    shutil.copy('run_secure_submission_system.bat', os.path.join(dist_dir, 'run_secure_submission_system.bat'))
    
    # Copy README.txt to the distribution directory
    shutil.copy('README.txt', os.path.join(dist_dir, 'README.txt'))
    
    # Clean up build artifacts
    print("Cleaning up build artifacts...")
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('SecureSubmissionSystem.spec'):
        os.remove('SecureSubmissionSystem.spec')
    
    print(f"Distribution package created successfully in the '{dist_dir}' directory!")
    print("To use the application:")
    print(f"1. Copy the '{dist_dir}' folder to the target computer")
    print("2. Run 'run_secure_submission_system.bat' to start the application")
    
    return True

if __name__ == "__main__":
    create_distribution()