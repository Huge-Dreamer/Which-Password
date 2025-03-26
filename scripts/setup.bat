@echo off
echo Setting up Which-Password...

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed! Please install Python 3.7 or higher.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Check if 7-Zip is installed
where 7z >nul 2>&1
if errorlevel 1 (
    echo 7-Zip is not installed! Please install 7-Zip.
    echo Download from: https://www.7-zip.org/
    pause
    exit /b 1
)

:: Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Upgrade pip
python -m pip install --upgrade pip

:: Install requirements
echo Installing dependencies...
pip install -r requirements.txt

:: Install the package in development mode
echo Installing Which-Password...
pip install -e .

:: Create necessary directories
if not exist extracted mkdir extracted

:: Copy default config if it doesn't exist
if not exist config\config.json (
    echo Creating default config.json...
    copy config\config.json.example config\config.json
)

echo.
echo Installation complete!
echo.
echo To use Which-Password:
echo 1. Activate the virtual environment: venv\Scripts\activate
echo 2. Run: which-password your_archive.rar --passwords PWD.txt
echo.
pause 