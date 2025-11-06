import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config
from extensions import db  # <-- 1. Import from new extensions.py file
from models import Todo     # <-- 4. Import models (safe to do now)

app = Flask(__name__)
app.config.from_object(Config)

# --- Initialize Extensions ---
db.init_app(app)  # <-- 2. Connect the db to the app
CORS(app)         # <-- 3. Add CORS

# --- API Endpoints ---

@app.route('/todos', methods=['GET'])
def get_todos():
    """Gets all todo items."""
    try:
        todos = db.session.execute(db.select(Todo)).scalars().all()
        return jsonify([todo.to_dict() for todo in todos]), 200
    except Exception as e:
        return jsonify({'error': f'Could not fetch from database: {str(e)}'}), 500

@app.route('/todos', methods=['POST'])
def create_todo():
    """Creates a new todo item."""
    data = request.get_json()
    if not data or 'task' not in data:
        return jsonify({'error': 'Missing task data'}), 400
        
    new_todo = Todo(task=data['task'], completed=False)
    
    try:
        db.session.add(new_todo)
        db.session.commit()
        return jsonify(new_todo.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Could not write to database: {str(e)}'}), 500

@app.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    """Gets a single todo item by ID."""
    try:
        todo = db.session.get(Todo, todo_id)
        if todo:
            return jsonify(todo.to_dict()), 200
        else:
            return jsonify({'error': 'Todo not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Could not fetch from database: {str(e)}'}), 500

@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """Updates a todo item (task content or completion status)."""
    todo = db.session.get(Todo, todo_id)
    if not todo:
        return jsonify({'error': 'Todo not found'}), 404
        
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No update data provided'}), 400

    try:
        if 'task' in data:
            todo.task = data['task']
        if 'completed' in data:
            todo.completed = data['completed']
            
        db.session.commit()
        return jsonify(todo.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Could not update database: {str(e)}'}), 500

@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """Deletes a todo item."""
    todo = db.session.get(Todo, todo_id)
    if not todo:
        return jsonify({'error': 'Todo not found'}), 404
        
    try:
        db.session.delete(todo)
        db.session.commit()
        return jsonify({'message': 'Todo deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Could not delete from database: {str(e)}'}), 500

# This is the entry point for running the app locally
# Gunicorn will bypass this and import the 'app' object directly
if __name__ == '__main__':
    app.run(debug=True, port=5000)