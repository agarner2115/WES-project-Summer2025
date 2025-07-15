#receiver
import serial
import time
import os

from plotter import parse_and_plot

# Uncomment suitable line for your Pi and comment other which is not required 
'''For Raspberry Pi 4 & 3'''
lora = serial.Serial(port = '/dev/ttyUSB0', baudrate = 9600, parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE, bytesize = serial.EIGHTBITS, timeout = 1)

#Directories  to search for exexcutable Python scripts
search_directories = ['/home/intern/WES_env/WESproject', os.getcwd()]

def loraRX_running():
    print("[Lora Receiver] Listening for incoming data...")
    try:
        while True:
            if lora.in_waiting > 0:
                message = lora.read(lora.in_waiting).decode('utf-8', errors='replace').strip()
                print (f"Received Weather Data: {command}")
                
                #Handle remote script execution
                if message.startswith("run"):
                    script_name = message[4:].strip()
                    script_found = False
                    
                    for directory in search_directories:
                        script_path = os.path.join(directory, script_name)
                        script_found = True
                        output = os.popen(f"python3 {script_path}").read()
                        print(f"[Executed] Output of {script_name}:\n{output}")
                        break
                        
                    if not script_found:
                        print(f"[Error] Script'{script_name}' not found.")
                        
                #Otherwise, treat it as sensor data for plotting
                else:
                    parse_and_plot(message)
                time.sleep(0.2)
    except KeyboardInterrupt:
            print ("\n[LoRa RX] Stopped by user.")
    except Exception as e:
            print (f"[LoRa RX] Error: {e}")
