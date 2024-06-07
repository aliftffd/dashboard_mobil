import csv
import json
import threading
import logging
from flask import Flask, request
from flask_socketio import SocketIO
from flask_cors import CORS
from threading import Lock
from datetime import datetime
from time import sleep
from radar import Readspeed  # Ensure this is the correct import

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'donsky!'
socketio = SocketIO(app, cors_allowed_origins='*')
CORS(app, origins=["http://localhost:5174"])  # Allow requests from Vite React frontend

thread = None
thread_lock = Lock()

shared_data = {
    'timestamp': None,
    'value': None,
}

csv_file = 'sensor_data_log.csv'

def initialize_csv():
    """Initialize the CSV file with headers if it doesn't exist."""
    try:
        with open(csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            if file.tell() == 0:  # Check if the file is empty
                writer.writerow(['Timestamp', 'Value'])
    except Exception as e:
        logging.error(f"Error initializing CSV file: {e}")

def log_to_csv(data):
    """Log shared data to the CSV file."""
    try:
        with open(csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([data['timestamp'], data['value']])
    except Exception as e:
        logging.error(f"Error logging to CSV file: {e}")

def get_current_datetime():
    now = datetime.now()
    return now.strftime("%m/%d/%Y %H:%M:%S")

def speed_callback(speed):
    with thread_lock:
        shared_data['value'] = speed
        shared_data['timestamp'] = get_current_datetime()
        logging.info(f"Speed Data: {shared_data}")
        socketio.emit('sensorData', json.dumps(shared_data))
        log_to_csv(shared_data)

# Initialize the sensors globally
readspeed = Readspeed('/dev/ttyACM0', 115200, speed_callback)
# rfidreader = RFIDReader('/dev/ttyUSB1', 115200, rfid_callback)

def background_thread():
    global readspeed  # Ensure this is accessible
    logging.info("Starting background thread for reading sensor values")
    while True:
        try:
            # Read speed sensor
            speed_thread = threading.Thread(target=readspeed.read_speed)
            speed_thread.start()
            speed_thread.join(timeout=1)  # Add a timeout

            if speed_thread.is_alive():
                logging.warning("Speed thread is taking too long. Stopping thread.")
                speed_thread.join()  # Ensure thread cleanup

        except serial.SerialException as e:
            logging.error(f"SerialException: {e}")
            readspeed.serial_port.close()
            sleep(0.01)
            readspeed.serial_port.open()
        except Exception as e:
            logging.error(f"Error in background thread: {e}")
            break

@app.route('/')
def index():
    return "Data endpoint"

@socketio.on('connect')
def connect(auth):
    global thread
    logging.info('Client connected')

    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)

@socketio.on('disconnect')
def disconnect():
    logging.info(f'Client disconnected: {request.sid}')

if __name__ == '__main__':
    initialize_csv()  # Initialize the CSV file
    try:
        socketio.run(app, host='localhost', port=5004)
    except Exception as e:
        logging.error(f"Error running app: {e}")
