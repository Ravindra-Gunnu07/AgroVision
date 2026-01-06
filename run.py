#!/usr/bin/env python
"""
AgroVision - Smart Farming Assistant
Quick start script for running the application
"""
import os
import sys

# Check if running from correct directory
if not os.path.exists('app.py'):
    print("❌ Error: app.py not found!")
    print("Please run this script from the AgroVision project directory.")
    sys.exit(1)

# Check for required files
required_files = ['plant_disease_model.h5', 'templates/index.html']
missing_files = [f for f in required_files if not os.path.exists(f)]

if missing_files:
    print("⚠️  Warning: Some files are missing:")
    for f in missing_files:
        print(f"   - {f}")

print("\n" + "=" * 50)
print("🌾 AgroVision - Smart Farming Assistant")
print("=" * 50)
print("\nStarting Flask server...")
print("\n📍 URLs:")
print("   Home:          http://127.0.0.1:5000/")
print("   Disease Detection: http://127.0.0.1:5000/detect")
print("   Government Schemes: http://127.0.0.1:5000/schemes")
print("   Voice Help:    http://127.0.0.1:5000/voice")
print("   Chatbot:       http://127.0.0.1:5000/chatbot")
print("\n" + "=" * 50)
print("Press Ctrl+C to stop the server\n")

# Run the app
if __name__ == "__main__":
    from app import app
    app.run(debug=True, host='0.0.0.0', port=5000)
