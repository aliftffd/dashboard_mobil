from serial import Serial
import time
from datetime import datetime

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
            print(f"Initialized serial port: {self.port} at {self.baud_rate} baud rate")
        except Exception as e:
            print("Error initializing serial port:", e)

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
            print(f"Raw tag data: {tag_data}")  # Log the raw tag data
            # Convert RFID response to detected tag
            timestamp = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
            if 'E2 00 20 23 12 05 EE AA 00 01 00 73' in tag_data:  # Tag 1
                self.callback(timestamp, "Tag 1", 'E2 00 20 23 12 05 EE AA 00 01 00 73')
            elif 'E2 00 20 23 12 05 EE AA 00 01 00 76' in tag_data:  # Tag 2
                self.callback(timestamp, "Tag 2", 'E2 00 20 23 12 05 EE AA 00 01 00 76')
            elif 'E2 00 20 23 12 05 EE AA 00 01 00 90' in tag_data:  # Tag 3
                self.callback(timestamp, "Tag 3", 'E2 00 20 23 12 05 EE AA 00 01 00 90')
            else:
                print("No known tags detected")
        else:
            print("No tag data received")

if __name__ == "__main__":
    def rfid_callback(timestamp, name, tag_id):
        print(f"RFID Callback - Timestamp: {timestamp}, Name: {name}, Tag ID: {tag_id}")

    reader = RFIDReader('/dev/ttyUSB1', 115200, rfid_callback)
    while True:
        reader.read_tag()
        time.sleep(0.01)  # Wait for 0.1 second before reading RFID again
