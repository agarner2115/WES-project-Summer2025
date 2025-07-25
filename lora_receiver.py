import serial
import time
from datetime import datetime
import os
import subprocess
from plotter import parse_and_plot, handle_ai_detection

# Setup serial port (adjust device if needed)
try:
    lora = serial.Serial(
        port='/dev/ttyUSB0',
        baudrate=9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
    )
except serial.SerialException as e:
    print(f"[LoRa RX] Could not open serial port: {e}")
    print("Check USB connection, port name, and permissions.")
    exit(1)

# Directories to look for executable scripts (for "run script.py" commands)
search_directories = ['/home/intern/WES_env/Lora-HAT', os.getcwd()]

def loraRX_running():
    print("[LoRa RX] Listening for incoming data...")
    buffer = ""
    try:
        while True:
            try:
                incoming_bytes = lora.readline()
                if incoming_bytes:
                    line = incoming_bytes.decode('utf-8', errors='replace').strip()
                    print(f"[LoRa RX] Received: {line}")  # Debug: Show received line
                    buffer += line + '\n'  # Add line to buffer with newline

                # Process all complete lines
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    line = line.strip()
                    print(f"[LoRa RX] Processing line: {line}")  # Debug: Show line being processed
                    
                    # Initialize script_found/name before the if statement
                    script_found = False
                    script_name = None

                    # Handle remote command to run a script
                    if line.startswith("run"):
                        script_name = line[4:].strip()
                        script_found = False
                        for directory in search_directories:
                            script_path = os.path.join(directory, script_name)
                            if os.path.exists(script_path):
                                script_found = True
                                print(f"[LoRa RX] Running script: {script_path}")
                                try:
                                    result = subprocess.run(
                                        ['python3', script_path],
                                        capture_output=True, text=True, check=True
                                    )
                                    print(f"[LoRa RX] Script output:\n{result.stdout}")
                                    if result.stderr:
                                        print(f"[LoRa RX] Script error output:\n{result.stderr}")
                                except subprocess.CalledProcessError as e:
                                    print(f"[LoRa RX] Script failed: {e}")
                                break  # Exit the loop after running the script
                        if not script_found:
                            print(f"[LoRa RX] Script '{script_name}' not found.")

                    # Handle AI detection messages
                    elif "/detected_" in line and line.endswith(".jpg"):
                        print("\n")  # Add a blank line for easy readabilty
                        print(f"[LoRa RX] AI Detection message received: {line}")  # Debug: Show AI detection message
                        handle_ai_detection(line)
                    
                    # Handle sensor data lines
                    elif line.startswith("Temperature:"):
                        print("\n")  # Add a blank line for easy readabilty
                        parse_and_plot(line) 

                    else:
                        print(f"[LoRa RX] Unrecognized message: {line}")

                time.sleep(0.1)

            except Exception as e:
                print(f"[LoRa RX] Error: {e}")
    except KeyboardInterrupt:
        print("\n[LoRa RX] Stopped by user.")
    finally:
        if lora.is_open:
            lora.close()
            print("[LoRa RX] Serial port closed.")

if __name__ == "__main__":
    loraRX_running()
