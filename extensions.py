from flask_sqlalchemy import SQLAlchemy

# Create the database instance here, but don't initialize it with an app yet.
# This file will be imported by app.py, models.py, and run_migrations.py,
# preventing a circular dependency.
db = SQLAlchemy()