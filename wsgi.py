"""
WSGI entry point for Render deployment.
This module exposes the Flask app object for gunicorn.
"""
from neuroapt.app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
