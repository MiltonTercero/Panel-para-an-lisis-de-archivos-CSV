#!/bin/bash
# EDA Panel - Launcher Script
# Double-click this file to run the application

cd "$(dirname "$0")"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
    
    echo "📦 Installing dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt
    
    echo "✅ Setup complete!"
else
    source venv/bin/activate
fi

echo "🚀 Starting EDA Panel..."
python main.py
