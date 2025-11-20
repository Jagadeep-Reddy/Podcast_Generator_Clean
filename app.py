from flask import Flask, render_template, request, jsonify, send_from_directory
from orchestrator import Orchestrator
import os
import uuid
import json
from datetime import datetime

print("DEBUG: app.py is starting...")

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Initialize Orchestrator
orchestrator = Orchestrator(app.config['OUTPUT_FOLDER'])

# In-memory storage for history (in a real app, use a database)
HISTORY_FILE = 'history.json'

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload-source', methods=['POST'])
def upload_source():
    if 'file' not in request.files and 'text' not in request.form:
        return jsonify({'error': 'No file or text provided'}), 400
    
    source_id = str(uuid.uuid4())
    content = ""
    
    if 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        filename = f"{source_id}_{file.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            content = f"File uploaded: {file.filename}"
    else:
        content = request.form['text']
        
    return jsonify({'source_id': source_id, 'content_preview': content[:200] + "...", 'full_content': content})

@app.route('/generate-podcast', methods=['POST'])
def generate_podcast():
    data = request.json
    source_content = data.get('source_content')
    topic = data.get('topic')
    voice = data.get('voice')
    
    context = {
        'source_content': source_content,
        'topic': topic,
        'voice': voice
    }
    
    job_id = orchestrator.start_job(context)
    return jsonify({'job_id': job_id})

@app.route('/podcast/status/<job_id>', methods=['GET'])
def get_status(job_id):
    status = orchestrator.get_job_status(job_id)
    if not status:
        return jsonify({'error': 'Job not found'}), 404
    
    response = {
        'status': status['status'],
        'current_step': status['current_step'],
        'steps_completed': status['steps_completed'],
        'result': status['result'],
        'error': status['error']
    }
    
    # If completed, save to history (simple hack for this demo)
    if status['status'] == 'completed' and not status.get('saved', False):
        podcast_data = {
            'id': job_id,
            'topic': status['context'].get('topic'),
            'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'script': status['result']['script'],
            'audio_url': status['result']['audio_url']
        }
        history = load_history()
        history.insert(0, podcast_data)
        save_history(history)
        status['saved'] = True # Prevent double saving
        
    return jsonify(response)

@app.route('/podcast/<id>', methods=['GET'])
def get_podcast(id):
    history = load_history()
    podcast = next((p for p in history if p['id'] == id), None)
    if podcast:
        return jsonify(podcast)
    return jsonify({'error': 'Not found'}), 404

@app.route('/history', methods=['GET'])
def get_history():
    return jsonify(load_history())

@app.route('/outputs/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
