from flask import Flask, request, jsonify, render_template,send_from_directory
import os
from werkzeug.utils import secure_filename

from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = './'
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'text'}
line_Count = 1
versionflag = 0
maxCount = 0
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return "Ss"

@app.route('/GetFileData', methods=['GET'])
def funn():
    global line_Count
    global versionflag
    global maxCount
    line_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'Line.txt')
    if versionflag == 1:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'Boot.txt')

        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()

            lines = [line.strip() for line in lines]  # Remove any leading/trailing whitespace
            maxCount = len(lines)

            # Return the lines as plain text
            myData = ''.join(lines[line_Count - 1])
            line_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'Line.txt')
            with open(line_file_path, 'w') as line_file:
                line_file.write(myData)


            if myData == ":00000001FF":
                line_Count = 1
                versionflag = 0
                
                
                
                return myData, 200
            else:
                return myData, 200

        except FileNotFoundError:
            response = jsonify({'message': 'File not found'})
            return response, 404
    else:
        response = jsonify({'message': 'you are uptodate'})
        return response, 402





@app.route('/Line.txt', methods=['GET'])
def read_line_file():
    global line_Count
    global versionflag
    global maxCount
    line_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'Line.txt')
    if versionflag == 1:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'Boot.txt')

        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()

            lines = [line.strip() for line in lines]  # Remove any leading/trailing whitespace
            maxCount = len(lines)

            # Return the lines as plain text
            myData = ''.join(lines[line_Count - 1])
            line_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'Line.txt')
            with open(line_file_path, 'w') as line_file:
                line_file.write(myData)


            if myData == ":00000001FF":
                line_Count = 1
                versionflag = 0
                
                
                
                return send_from_directory(app.config['UPLOAD_FOLDER'], 'Line.txt'), 200
            else:
                return send_from_directory(app.config['UPLOAD_FOLDER'], 'Line.txt'), 200

        except FileNotFoundError:
            response = jsonify({'message': 'File not found'})
            return response, 404
    else:
        response = jsonify({'message': 'you are uptodate'})
        return response, 402
    




@app.route('/ok', methods=['POST'])
def IncreaseLine():
    global line_Count
    global maxCount
    global versionflag
    data = request.get_json()
    
    if 'CMD' in data:
        message = data['CMD']
        # Perform any desired operations with the message here
        # For example, you can print it
        print(message)
        if message == "1":
            line_Count = line_Count + 1
            if line_Count > maxCount:
                line_Count = 1
                versionflag = 0

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
    global versionflag

    if 'file' not in request.files:
        response = jsonify({'message': 'No file part in the request'})
        return response, 400
    line_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'Line.txt')
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'Boot.txt')
        file.save(file_path)
        response = jsonify({'message': 'File uploaded successfully', 'file_path': file_path})
        versionflag = 1
        return response, 200
    else:
        response = jsonify({'message': 'Invalid file type'})
        return response, 400
    
    


if __name__ == '__main__':
    app.run(debug=True)
