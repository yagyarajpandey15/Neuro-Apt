"""
WSGI entry point for production deployment.
This module exposes the Flask app object for gunicorn.
"""
import os
from neuroapt.app import create_app
from config import config

# Get configuration based on environment
env = os.environ.get('FLASK_ENV', 'production')
app_config = config.get(env, config['production'])

# Create Flask application instance
app = create_app(app_config)

if __name__ == "__main__":
    app.run()
