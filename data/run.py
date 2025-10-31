"""
Flask Application Entry Point for Vehicle Rental System.

This module initializes and runs the Flask web application.
"""

import sys
import os

# IMPORTANT: Get the absolute directory where THIS script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Force Python to use THIS directory first for imports
sys.path.insert(0, BASE_DIR)

# Change working directory to script location to ensure correct path resolution
os.chdir(BASE_DIR)

print(f"[DEBUG] Working Directory: {os.getcwd()}")
print(f"[DEBUG] Base Directory: {BASE_DIR}")
print(f"[DEBUG] Templates Directory: {os.path.join(BASE_DIR, 'templates')}")

from flask import Flask
from controllers.routes import init_routes

# Create Flask app with ABSOLUTE paths
app = Flask(__name__,
            template_folder=os.path.join(BASE_DIR, 'templates'),
            static_folder=os.path.join(BASE_DIR, 'static'))
app.secret_key = 'vehicle_rental_secret_key_2025'  # For session management

# Configure upload folder for vehicle images (use absolute path)
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'static', 'images', 'vehicles')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize routes
init_routes(app)

if __name__ == '__main__':
    # Create upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Run the application
    print("="*60)
    print("Vehicle Rental System - Starting...")
    print("Access the application at: http://127.0.0.1:5000")
    print("="*60)
    
    app.run(debug=True, host='127.0.0.1', port=5000)
