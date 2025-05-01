# Secure Submission System - Windows Application Guide

This guide explains how to build and distribute the Secure Submission System as a standalone Windows desktop application.

## Prerequisites

To build the Windows application, you need:

1. **Windows Operating System** - The build process should be performed on a Windows machine
2. **Python 3.11 or newer** - Installed and configured with pip
3. **PyInstaller** - For packaging the Python application (`pip install pyinstaller`)
4. **NSIS (Nullsoft Scriptable Install System)** - For creating the Windows installer
   - Download from [NSIS website](https://nsis.sourceforge.io/Download)
   - Install to the default location (typically `C:\Program Files\NSIS` or `C:\Program Files (x86)\NSIS`)

## Build Process

The build process has been automated through several Python scripts:

### Option 1: Automated Build (Recommended)

1. Run the master build script:
   ```
   python build_windows_app.py
   ```

2. This script will:
   - Create the distribution package using PyInstaller
   - Build the Windows installer using NSIS
   - Place the final installer in the `releases` directory

### Option 2: Manual Build

If you prefer to execute the build steps manually:

1. Create the distribution package:
   ```
   python create_distribution.py
   ```

2. Build the Windows installer using NSIS:
   ```
   "C:\Program Files\NSIS\makensis.exe" installer.nsi
   ```
   or
   ```
   "C:\Program Files (x86)\NSIS\makensis.exe" installer.nsi
   ```

## Distribution

After building the application, you'll have a Windows installer file named `SecureSubmissionSystem-Setup.exe` in the `releases` directory.

### Distribution Options

1. **Direct Distribution**:
   - Share the installer file with users via email, file sharing, or USB drive
   - Users run the installer to set up the application on their computer

2. **Web Download**:
   - Host the installer file on your website or file sharing service
   - Provide users with a download link

3. **Enterprise Deployment**:
   - Use your organization's software deployment tools (e.g., Microsoft SCCM)
   - The installer supports silent installation via command line

## User Installation

When users receive the installer, they should:

1. Run the `SecureSubmissionSystem-Setup.exe` file
2. Follow the installation wizard prompts
3. Launch the application from the Start Menu or Desktop shortcut

## Application Data

The Windows application stores all data in the user's Documents folder under `SecureSubmissionSystem`:

- `%USERPROFILE%\Documents\SecureSubmissionSystem\submission_system.db` - SQLite database
- `%USERPROFILE%\Documents\SecureSubmissionSystem\uploads\` - Uploaded images

## Customization

To customize the Windows application:

1. **Application Name and Branding**:
   - Edit the `installer.nsi` file to change the application name, version, and company
   - Replace `static/favicon.ico` with your own icon file

2. **Installer Appearance**:
   - Add installer graphics to `static/installer-welcome.bmp` (164x314 pixels)
   - Customize the installer strings in `installer.nsi`

## Troubleshooting

Common issues and solutions:

1. **NSIS Not Found**:
   - Ensure NSIS is installed in one of the standard program directories
   - If installed elsewhere, update the path in `build_windows_app.py`

2. **PyInstaller Errors**:
   - Make sure all required Python packages are installed
   - Try running PyInstaller manually for more detailed error messages

3. **Application Won't Start**:
   - Check if another application is using port 5000
   - Ensure the user has sufficient permissions to write to their Documents folder

## Version Updates

When releasing a new version:

1. Update the version number in `installer.nsi`
2. Rebuild using the steps above
3. Distribute the new installer to users