
import serial
import json

# Define the serial port and baud rate
serial_port = '/dev/ttyACM0'  # Adjust this to your serial port
baud_rate = 115200  # Adjust this to your baud rate

# Create a serial object
ser = serial.Serial(serial_port, baud_rate)

try:
    # Loop indefinitely to read lines from the serial port
    while True:
        # Read a line from the serial port
        line = ser.readline().decode('utf-8').strip()
        
        # Parse the JSON-formatted data
        try:
            data = json.loads(line)
            
            # Print the parsed data
            print(data)
            
            # Access individual fields if needed
            # For example, if the JSON data has a field named 'value':
            # value = data['value']
            
        except json.JSONDecodeError as e:
            print("Error decoding JSON:", e)
            continue  # Skip this iteration if JSON decoding fails
        
except KeyboardInterrupt:
    # Close the serial port when the program is terminated
    ser.close()
    print("Serial port closed.")
except Exception as e:
    print("An error occurred:", e)
    ser.close()
