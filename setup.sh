#!/bin/bash
# Quick setup script for InvestSwarm

echo "=================================="
echo "InvestSwarm Setup"
echo "=================================="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
required_version="3.8"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3,8) else 1)" 2>/dev/null; then
    echo "Error: Python 3.8 or higher is required"
    echo "Current version: $(python3 --version)"
    exit 1
fi

echo "Python version check passed"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "Dependencies installed successfully"
else
    echo "Failed to install dependencies"
    exit 1
fi

# Setup .env file
echo ""
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ".env file created"
    echo ""
    echo "IMPORTANT: Edit .env and add your DEDALUS_API_KEY"
    echo "Get your API key at: https://dedaluslabs.ai"
else
    echo ".env file already exists"
fi

# Make main.py executable
chmod +x main.py
echo "Made main.py executable"

echo ""
echo "=================================="
echo "Setup Complete"
echo "=================================="
echo ""
echo "Edit .env and add your DEDALUS_API_KEY"
echo "Run: python main.py TICKER"
echo ""
