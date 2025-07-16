#receiver
import serial
import time
import os
import subprocess

from plotter import parse_and_plot

# Uncomment suitable line for your Pi and comment other which is not required 
'''For Raspberry Pi 4 & 3'''
lora = None
try:
    lora = serial.Serial(port = '/dev/ttyUSB0', baudrate = 9600, parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE, bytesize = serial.EIGHTBITS, timeout = 1)
except serial.SerialException as e:
    print(f"[Error] Could not open serial port. {e}")
    print("Please check:")
    print("1. Is the LoRa modke connected to the correct USB port?")
    print("2. Is the port name '/dev/ttyUSB0' correct for your setup?")
    print("3. Do you have sufficient permissions? (Try: sudo usermod -a -G dialout $USER and reboot)")
    exit(1)

#Directories  to search for exexcutable Python scripts
search_directories = ['/home/intern/WES_env/WESproject', os.getcwd()]

def loraRX_running():
    print("[Lora Receiver] Listening for incoming data...")
    try:
        while True:
            if lora.in_waiting > 0:
                message = lora.read(lora.in_waiting).decode('utf-8', errors='replace').strip()
                print (f"Received LoRa Data: {message}")
                
                #Handle remote script execution
                if message.startswith("run"):
                    script_name = message[4:].strip()
                    script_found = False
                    
                    for directory in search_directories:
                        script_path = os.path.join(directory, script_name)
                        script_found = True
                        output = os.popen(f"python3 {script_path}").read()
                        print(f"[LoRa Receiver] Attempting to run script: {script_path}")
                        try:
                            result = subprocess.run(['python3', script_path], capture_output=True, text=True, check=True)
                            print(f"[Executed] Output of {script_name}:\n{result.stdout}")
                            if result.stderr:
                                print(f"[Executed] Error output for {script_name}:\n{result.stderr}")
                        except subprocess.CalledProcessError as e:
                            print(f"[Error] Script '{script_name}' failed wih exit code {e.returncode}:\n{e.stderr}")
                        except FileNotFoundError:
                            print(f"[Errpr] 'python3' command not found. Ensure Python s in your PATH.")
                        break
                    if not script_found:
                        print(f"[Error] Script '{script_name}' not foundd in any specified directory.")
                    
                elif message.startswith("AI_DETECTION:"):
                    handle_ai_detection(message)
                elif message.startswith("Temperature:"):
                    parse_and_plot(message)
                else:
                    print(f"[LoRa Receiver] Unrecognized message format: {message}")

            time.sleep(0.2)
            
    except KeyboardInterrupt:
            print ("\n[LoRa RX] Stopped by user.")
    except Exception as e:
            print (f"[LoRa RX] Error: {e}")
    finally:
        if lora and lora.is_open:
            lora.close()
            print("[LoRa RX] Serial port closed.")

if __name__ == "__main__":
    loraRX_running 
