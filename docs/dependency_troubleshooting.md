# Dependency Troubleshooting Guide

This guide helps you resolve common dependency issues when installing and running the Video Watermark Remover application.

## Common Installation Issues

### NumPy Installation Errors

NumPy is a critical dependency for this application and often causes installation issues due to version compatibility problems.

#### Symptoms:
- Error messages containing `numpy.core.multiarray failed to import`
- Errors about API version mismatches
- Build errors during NumPy installation

#### Solutions:

1. **Upgrade pip to the latest version**:
   ```
   pip install --upgrade pip
   ```

2. **Install NumPy separately first**:
   ```
   pip install numpy==1.19.3
   ```

3. **Install Visual C++ Redistributable (Windows only)**:
   - Download and install from [Microsoft's website](https://support.microsoft.com/en-us/help/2977003/the-latest-supported-visual-c-downloads)

4. **Install development tools (Linux only)**:
   - For Ubuntu/Debian:
     ```
     sudo apt-get install python3-dev build-essential
     ```
   - For Fedora/RHEL:
     ```
     sudo dnf install python3-devel gcc
     ```

### OpenCV Installation Issues

#### Symptoms:
- Import errors with cv2
- DLL load failed errors on Windows
- Missing media features on Windows N/KN editions

#### Solutions:

1. **Install Visual C++ Redistributable (Windows)**:
   - Required for OpenCV to function properly

2. **Install Media Feature Pack (Windows N/KN editions)**:
   - Required for Windows N and KN editions which lack media components

3. **Try a different OpenCV version**:
   ```
   pip install opencv-python==4.5.5.62
   ```

### SciPy and Imageio Issues

#### Symptoms:
- Import errors
- Version compatibility issues

#### Solutions:

1. **Install compatible versions**:
   ```
   pip install scipy==1.7.0 imageio==2.9.0
   ```

## Step-by-Step Troubleshooting

1. **Clean your environment**:
   - Remove the virtual environment and create a new one
   - Windows: `rmdir /s /q venv && python -m venv venv`
   - Linux/macOS: `rm -rf venv && python3 -m venv venv`

2. **Install dependencies one by one**:
   ```
   pip install numpy==1.19.3
   pip install opencv-python==4.5.5.62
   pip install scipy==1.7.0
   pip install imageio==2.9.0
   pip install flask==2.0.1
   pip install Werkzeug==2.0.1
   pip install python-dotenv==0.19.0
   pip install ffmpeg-python==0.2.0
   ```

3. **Test imports**:
   ```python
   import numpy
   import cv2
   import scipy
   import imageio
   import flask
   ```

4. **Run the dependency test script**:
   ```
   python test_dependencies.py
   ```

## Using Pre-built Wheels

If you're still experiencing issues, you can try using pre-built wheels for problematic packages:

1. **For Windows**:
   - Visit [Unofficial Windows Binaries for Python](https://www.lfd.uci.edu/~gohlke/pythonlibs/)
   - Download the appropriate wheel files for your Python version
   - Install with: `pip install path/to/downloaded/wheel/file.whl`

2. **For Linux**:
   - Consider using your distribution's package manager
   - For example, on Ubuntu: `sudo apt-get install python3-numpy python3-opencv`

## Getting Help

If you're still experiencing issues after trying these solutions:

1. Check the error messages carefully for clues
2. Search for the specific error message online
3. Create an issue on the project's GitHub repository with detailed information about your system and the error