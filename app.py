from flask import Flask, request, jsonify, render_template
import os
from werkzeug.utils import secure_filename
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = './'
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'text'}
line_Count = 1

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return "Ss"

@app.route('/GetFileData', methods=['GET'])
def funn():
    global line_Count
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'Boot.txt')
    
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        lines = [line.strip() for line in lines]  # Remove any leading/trailing whitespace
        print (lines[0])
        # Return the lines as plain text
        myData=''.join(lines[line_Count-1])
        if myData == ":00000001FF":
            line_Count = 1
            return myData, 200
        else:
            return myData, 200
    
    except FileNotFoundError:
        response = jsonify({'message': 'File not found'})
        return response, 404

@app.route('/ok', methods=['POST'])
def IncreaseLine():
    global line_Count
    data = request.get_json()
    
    if 'CMD' in data:
        message = data['CMD']
        # Perform any desired operations with the message here
        # For example, you can print it
        print(message)
        if message == "1":
            line_Count = line_Count + 1
            # Return a response
            response = jsonify({'status': 'success', 'message': 'Message received','line':line_Count})
            return response, 200
        else:
            response = jsonify({'status': 'ERROR', 'message': 'Message received NOT COMPATABLE'})
            return response, 405
    else:
        response = jsonify({'status': 'error', 'message': 'No message found in request'})
        return response, 400



@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        response = jsonify({'message': 'No file part in the request'})
        return response, 400

    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'Boot.txt')
        file.save(file_path)
        response = jsonify({'message': 'File uploaded successfully', 'file_path': file_path})
        return response, 200
    else:
        response = jsonify({'message': 'Invalid file type'})
        return response, 400
    
    


if __name__ == '__main__':
    app.run(debug=True)
