# Transmitter
import time
import serial
from shared_resources import data_queue
from bme280Data import read_bme280, calculate_altitude  # Import the functions to read from the BME280 sensor and calculate altitude

# Uncomment suitable line for your Pi and comment the other which is not required 
'''For Raspberry Pi 4 & 3'''
lora = serial.Serial(port='/dev/ttyS0', baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)

'''For Raspberry Pi 5'''
# lora = serial.Serial(port='/dev/ttyAMA0', baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)

def loraTX_running():
    try:
        while not stop_event.is_set():
                if not data_queue.empty():
                    data = data_queue.get()
                #Get weather data from the BME280 sensor
                temperature, pressure, humidity = read_bme280()  # Assuming this function returns temperature, pressure, and humidity
                altitude = calculate_altitude(pressure)  #Calculate altitude based on pressure
                #Format the data as a string
                data = f"Temperature: {temperature}°C, Pressure: {pressure} hPa, Humidity: {humidity}%, Altitude: {altitude} m"
                b = bytes(data, 'utf-8')  #Convert string into bytes
                lora.write(b)  #Send the data to the other LoRa
                print(f"Sent: {data}")
            
            time.sleep(0.2)  # Delay of 200ms

except Exception as e:
        print(f"[LoRa TX] Error: {e}")
