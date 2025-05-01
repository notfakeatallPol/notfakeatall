import os
import sys
import shutil
import subprocess
import platform

def build_windows_app():
    """
    Master build script for creating the Windows executable application and installer.
    """
    print("=" * 70)
    print(" SECURE SUBMISSION SYSTEM - WINDOWS APPLICATION BUILDER")
    print("=" * 70)
    
    # Check if running on Windows
    if not platform.system() == 'Windows':
        print("Warning: This script is designed to run on Windows.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Build cancelled.")
            return
    
    # Step 1: Create the distribution package
    print("\nSTEP 1: Creating distribution package...")
    
    try:
        from create_distribution import create_distribution
        success = create_distribution()
        if not success:
            print("Failed to create distribution package. Exiting.")
            return
    except Exception as e:
        print(f"Error creating distribution package: {e}")
        return
    
    # Step 2: Build the installer (requires NSIS)
    print("\nSTEP 2: Building Windows installer...")
    
    # Check if NSIS is installed
    nsis_path = None
    
    # Try common NSIS installation paths
    common_paths = [
        r"C:\Program Files\NSIS\makensis.exe",
        r"C:\Program Files (x86)\NSIS\makensis.exe"
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            nsis_path = path
            break
    
    if nsis_path is None:
        print("NSIS (Nullsoft Scriptable Install System) not found.")
        print("Please download and install NSIS from https://nsis.sourceforge.io/Download")
        print("Then run this script again.")
        return
    
    # Run NSIS to create the installer
    try:
        subprocess.check_call([nsis_path, "installer.nsi"])
        print("Windows installer created successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error building Windows installer: {e}")
        return
    
    # Step 3: Final cleanup and instructions
    print("\nSTEP 3: Finalizing...")
    
    # Create a releases directory for the final installer
    if not os.path.exists("releases"):
        os.makedirs("releases")
    
    # Move the installer to the releases directory
    try:
        shutil.move("SecureSubmissionSystem-Setup.exe", 
                   os.path.join("releases", "SecureSubmissionSystem-Setup.exe"))
    except Exception as e:
        print(f"Error moving installer to releases directory: {e}")
    
    # Success!
    print("\n" + "=" * 70)
    print(" BUILD COMPLETED SUCCESSFULLY")
    print("=" * 70)
    print("\nInstaller created: releases/SecureSubmissionSystem-Setup.exe")
    print("\nTo distribute the application:")
    print("1. Share the installer file 'SecureSubmissionSystem-Setup.exe' with users")
    print("2. Users run the installer to set up the application")
    print("3. The application can be launched from the Start Menu or Desktop shortcut")
    
if __name__ == "__main__":
    build_windows_app()