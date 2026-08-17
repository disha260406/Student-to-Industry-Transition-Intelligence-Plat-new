import sys
import os

# Add backend directory to path
backend_dir = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, os.path.abspath(backend_dir))

from app import create_app

app = create_app()

# Vercel expects the WSGI app to be named 'app'
