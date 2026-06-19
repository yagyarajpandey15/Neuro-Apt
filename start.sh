#!/usr/bin/env bash
# Start script for Render deployment
# This will be used instead of the manual command

echo "Starting Neuro-Apt with gunicorn..."
exec gunicorn wsgi:app --config gunicorn_config.py
