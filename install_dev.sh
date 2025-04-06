#!/bin/bash
# Install the package in development mode

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Update pip
pip install --upgrade pip

# Install development dependencies
pip install pytest

# Install the package in development mode
pip install -e .

echo "CountGPT installed in development mode."
echo "You can now run: venv/bin/countgpt example.txt"
echo "Or activate the environment with: source venv/bin/activate"
echo "Or run: venv/bin/countgpt --list-models"