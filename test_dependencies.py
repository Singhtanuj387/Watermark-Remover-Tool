import sys
import pkg_resources

def check_dependencies():
    """Check if all required dependencies are installed and compatible."""
    print("Python version:", sys.version)
    
    required_packages = [
        'flask',
        'opencv-python',
        'numpy',
        'Werkzeug',
        'python-dotenv',
        'ffmpeg-python',
        'scipy',
        'imageio'
    ]
    
    print("\nChecking installed packages:")
    for package in required_packages:
        try:
            version = pkg_resources.get_distribution(package).version
            print(f"✓ {package}=={version}")
        except pkg_resources.DistributionNotFound:
            print(f"✗ {package} is not installed")
    
    print("\nTesting imports:")
    try:
        import flask
        print("✓ Flask imported successfully")
    except ImportError as e:
        print(f"✗ Flask import error: {e}")
    
    try:
        import cv2
        print("✓ OpenCV imported successfully")
    except ImportError as e:
        print(f"✗ OpenCV import error: {e}")
    
    try:
        import numpy
        print("✓ NumPy imported successfully")
    except ImportError as e:
        print(f"✗ NumPy import error: {e}")
    
    try:
        import scipy
        print("✓ SciPy imported successfully")
    except ImportError as e:
        print(f"✗ SciPy import error: {e}")
    
    try:
        import imageio
        print("✓ Imageio imported successfully")
    except ImportError as e:
        print(f"✗ Imageio import error: {e}")

if __name__ == "__main__":
    check_dependencies()