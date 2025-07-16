import time
from datetime import datetime
import smbus2
import bme280

from shared_resources import data_queue, stop_event

#Constants
I2C_BUS = smbus2.SMBus(1)  #I2C bus 1 (default for Raspberry Pi)
BME280_ADDRESS = 0x76      #Default I2C address for BME280
SENSOR_ID = "BME280-01"    #Optional ID for logging
SEA_LEVEL_PRESSURE = 1013.25  #Standard sea level pressure in hPa

#Class for SensorData
class SensorData:
    def __init__(self, timestamp, temperature, humidity, pressure, altitude, sensor_id):
        self.timestamp = timestamp
        self.temperature = temperature
        self.humidity = humidity
        self.pressure = pressure
        self.altitude = altitude
        self.sensor_id = sensor_id

def read_bme280():
    #Use global I2C bus
    calibration_params = bme280.load_calibration_params(I2C_BUS, BME280_ADDRESS)
    data = bme280.sample(I2C_BUS, BME280_ADDRESS, calibration_params)
    return data.temperature, data.pressure, data.humidity

def calculate_altitude(pressure):
    #Calculate altitude in meters from pressure in hPa
    return (1 - (pressure / SEA_LEVEL_PRESSURE) ** (1 / 5.255)) * 44330.0

def BME_running(stop_event):
    try:
        while not stop_event.is_set():
                print('Reading sensor...')
                
                #Extract values
                temperature, pressure, humidity = read_bme280()  # Unpack the tuple
                altitude = calculate_altitude(pressure)  # Calculate altitude based on pressure
                timestamp = datetime.now()
                #data.sensor_id = SENSOR_ID

                #Create an instance of SensorData
                sensor_data = SensorData(timestamp, temperature, humidity, pressure, altitude, SENSOR_ID)

                #Output to console
                print(f"Sensor ID: {SENSOR_ID}")
                print(f"Timestamp: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"Temperature: {temperature:.2f} °C")
                print(f"Pressure: {pressure:.2f} hPa")
                print(f"Humidity: {humidity:.2f} %")
                print(f"Altitude: {altitude:.2f} m")
                print("-" * 40)
    
                data_queue.put(sensor_data)  # Put data in the queue
                time.sleep(10)  # Wait before next reading

    except KeyboardInterrupt:
        print("Program stopped by user.")
    except Exception as e:
        print(f"A BME280 error has occurred: {e}")
        #This code reads data from a BME280 sensor and plots the temperature, humidity, pressure, and altitude in real-time.
