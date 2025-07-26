#!/bin/bash

echo "Video Watermark Remover"
echo "====================="
echo ""

show_menu() {
    echo "Choose an option:"
    echo "1. Start the application"
    echo "2. Verify installation"
    echo "3. Test dependencies"
    echo "4. Exit"
    echo ""
    read -p "Enter your choice (1-4): " choice
    
    case $choice in
        1) start_app ;;
        2) verify_install ;;
        3) test_dependencies ;;
        4) exit_app ;;
        *) 
            echo "Invalid choice. Please try again."
            echo ""
            show_menu
            ;;
    esac
}

start_app() {
    echo ""
    echo "Starting Video Watermark Remover..."
    echo ""

    # Check if Python is installed
    if ! command -v python3 &> /dev/null; then
        echo "Python 3 is not installed. Please install Python 3.8 or higher."
        echo "Visit https://www.python.org/downloads/ to download Python."
        read -p "Press Enter to continue..."
        show_menu
        return
    fi

    # Check if virtual environment exists, if not create it
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
        if [ $? -ne 0 ]; then
            echo "Failed to create virtual environment."
            read -p "Press Enter to continue..."
            show_menu
            return
        fi
    fi

    # Activate virtual environment and install dependencies
    echo "Activating virtual environment and installing dependencies..."
    source venv/bin/activate

    # Install dependencies with better error handling
    echo "Installing dependencies..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo ""
        echo "There was an error installing dependencies."
        echo "If you're experiencing issues with numpy or other packages, try:"
        echo "1. Make sure you have the latest pip: pip install --upgrade pip"
        echo "2. If you have build tools issues, install required development packages:"
        echo "   For Ubuntu/Debian: sudo apt-get install python3-dev build-essential"
        echo "   For Fedora/RHEL: sudo dnf install python3-devel gcc"
        echo "3. Try installing packages one by one to identify problematic dependencies"
        echo ""
        read -p "Press Enter to continue..."
        deactivate
        show_menu
        return
    fi

    # Run the Flask application
    echo "Starting the application..."
    python app.py

    # Deactivate virtual environment when the application is closed
    deactivate
    
    read -p "Press Enter to continue..."
    show_menu
}

verify_install() {
    echo ""
    echo "Verifying installation..."
    echo ""

    # Check if Python is installed
    if ! command -v python3 &> /dev/null; then
        echo "Python 3 is not installed. Please install Python 3.8 or higher."
        echo "Visit https://www.python.org/downloads/ to download Python."
        read -p "Press Enter to continue..."
        show_menu
        return
    fi

    # Check if virtual environment exists, if not create it
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
        if [ $? -ne 0 ]; then
            echo "Failed to create virtual environment."
            read -p "Press Enter to continue..."
            show_menu
            return
        fi
    fi

    # Activate virtual environment
    source venv/bin/activate

    # Run verification script
    python verify_installation.py

    # Deactivate virtual environment
    deactivate
    
    read -p "Press Enter to continue..."
    show_menu
}

test_dependencies() {
    echo ""
    echo "Testing dependencies..."
    echo ""

    # Check if Python is installed
    if ! command -v python3 &> /dev/null; then
        echo "Python 3 is not installed. Please install Python 3.8 or higher."
        echo "Visit https://www.python.org/downloads/ to download Python."
        read -p "Press Enter to continue..."
        show_menu
        return
    fi

    # Check if virtual environment exists, if not create it
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
        if [ $? -ne 0 ]; then
            echo "Failed to create virtual environment."
            read -p "Press Enter to continue..."
            show_menu
            return
        fi
    fi

    # Activate virtual environment
    source venv/bin/activate

    # Run dependency test script
    python test_dependencies.py

    # Deactivate virtual environment
    deactivate
    
    read -p "Press Enter to continue..."
    show_menu
}

exit_app() {
    echo ""
    echo "Thank you for using Video Watermark Remover!"
    echo ""
    exit 0
}

# Start the menu
show_menu