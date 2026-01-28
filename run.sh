#!/bin/bash

echo "🚀 Starting SPY Iron Condor Pro..."
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+ first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 not found. Please install pip first."
    exit 1
fi

# Install requirements
echo "📦 Installing required packages..."
pip3 install -q -r requirements.txt

if [ $? -ne 0 ]; then
    echo "⚠️ Some packages failed to install. Trying again..."
    pip3 install --upgrade pip
    pip3 install -r requirements.txt
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 Opening app at http://localhost:8501"
echo "📊 Press Ctrl+C to stop the app"
echo ""
sleep 2

# Run Streamlit app
streamlit run app.py
