#Transmitter
import time
import serial

from shared_resources import data_queue

# Uncomment suitable line for your Pi and comment other which is not required 
'''For Raspberry Pi 4 & 3'''
lora = serial.Serial(port = '/dev/ttyS0', baudrate = 9600, parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE, bytesize = serial.EIGHTBITS, timeout = 1)

'''For Raspberry Pi 5'''
#lora = serial.Serial(port = '/dev/ttyAMA0', baudrate = 9600, parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE, bytesize = serial.EIGHTBITS, timeout = 1)

#def loraTX_running():
while True:
    if not data_queue.empty():
        data = data_queue.get()  # Get data from the queue
    n = input("Enter The Message = ")#input the string
    b = bytes(n,'utf-8')#convert string into bytes
    s = lora.write(b)#send the data to other lora
    print(s)
    time.sleep(0.2)#delay of 200ms
