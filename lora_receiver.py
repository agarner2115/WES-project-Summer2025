#receiver
import serial
import time
import os

'''For Raspberry Pi 4 & 3'''
lora = serial.Serial(port = '/dev/ttyS0', baudrate = 9600, parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE, bytesize = serial.EIGHTBITS, timeout = 1)

search_directories = ['/home/intern/WE#S_env/WESproject', os.getcwd()]

def loraRX_running():
    while True:
        if lora.in_waiting > 0: 
            command = lora.read(lora.in_waiting).decode('utf-8')
            print(f"Received Weather Data: {command}")
            
            try:
                if command.startswith("run "):
                    script_name = command[4:]
                    
                    script_found = False
                    
                    for directory in search_directories:
                        script_path = os.path.join(directory, script_name)
                        if os.path.isfile(script_path):
                            script_found = True
                            output = os.popen(f"python3 {script_path}").read()
                            print(f"Output: {output}")
                            break
                            
                    if not script_found:
                        print(f"Script not found")
                else:
                    print("Invalid Command")
            except Exception as e:
                print(f"Error executing command: {e}")
                
        time.sleep(0.2) 
