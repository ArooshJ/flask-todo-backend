import os
from dotenv import load_dotenv # <-- ADD THIS

# Get the base directory of the project
basedir = os.path.abspath(os.path.dirname(__file__))

# --- Load environment variables from .env file ---
# This line finds the .env file and loads it into os.environ
# It's smart and won't crash if the .env file is missing (e.g., in production)
load_dotenv() # <-- ADD THIS

class Config:
    """
    Base configuration class.
    
    SQLALCHEMY_DATABASE_URI:
    We now read this from an environment variable `DATABASE_URL`.
    This is critical for production on Elastic Beanstalk, which will
    provide this variable to connect to our RDS database.
    
    If `DATABASE_URL` is NOT set (e.g., when we're still testing locally),
    we'll fall back to using the local `app.db` SQLite file.
    """
    
    # Get the production DATABASE_URL from environment variables
    # Or, fall back to the local SQLite database for development
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(basedir, 'app.db')
    ).replace('postgres://', 'postgresql://') # Fix for Heroku/Render/some services

    SQLALCHEMY_TRACK_MODIFICATIONS = False