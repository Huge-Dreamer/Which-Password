#!/bin/bash

echo "Setting up Which-Password..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python is not installed! Please install Python 3.7 or higher."
    echo "Download from: https://www.python.org/downloads/"
    exit 1
fi

# Check if 7-Zip is installed
if ! command -v 7z &> /dev/null; then
    echo "7-Zip is not installed! Please install 7-Zip."
    echo "Download from: https://www.7-zip.org/"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Install the package in development mode
echo "Installing Which-Password..."
pip install -e .

# Create necessary directories
mkdir -p extracted

# Copy default config if it doesn't exist
if [ ! -f "config/config.json" ]; then
    echo "Creating default config.json..."
    cp config/config.json.example config/config.json
fi

echo
echo "Installation complete!"
echo
echo "To use Which-Password:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run: which-password your_archive.rar --passwords PWD.txt"
echo 