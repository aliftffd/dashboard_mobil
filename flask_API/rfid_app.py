import threading
import time
from flask import Flask, jsonify
from flask_socketio import SocketIO, emit
import csv
from datetime import datetime
from flask_cors import CORS
from serial import Serial
from motor import MotorController

class RFIDApplication:
    def __init__(self, motor_controller):
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app, cors_allowed_origins='*')
        CORS(self.app, origins=["http://localhost:5174"])
        self.motor_controller = motor_controller
        self.rfid_serial = self._initialize_serial()
        self.csv_file = 'rfid_log.csv'
        self._initialize_csv()

        @self.app.route('/')
        def index():
            return "RFID Motor Control WebSocket Server"

        @self.app.route('/health')
        def health():
            return jsonify(status="running"), 200

    def _initialize_serial(self):
        try:
            print("Initializing serial port...")
            return Serial('/dev/ttyUSB1', 115200, timeout=0.1)
        except Exception as e:
            print("Error initializing serial port:", e)
            return None

    def _initialize_csv(self):
        """Initialize the CSV file with headers if it doesn't already exist."""
        try:
            with open(self.csv_file, mode='a', newline='') as file:
                writer = csv.writer(file)
                if file.tell() == 0:  # Check if the file is emptysu
                    writer.writerow(['Timestamp', 'Tag ID', 'Name', 'Duty Cycle'])
        except Exception as e:
            print("Error initializing CSV file:", e)

    def log_to_csv(self, tag_id, name, duty_cycle):
        """Log RFID data to a CSV file."""
        try:
            with open(self.csv_file, mode='a', newline='') as file:
                writer = csv.writer(file)
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                writer.writerow([timestamp, tag_id, name, duty_cycle])
        except Exception as e:
            print("Error logging to CSV file:", e)

    def send_rfid_cmd(self, cmd):
        try:
            print(f"Sending RFID command: {cmd}")
            if self.rfid_serial and self.rfid_serial.is_open:
                self.rfid_serial.write(bytes.fromhex(cmd))
                response = self.rfid_serial.read(512)
                if response:
                    response_hex = response.hex().upper()
                    hex_list = [response_hex[i:i+2] for i in range(0, len(response_hex), 2)]
                    print(f"Received RFID response: {' '.join(hex_list)}")
                    return ' '.join(hex_list)
            return None
        except Exception as e:
            print("Error sending RFID command:", e)
            return None

    def rfid_motor_control(self):
        if self.rfid_serial is None:
            print("RFID serial port not initialized.")
            self.motor_controller.stop()
            return

        duty_cycle = 1.0
        self.motor_controller.set_motor_duty_cycle(duty_cycle)

        try:
            while True:
                try:
                    print("Waiting for RFID command...")
                    tag_data = self.send_rfid_cmd('BB 00 22 00 00 22 7E')
                    if tag_data:
                        if 'E2 00 20 23 12 05 EE AA 00 01 00 73' in tag_data or 'E2 00 20 23 12 N05 EE AA 00 01 00 87' in tag_data:
                            duty_cycle = 0.3
                            tag_id = 'E2 00 20 23 12 05 EE AA 00 01 00 73'
                            name = 'Tag 1'
                        elif 'E2 00 20 23 12 05 EE AA 00 01 00 76' in tag_data or 'E2 00 20 23 12 05 EE AA 00 01 00 88' in tag_data:
                            duty_cycle = 0.2
                            tag_id = 'E2 00 20 23 12 05 EE AA 00 01 00 76'
                            name = 'Tag 2'
                        elif 'E2 00 20 23 12 05 EE AA 00 01 00 90' in tag_data or 'E2 00 20 23 12 05 EE AA 00 01 00 85' in tag_data:
                            duty_cycle = 0
                            tag_id = 'E2 00 20 23 12 05 EE AA 00 01 00 90'
                            name = 'Tag 3'
                        else:
                            continue

                        print(f"Detected RFID tag: {tag_id}, Name: {name}, Duty Cycle: {duty_cycle}")
                        self.socketio.emit('rfid_data', {'name': name, 'tag_id': tag_id})
                        self.log_to_csv(tag_id, name, duty_cycle)

                    print(f"Setting motor duty cycle to: {duty_cycle}")
                    self.motor_controller.set_motor_duty_cycle(duty_cycle)
                    time.sleep(0.5)
                    print("Loop iteration completed")
                except Exception as e:
                    print("Error in RFID motor control loop:", e)
                    self.motor_controller.set_motor_duty_cycle(0)
                    break
        finally:
            if self.rfid_serial:
                self.rfid_serial.close()
            self.motor_controller.stop()

    def run_flask(self):
        try:
            print("Starting Flask server...")
            self.socketio.run(self.app, host='localhost', port=5000)
        except Exception as e:
            print("Error running Flask server:", e)

    def main(self):
        try:
            rfid_thread = threading.Thread(target=self.rfid_motor_control, daemon=True)
            rfid_thread.start()
            flask_thread = threading.Thread(target=self.run_flask, daemon=True)
            flask_thread.start()
            rfid_thread.join()
            flask_thread.join()
        except Exception as e:
            print("Error in main thread:", e)
            self.motor_controller.stop()

if __name__ == "__main__":
    motor_controller = MotorController(ena=8, in1=9, in2=10, enb=13, in3=11, in4=12)
    rfid_app = RFIDApplication(motor_controller)
    rfid_app.main()
