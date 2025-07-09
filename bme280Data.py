import time
from datetime import datetime
import smbus2
import bme280

from shared_resources import data_queue

#Constants
I2C_BUS = smbus2.SMBus(1)  #I2C bus 1 (default for Raspberry Pi)
BME280_ADDRESS = 0x76      #Default I2C address for BME280
SENSOR_ID = "BME280-01"    #Optional ID for logging
SEA_LEVEL_PRESSURE = 1013.25  #Standard sea level pressure in hPa

def read_bme280():
    #Use global I2C bus
    calibration_params = bme280.load_calibration_params(I2C_BUS, BME280_ADDRESS)
    data = bme280.sample(I2C_BUS, BME280_ADDRESS, calibration_params)
    return data

def calculate_altitude(pressure):
    """Calculate altitude in meters from pressure in hPa."""
    return (1 - (pressure / SEA_LEVEL_PRESSURE) ** (1 / 5.257)) * 44330.0

"""
#Lists to store data
timestamps = []
temp_values = []
humidity_values = []
pressure_values = []
altitude_values = []


#Setup plot
plt.ion()
fig, axs = plt.subplots(4, 1, sharex=True, figsize=(10, 10))
fig.suptitle('Real-time BME280 Sensor Readings')

axs[0].set_ylabel('Temperature (°C)')
axs[1].set_ylabel('Humidity (%)')
axs[2].set_ylabel('Pressure (hPa)')
axs[3].set_ylabel('Altitude (m)')

print('Made it through the plots...')
"""
def BME_running(stop_event):
    try:
        while not stop_event.is_set():
                print('Reading sensor...')
                data = read_bme280()
                
                #Extract values
                temp = data.temperature
                pressure = data.pressure
                humidity = data.humidity
                altitude = calculate_altitude(pressure)
                timestamp = datetime.now()
                data.sensor_id = SENSOR_ID
                """
                #Append to lists
                timestamps.append(timestamp)
                temp_values.append(temp)
                humidity_values.append(humidity)
                pressure_values.append(pressure)
                altitude_values.append(altitude)
    
                #Update plots
                for ax, values, label in zip(
                    axs,
                    [temp_values, humidity_values, pressure_values, altitude_values],
                    ['Temperature (°C)', 'Humidity (%)', 'Pressure (hPa)', 'Altitude (m)']
                ):
                    ax.clear()
                    ax.plot(timestamps, values, label=label)
                    ax.legend()
                    ax.set_ylabel(label)
    
                axs[-1].set_xlabel('Time')
                fig.autofmt_xdate(rotation=45)
                plt.pause(0.1)
                """
                #Output to console
                print(f"Sensor ID: {SENSOR_ID}")
                print(f"Timestamp: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"Temperature: {temp:.2f} °C")
                print(f"Pressure: {pressure:.2f} hPa")
                print(f"Humidity: {humidity:.2f} %")
                print(f"Altitude: {altitude:.2f} m")
                print("-" * 40)
    
                data_queue.put(data)  # Put data in the queue
                time.sleep(10)  # Wait before next reading

    except KeyboardInterrupt:
        print("Program stopped by user.")
    except Exception as e:
        print(f"A BME280 error has occurred: {e}")
        #This code reads data from a BME280 sensor and plots the temperature, humidity, pressure, and altitude in real-time.
