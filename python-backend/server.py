from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import sqlite3
import os

app = Flask(__name__)
CORS(app) 

# --- CONFIGURATION ---
DB_FILE = 'users.db'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Users Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            age INTEGER NOT NULL,
            designation TEXT,
            experience TEXT
        )
    ''')

    # Projects Table (NEW)
    c.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT NOT NULL,
            description TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database {DB_FILE} initialized.")

init_db()

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return "Python Backend is Running!"

# --- USER ROUTES ---
@app.route('/api/v1/users/save', methods=['POST'])
def save_user():
    try:
        data = request.json
        conn = get_db_connection()
        c = conn.cursor()
        c.execute(
            "INSERT INTO users (email, age, designation, experience) VALUES (?, ?, ?, ?)", 
            (data.get('email'), data.get('age'), data.get('designation'), data.get('experience'))
        )
        conn.commit()
        conn.close()
        return jsonify({"message": "User saved successfully!", "status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/users', methods=['GET'])
def get_users():
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users ORDER BY id DESC")
        rows = c.fetchall()
        conn.close()
        return jsonify([dict(row) for row in rows]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        return jsonify({"message": "User deleted", "status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- PROJECT ROUTES (NEW) ---
@app.route('/api/v1/projects', methods=['GET'])
def get_projects():
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM projects ORDER BY id DESC")
        rows = c.fetchall()
        conn.close()
        return jsonify([dict(row) for row in rows]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/projects', methods=['POST'])
def add_project():
    try:
        data = request.json
        conn = get_db_connection()
        c = conn.cursor()
        c.execute(
            "INSERT INTO projects (name, url, description) VALUES (?, ?, ?)", 
            (data.get('name'), data.get('url'), data.get('description'))
        )
        conn.commit()
        conn.close()
        return jsonify({"message": "Project added", "status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/projects/<int:id>', methods=['DELETE'])
def delete_project(id):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("DELETE FROM projects WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        return jsonify({"message": "Project deleted", "status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- IMAGE ROUTES ---
@app.route('/api/v1/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({"message": "File uploaded successfully", "filename": filename}), 200
    return jsonify({"error": "File type not allowed"}), 400

@app.route('/api/v1/images', methods=['GET'])
def get_images():
    try:
        images = os.listdir(app.config['UPLOAD_FOLDER'])
        return jsonify(images), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    print("Starting Flask Server on port 5000...")
    # app.run(port=5000, debug=True)
    app.run(host='0.0.0.0', port=5000)