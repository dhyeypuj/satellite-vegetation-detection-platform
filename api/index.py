import sys
import os

# Ensure the project root directory is in the Python module search path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app import app

# Expose WSGI application for Vercel Python runtime
app = app
