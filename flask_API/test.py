from flask import Flask, render_template
from flask_socketio import SocketIO
from serial import Serial
from flask_cors import CORS
import serial
import threading
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins='*')
CORS(app, origins=["http://localhost:5173"]) 

class RFIDReader:
    def __init__(self, port, baud_rate, callback):
        self.port = port
        self.baud_rate = baud_rate
        self.callback = callback
        self.serial_port = None
        self.initialize_serial()

    def initialize_serial(self):
        try:
            self.serial_port = Serial(self.port, self.baud_rate, timeout=1)
            print(f"Initialized RFID serial port: {self.port} at {self.baud_rate} baud rate")
        except Exception as e:
            print("Error initializing RFID serial port:", e)

    def send_rfid_cmd(self, cmd):
        try:
            if self.serial_port is not None and self.serial_port.is_open:
                data = bytes.fromhex(cmd)
                self.serial_port.write(data)
                response = self.serial_port.read(512)
                if response:
                    response_hex = response.hex().upper()
                    hex_list = [response_hex[i:i+2] for i in range(0, len(response_hex), 2)]
                    hex_space = ' '.join(hex_list)
                    return hex_space
                else:
                    return None
        except Exception as e:
            print("Error sending RFID command:", e)
            return None

    def read_tag(self):
        tag_data = self.send_rfid_cmd('BB 00 22 00 00 22 7E')
        if tag_data:
            print(f"Raw RFID tag data: {tag_data}")  # Log the raw tag data
            # Convert RFID response to detected tag
            timestamp = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
            if 'E2 00 20 23 12 05 EE AA 00 01 00 73' in tag_data:  # Tag 1
                self.callback(timestamp, "RFID Tag 1", 'E2 00 20 23 12 05 EE AA 00 01 00 73')
            elif 'E2 00 20 23 12 05 EE AA 00 01 00 76' in tag_data:  # Tag 2
                self.callback(timestamp, "RFID Tag 2", 'E2 00 20 23 12 05 EE AA 00 01 00 76')
            elif 'E2 00 20 23 12 05 EE AA 00 01 00 90' in tag_data:  # Tag 3
                self.callback(timestamp, "RFID Tag 3", 'E2 00 20 23 12 05 EE AA 00 01 00 90')
            else:
                print("No known RFID tags detected")
        else:
            print("No RFID tag data received")

class Readspeed:
    def __init__(self, port, baud_rate, callback):
        self.port = port
        self.baud_rate = baud_rate
        self.callback = callback
        self.serial_port = None
        self.initialize_serial()

    def initialize_serial(self):
        try:
            self.serial_port = serial.Serial(self.port, self.baud_rate)
            print(f"Initialized Speed serial port: {self.port} at {self.baud_rate} baud rate")
            self.stop_event = threading.Event()
            self.read_thread = threading.Thread(target=self.read_speed)
            self.read_thread.start()
        except Exception as e:
            print("Error initializing Speed serial port:", e)

    def read_speed(self):
        while not self.stop_event.is_set():
            line = self.serial_port.readline().decode('utf-8').strip()
            try:
                # Convert the line to float directly
                speed = float(line)
                self.callback(speed, "Speed Sensor")
            except ValueError:
                print(f"Unable to convert line to float: {line}")

    def stop(self):
        self.stop_event.set()
        self.read_thread.join()

@app.route('/')
def index():
    return render_template('index.html')

tag_info = []

def rfid_callback(timestamp, name, tag_id):
    tag_info.append((name, tag_id))
    socketio.emit('tag_update', {'name': name, 'tag_id': tag_id}, namespace='/')

def speed_callback(speed, name):
    socketio.emit('speed_update', {'name': name, 'speed': speed}, namespace='/')

rfidreader = RFIDReader('/dev/ttyUSB1', 115200, rfid_callback)
speedreader = Readspeed('/dev/ttyACM0', 115200, speed_callback)

if __name__ == "__main__":
    socketio.run(app, debug=True)
