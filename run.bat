@echo off
setlocal enabledelayedexpansion

echo Video Watermark Remover
echo =====================
echo.

:menu
echo Choose an option:
echo 1. Start the application
echo 2. Verify installation
echo 3. Test dependencies
echo 4. Exit
echo.

set /p choice=Enter your choice (1-4): 

if "%choice%"=="1" goto start_app
if "%choice%"=="2" goto verify_install
if "%choice%"=="3" goto test_dependencies
if "%choice%"=="4" goto end

echo Invalid choice. Please try again.
echo.
goto menu

:start_app
echo.
echo Starting Video Watermark Remover...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH. Please install Python 3.8 or higher.
    echo Visit https://www.python.org/downloads/ to download Python.
    pause
    exit /b 1
)

REM Check if virtual environment exists, if not create it
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
)

REM Activate virtual environment and install dependencies
echo Activating virtual environment and installing dependencies...
call venv\Scripts\activate.bat

REM Install dependencies with better error handling
echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo There was an error installing dependencies.
    echo If you're experiencing issues with numpy or other packages, try:
    echo 1. Make sure you have the latest pip: pip install --upgrade pip
    echo 2. If you have Visual C++ build tools issues, install Visual C++ Redistributable
    echo 3. Try installing packages one by one to identify problematic dependencies
    echo.
    pause
    exit /b 1
)

REM Run the Flask application
echo Starting the application...
python app.py

REM Deactivate virtual environment when the application is closed
call venv\Scripts\deactivate.bat

goto end

:verify_install
echo.
echo Verifying installation...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH. Please install Python 3.8 or higher.
    echo Visit https://www.python.org/downloads/ to download Python.
    pause
    goto menu
)

REM Check if virtual environment exists, if not create it
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment.
        pause
        goto menu
    )
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run verification script
python verify_installation.py

REM Deactivate virtual environment
call venv\Scripts\deactivate.bat

pause
goto menu

:test_dependencies
echo.
echo Testing dependencies...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH. Please install Python 3.8 or higher.
    echo Visit https://www.python.org/downloads/ to download Python.
    pause
    goto menu
)

REM Check if virtual environment exists, if not create it
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment.
        pause
        goto menu
    )
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run dependency test script
python test_dependencies.py

REM Deactivate virtual environment
call venv\Scripts\deactivate.bat

pause
goto menu

:end
echo.
echo Thank you for using Video Watermark Remover!
echo.
pause