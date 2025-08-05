#!/bin/bash

# Install Playwright browsers for scraping
echo "🚀 Installing Playwright browsers..."

# Navigate to scraper service directory
cd "$(dirname "$0")"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
playwright install chromium

# Install system dependencies for Playwright (Ubuntu/Debian)
echo "🔧 Installing system dependencies..."
playwright install-deps chromium

echo "✅ Playwright setup complete!"
echo ""
echo "🧪 To test the scraper, run:"
echo "   python test_scraper.py"
echo ""
echo "🚀 To start the service, run:"
echo "   python main.py"
