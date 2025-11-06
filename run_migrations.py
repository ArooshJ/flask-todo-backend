from app import app
from extensions import db  # <-- This is the updated line
from models import Todo    # <-- Need to import models too

print("--- RUNNING MIGRATION SCRIPT ---")
try:
    with app.app_context():
        # This will create the 'todo' table
        db.create_all()
    print("Database tables created successfully (or already exist).")
    print("--- MIGRATION SCRIPT COMPLETE ---")
except Exception as e:
    print(f"Error during database migration: {str(e)}")