from serial import Serial
import time

port = '/dev/ttyUSB1'
baud_rate = 9600
timeout = 1

def initialize_serial(port, baud_rate, timeout):
    try:
        return Serial(port, baud_rate, timeout=timeout)
    except Exception as e:
        print("Error initializing serial port:", e)
        return None

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

def read_tag(serial_port):
    tag_data = send_rfid_cmd(serial_port, 'BB 00 22 00 00 22 7E')
    if tag_data:
        # Convert RFID response to detected tag
        if 'E2 00 20 23 12 05 EE AA 00 01 00 73' in tag_data:  # Tag 1
            return print("Tag 1 detected")
        elif 'E2 00 20 23 12 05 EE AA 00 01 00 76' in tag_data:  # Tag 2
            return print("Tag 2 detected")
        elif 'E2 00 20 23 12 05 EE AA 00 01 00 90' in tag_data:  # Tag 3
            return print("Tag 3 detected")
    return None

if __name__ == "__main__":
    serial_port = initialize_serial(port, baud_rate, timeout)
    while True:
        tag = read_tag(serial_port)
        if tag:
            print(tag)
        time.sleep(0.1)  # Wait for 0.1 second before reading RFID again