import os
import sys
import zipfile
import datetime

def create_source_package():
    """
    Create a source package zip file containing all the files needed to build the Windows executable.
    """
    print("Creating source package for Secure Submission System...")
    
    # Get the current date for the filename
    today = datetime.datetime.now().strftime("%Y%m%d")
    
    # Define the output zip file name
    zip_filename = f"secure_submission_system_source_{today}.zip"
    
    # Files to include in the package
    files_to_include = [
        # Core application files
        'secure_submission_app.py',
        'README.txt',
        'LICENSE',
        
        # Build scripts
        'build_windows_app.py',
        'create_distribution.py',
        'create_installer_image.py',
        'setup_windows_build_environment.py',
        'installer.nsi',
        'windows_app_guide.md',
        'run_secure_submission_system.bat',
        
        # Ensure static files are included
        'static/favicon.ico',
        'static/favicon.svg',
        'static/installer-welcome.bmp',
        'static/css/style.css',
        'static/js/main.js',
        'static/uploads/.gitkeep',
    ]
    
    # Template files
    template_files = []
    for root, dirs, files in os.walk('templates'):
        for file in files:
            template_files.append(os.path.join(root, file))
    
    # Create the zip file
    try:
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add core and build files
            for file in files_to_include:
                if os.path.exists(file):
                    zipf.write(file)
                else:
                    print(f"Warning: File not found: {file}")
            
            # Add template files
            for file in template_files:
                if os.path.exists(file):
                    zipf.write(file)
        
        print(f"Source package created: {zip_filename}")
        print(f"This file contains everything needed to build the Windows executable application.")
        print("To use it:")
        print("1. Extract the zip file on a Windows computer")
        print("2. Run 'setup_windows_build_environment.py' to install dependencies")
        print("3. Run 'build_windows_app.py' to create the Windows installer")
        
        return zip_filename
    
    except Exception as e:
        print(f"Error creating source package: {e}")
        return None

if __name__ == "__main__":
    create_source_package()