"""
Flask Application Entry Point for Vehicle Rental System.

This module initializes and runs the Flask web application.
"""

from flask import Flask
from controllers.routes import init_routes
import os

# Create Flask app
app = Flask(__name__)
app.secret_key = 'vehicle_rental_secret_key_2025'  # For session management

# Configure upload folder for vehicle images
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'images', 'vehicles')
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
