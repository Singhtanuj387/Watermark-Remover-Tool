#!/usr/bin/env python
"""
Verification script for Video Watermark Remover installation.
This script checks if all required components are properly installed and configured.
"""

import os
import sys
import subprocess
import platform
from importlib import util

def print_status(message, status):
    """Print a formatted status message."""
    status_text = "\033[92m✓ PASS\033[0m" if status else "\033[91m✗ FAIL\033[0m"
    print(f"{message:<60} {status_text}")
    return status

def check_python_version():
    """Check if Python version is compatible."""
    required_version = (3, 6)
    current_version = sys.version_info
    status = current_version >= required_version
    version_str = f"{current_version.major}.{current_version.minor}.{current_version.micro}"
    print_status(f"Python version (>= {required_version[0]}.{required_version[1]}) - found {version_str}", status)
    return status

def check_package(package_name):
    """Check if a Python package is installed."""
    spec = util.find_spec(package_name)
    status = spec is not None
    print_status(f"Package '{package_name}' is installed", status)
    return status

def check_ffmpeg():
    """Check if FFmpeg is installed and accessible."""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        status = result.returncode == 0
        version_info = result.stdout.split('\n')[0] if status else "Not found"
        print_status(f"FFmpeg installation - {version_info}", status)
        return status
    except FileNotFoundError:
        print_status("FFmpeg installation", False)
        return False

def check_directory(directory):
    """Check if a directory exists, create it if it doesn't."""
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
            print_status(f"Created directory '{directory}'", True)
        except Exception as e:
            print_status(f"Failed to create directory '{directory}': {e}", False)
            return False
    else:
        print_status(f"Directory '{directory}' exists", True)
    return True

def check_file_permissions(file_path):
    """Check if a file has correct permissions."""
    if not os.path.exists(file_path):
        print_status(f"File '{file_path}' does not exist", False)
        return False
    
    try:
        # Try to open the file for reading and writing
        with open(file_path, 'r') as f:
            pass
        status = True
        print_status(f"File '{file_path}' is readable", status)
        return status
    except Exception as e:
        print_status(f"File '{file_path}' permission check failed: {e}", False)
        return False

def main():
    """Run all verification checks."""
    print("\n===== Video Watermark Remover Installation Verification =====\n")
    
    # System checks
    print("\nSystem Checks:")
    print("-" * 70)
    system_status = True
    system_status &= check_python_version()
    system_status &= check_ffmpeg()
    
    # Package checks
    print("\nPackage Checks:")
    print("-" * 70)
    packages_status = True
    required_packages = [
        "flask", "cv2", "numpy", "scipy", "imageio", 
        "werkzeug", "dotenv", "ffmpeg"
    ]
    for package in required_packages:
        packages_status &= check_package(package)
    
    # Directory checks
    print("\nDirectory Checks:")
    print("-" * 70)
    directory_status = True
    required_directories = [
        "uploads", "processed", "static", "templates", "static/css"
    ]
    for directory in required_directories:
        directory_status &= check_directory(directory)
    
    # File permission checks
    print("\nFile Permission Checks:")
    print("-" * 70)
    file_status = True
    critical_files = [
        "app.py", "watermark_remover.py", "requirements.txt"
    ]
    for file in critical_files:
        if os.path.exists(file):
            file_status &= check_file_permissions(file)
        else:
            print_status(f"File '{file}' does not exist", False)
            file_status = False
    
    # Overall status
    print("\n===== Verification Summary =====\n")
    all_passed = system_status and packages_status and directory_status and file_status
    
    if all_passed:
        print("\033[92mAll checks passed! The installation appears to be correct.\033[0m")
        print("You can now run the application using 'python app.py'")
    else:
        print("\033[91mSome checks failed. Please fix the issues before running the application.\033[0m")
        print("Refer to the troubleshooting guide in docs/dependency_troubleshooting.md")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())