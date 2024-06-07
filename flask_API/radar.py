import serial
import threading
import time

class Readspeed():
    def __init__(self, port, baud_rate, callback, timeout=1):
        self.serial_port = serial.Serial(port, baud_rate)
        self.stop_event = threading.Event()
        self.callback = callback
        self.timeout = timeout  # Timeout in seconds

    def read_speed(self):
        start_time = time.time()
        while not self.stop_event.is_set():
            if time.time() - start_time > self.timeout:
                print("Speed reading timed out. Stopping thread.")
                return
            line = self.serial_port.readline().decode('utf-8').strip()
            if line:  # Check if line is not empty
                try:
                    # Convert the line to float directly
                    speed = float(line)
                    self.callback(speed)
                except ValueError:
                    print(f"Unable to convert line to float: {line}")
            else:
                print("No data received from the sensor. Returning from read_speed.")
                return  # Return from the method if no data is received
    def stop(self):
        self.stop_event.set()
