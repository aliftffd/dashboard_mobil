from flask import Flask
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import Jetson.GPIO as GPIO
import time
from serial import Serial
import threading
import json

# Define Jetson Nano pins
ENA = 33
IN1 = 35
IN2 = 37
ENB = 32
IN3 = 40
IN4 = 38

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')
CORS(app, origins=["http://localhost:5173"])
# Initialize GPIO
def initialize_gpio():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup([ENA, IN1, IN2, ENB, IN3, IN4], GPIO.OUT)

# Initialize Serial Port for RFID
def initialize_serial():
    try:
        return Serial('/dev/ttyUSB1', 115200, timeout=0.1)
    except Exception as e:
        print("Error initializing serial port:", e)
        return None

# Function to send RFID command and read response
def send_rfid_cmd(serial_port, cmd):
    try:
        if serial_port is not None and serial_port.is_open:
            data = bytes.fromhex(cmd)
            serial_port.write(data)
            response = serial_port.read(512)
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

# Function to set motor speed
def set_motor_speed(speed):
    speed = max(0, min(100, speed))  # Ensure speed value is within range 0 to 100

    if speed == 0:
        GPIO.output(ENA, GPIO.LOW)
        GPIO.output(ENB, GPIO.LOW)
    else:
        GPIO.output(ENA, GPIO.HIGH)
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN2, GPIO.LOW)
        GPIO.output(ENB, GPIO.HIGH)
        GPIO.output(IN3, GPIO.HIGH)
        GPIO.output(IN4, GPIO.LOW)

        pwm_period = 0.2  # PWM period in seconds (adjust as needed)
        pwm_value = speed / 100.0
        on_time = pwm_period * pwm_value
        off_time = pwm_period * (1 - pwm_value)

        GPIO.output(ENA, GPIO.HIGH)
        GPIO.output(ENB, GPIO.HIGH)
        time.sleep(on_time)
        GPIO.output(ENA, GPIO.LOW)
        GPIO.output(ENB, GPIO.LOW)

    print("Motor speed set to:", speed)

# Function to handle RFID reading and motor control
def rfid_motor_control():
    initialize_gpio()
    rfid_serial = initialize_serial()
    if rfid_serial is None:
        return

    set_motor_speed(100)
    last_speed = 100

    while True:
        tag_data = send_rfid_cmd(rfid_serial, 'BB 00 22 00 00 22 7E')
        if tag_data:
            if 'E2 00 20 23 12 05 EE AA 00 01 00 73' in tag_data:
                last_speed = 65
                tag_id = 'E2 00 20 23 12 05 EE AA 00 01 00 73'
                name = 'Tag 1'
            elif 'E2 00 20 23 12 05 EE AA 00 01 00 76' in tag_data:
                last_speed = 50
                tag_id = 'E2 00 20 23 12 05 EE AA 00 01 00 76'
                name = 'Tag 2'
            elif 'E2 00 20 23 12 05 EE AA 00 01 00 90' in tag_data:
                last_speed = 0
                tag_id = 'E2 00 20 23 12 05 EE AA 00 01 00 90'
                name = 'Tag 3'
            else:
                continue

            socketio.emit('rfid_data', {'name': name, 'tag_id': tag_id})
        
        set_motor_speed(last_speed)
        time.sleep(0.1)

# Flask route to handle the main page
@app.route('/')
def index():
    return "RFID Motor Control WebSocket Server"

# Main function
def main():
    rfid_thread = threading.Thread(target=rfid_motor_control)
    rfid_thread.start()
    socketio.run(app, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()
