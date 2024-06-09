import serial
import time
import threading
import csv
from datetime import datetime

speed_port = '/dev/ttyACM0'
speed_baud_rate = 9600

rfid_port = '/dev/ttyUSB0'
rfid_baud_rate = 115200

csv_filename = 'kalibrasi.csv'

class ReadSpeed:
    def __init__(self, port, baud_rate, callback):
        self.serial_port = serial.Serial(port, baud_rate)
        self.stop_event = threading.Event()
        self.callback = callback

    def read_speed(self):
        while not self.stop_event.is_set():
            try:
                line = self.serial_port.readline().decode('utf-8').strip()
                if line:
                    try:
                        speed = float(line)
                        self.callback(speed)
                    except ValueError:
                        print(f"Unable to convert line to float: {line}")
                else:
                    print("No data received from the sensor.")
            except Exception as e:
                print(f"Error reading speed: {e}")
                self.stop_event.set()

class RfidReader:
    def __init__(self, port, baud_rate, callback):
        self.serial_port = serial.Serial(port, baud_rate)
        self.stop_event = threading.Event()
        self.callback = callback
        self.current_speed = 0.0  # Initialize current speed

    def read_tag(self):
        tag_names = {
            b'\xE2\x00\x20\x23\x12\x05\xEE\xAA\x00\x01\x00\x73': "TAG 1",
            b'\xE2\x00\x20\x23\x12\x05\xEE\xAA\x00\x01\x00\x76': "TAG 2",
            b'\xE2\x00\x20\x23\x12\x05\xEE\xAA\x00\x01\x00\x90': "TAG 3"
            b'\xE2\x00\x20\x23\x12\x05\xEE\xAA\x00\x01\x00\x87': "TAG 4"
            b'\xE2\x00\x20\x23\x12\x05\xEE\xAA\x00\x01\x00\x88': "TAG 5"
        }

        while not self.stop_event.is_set():
            command = b'\x43\x4D\x02\x02\x00\x00\x00\x00'
            self.serial_port.write(command)
            data = self.serial_port.read(26)

            if data:
                tag_detected = False
                for tag, name in tag_names.items():
                    if tag in data:
                        tag_detected = True
                        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        formatted_tag = self.format_tag_id(tag)
                        print(f"{name} detected: {formatted_tag} at {timestamp}")
                        self.callback(name, formatted_tag, timestamp, self.current_speed)
                        break
                if not tag_detected:
                    print("RFID is trying to read the ID")
            else:
                print("RFID is trying to read the ID")
            time.sleep(0.1)

    @staticmethod
    def format_tag_id(tag):
        return '-'.join(f"{byte:02X}" for byte in tag)

    def update_speed(self, speed):
        self.current_speed = speed

# Initialize CSV file with headers
def initialize_csv():
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Tag ID", "Speed"])

def speed_callback(speed):
    data = f"Speed: {speed} km/h"
    print(data)
    rfid_reader.update_speed(speed)  # Update the current speed in RFID reader

def tag_callback(tag_name, tag_id, timestamp, speed):
    data = f"Tag: {tag_name} with ID {tag_id} detected at {timestamp} with speed {speed} km/h"
    print(data)
    # Here you can call a function to send data to kalibrasi.py
    send_to_kalibrasi(tag_name, tag_id, timestamp, speed)

def send_to_kalibrasi(tag_name, tag_id, timestamp, speed):
    # Log the data to the CSV file
    with open(csv_filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, tag_id, speed])
    print(f"Logged to {csv_filename}: Tag {tag_name}, ID {tag_id}, Timestamp {timestamp}, Speed {speed}")

# Create instances of the readers
speed_reader = ReadSpeed(speed_port, speed_baud_rate, speed_callback)
rfid_reader = RfidReader(rfid_port, rfid_baud_rate, tag_callback)

# Run the readers in separate threads
speed_thread = threading.Thread(target=speed_reader.read_speed)
rfid_thread = threading.Thread(target=rfid_reader.read_tag)

# Initialize the CSV file
initialize_csv()

speed_thread.start()
rfid_thread.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopping threads...")
    speed_reader.stop_event.set()
    rfid_reader.stop_event.set()
    speed_thread.join()
    rfid_thread.join()
    print("Threads stopped gracefully.")
