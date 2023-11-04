from flask import Flask, request, jsonify, render_template,send_from_directory
import os
from werkzeug.utils import secure_filename
import time
from threading import Thread, Event
import paho.mqtt.client as mqtt
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
# MQTT broker configuration

mqtt_broker = "34.142.56.252"
mqtt_port = 1883

app.config['UPLOAD_FOLDER'] = './'
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'text'}
##mqtt vars
mqtt_subscribe_topic = "sensor/data"
mqtt_publish_topic = "control/device"
#general vars
line_Count = 1
versionflag = 0
maxCount = 0


message_ok_event = Event()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code " + str(rc))
    client.subscribe(mqtt_subscribe_topic)

def on_message(client, userdata, msg):
    print("Received MQTT message on topic " + msg.topic + ": " + str(msg.payload))


@app.route('/')
def index():
    return "Ss"

@app.route('/GetFileData', methods=['GET'])
def funn():
    global line_Count
    global versionflag
    global maxCount
    line_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'Line.txt')

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'Boot.txt')

    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()

        lines = [line.strip() for line in lines]  # Remove any leading/trailing whitespace
        maxCount = len(lines)
        line_Count = 0

        # Return the lines as plain text
        
        for line in lines:
            myData = line.strip()
            line_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'Line.txt')
            with open(line_file_path, 'w') as line_file:
                line_file.write(myData)
               
            mqtt_client.publish(mqtt_publish_topic, myData)
            mqtt_client.publish('sensor/data', 'NOK') 
            # Subscribe to the 'sensor/data' topic and wait for 'message ok' signal
            message_ok_event.clear()
            mqtt_client.subscribe('sensor/data', qos=1)
            mqtt_client.on_message = on_message
            message_ok_event.wait()  # Wait until the event is set (i.e., 'message ok' is received)
        
        mqtt_client.publish('update/data', '0') 
        return "All lines published successfully", 200

    except FileNotFoundError:
        response = jsonify({'message': 'File not found'})
        return response, 404


def on_message(client, userdata, msg):
    if msg.topic == 'sensor/data' and msg.payload.decode('utf-8') == 'ok':
        client.unsubscribe('sensor/data')
        message_ok_event.set()


# mqtt_client.on_connect = on_connect
# mqtt_client.connect(mqtt_broker_address, mqtt_broker_port, keepalive=60)
# mqtt_client.loop_start()

# Connect to the MQTT broker
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(mqtt_broker, mqtt_port, 60)

# Start the MQTT client in a background thread
mqtt_client.loop_start()



# @app.route('/Line.txt', methods=['GET'])
# def read_line_file():

#     return "okay from server"

    
#     # global line_Count
#     # global versionflag
#     # global maxCount
#     # line_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'Line.txt')
#     # if versionflag == 1:
#     #     file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'Boot.txt')

#     #     try:
#     #         with open(file_path, 'r') as file:
#     #             lines = file.readlines()

#     #         lines = [line.strip() for line in lines]  # Remove any leading/trailing whitespace
#     #         maxCount = len(lines)

#     #         # Return the lines as plain text
#     #         myData = ''.join(lines[line_Count - 1])
#     #         line_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'Line.txt')
#     #         with open(line_file_path, 'w') as line_file:
#     #             line_file.write(myData)


#     #         if myData == ":00000001FF":
#     #             line_Count = 1
#     #             versionflag = 0
                
                
                
#     #             return send_from_directory(app.config['UPLOAD_FOLDER'], 'Line.txt'), 200
#     #         else:
#     #             return send_from_directory(app.config['UPLOAD_FOLDER'], 'Line.txt'), 200

#     #     except FileNotFoundError:
#     #         response = jsonify({'message': 'File not found'})
#     #         return response, 404
#     # else:
#     #     response = jsonify({'message': 'you are uptodate'})
#     #     return response, 402
    




@app.route('/ok', methods=['GET'])
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
        mqtt_client.publish('update/data', '1')
        return response, 200
    else:
        response = jsonify({'message': 'Invalid file type'})
        return response, 400
    
    


if __name__ == '__main__':


    # Run the Flask application
    app.run(host='0.0.0.0', port=5000, debug=True)

#########################################

# from flask import Flask, request

# import paho.mqtt.client as mqtt

# app = Flask(__name__)

# # MQTT broker configuration
# mqtt_broker = "34.142.56.252"
# mqtt_port = 1883

# MQTT topics for publish and subscribe
# mqtt_subscribe_topic = "sensor/data"
# mqtt_publish_topic = "control/device"

# # MQTT callback functions
# def on_connect(client, userdata, flags, rc):
#     print("Connected to MQTT broker with result code " + str(rc))
#     client.subscribe(mqtt_subscribe_topic)

# def on_message(client, userdata, msg):
#     print("Received MQTT message on topic " + msg.topic + ": " + str(msg.payload))

@app.route('/sensor', methods=['POST'])
def receive_sensor_data():
    data = request.get_json()
    # Process the received sensor data
    # ...

    # Publish a response to the device
    response = "Data received successfully / " 
    mqtt_client.publish(mqtt_publish_topic, str(data))

    return "OK"

# if __name__ == '__main__':
#     # Connect to the MQTT broker
#     mqtt_client = mqtt.Client()
#     mqtt_client.on_connect = on_connect
#     mqtt_client.on_message = on_message
#     mqtt_client.connect(mqtt_broker, mqtt_port, 60)

#     # Start the MQTT client in a background thread
#     mqtt_client.loop_start()

#     # Run the Flask application
#     app.run(host='0.0.0.0', port=5000, debug=True)

