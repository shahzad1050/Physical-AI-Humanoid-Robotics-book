"""
Vercel API handler for FastAPI application
This file allows FastAPI to run as a Vercel Serverless Function
"""
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the FastAPI app
from backend.app import app

# Export the app for Vercel
app_instance = app
__all__ = ['app_instance']
