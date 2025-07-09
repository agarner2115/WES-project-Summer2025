import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as mdates
import csv
import os

# Data Storage
timestamps = []
temp_values = []
humidity_values = []
pressure_values = []
altitude_values = []

# CSV Setup
csv_filename = "bme280_data_log.csv"
if not os.path.exists(csv_filename):
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Temperature (°C)", "Humidity (%)", "Pressure (hPa)", "Altitude (m)"])

def log_to_csv(timestamp, temp, humidity, pressure, altitude):
    with open(csv_filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp.strftime("%Y-%m-%d %H:%M:%S"), temp, humidity, pressure, altitude])

# Live Plot Setup
plt.ion()
fig, axs = plt.subplots(4, 1, sharex=True, figsize=(10, 10))
fig.suptitle('Real-time BME280 Sensor Readings')

axs[0].set_ylabel('Temperature (°C)')
axs[1].set_ylabel('Humidity (%)')
axs[2].set_ylabel('Pressure (hPa)')
axs[3].set_ylabel('Altitude (m)')
axs[-1].set_xlabel('Time')

def update_plot():
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

def parse_and_plot(data_line: str):
    try:
        # Parse example: "Temperature: 24.56°C, Pressure: 1009.8 hPa, Humidity: 46.2%, Altitude: 96.4 m"
        parts = data_line.split(',')
        temp = float(parts[0].split(':')[1].replace('°C', '').strip())
        pressure = float(parts[1].split(':')[1].replace('hPa', '').strip())
        humidity = float(parts[2].split(':')[1].replace('%', '').strip())
        altitude = float(parts[3].split(':')[1].replace('m', '').strip())
        timestamp = datetime.now()

        # Store and trim history
        timestamps.append(timestamp)
        temp_values.append(temp)
        humidity_values.append(humidity)
        pressure_values.append(pressure)
        altitude_values.append(altitude)

        N = 50
        if len(timestamps) > N:
            timestamps.pop(0)
            temp_values.pop(0)
            humidity_values.pop(0)
            pressure_values.pop(0)
            altitude_values.pop(0)

        # Log to CSV
        log_to_csv(timestamp, temp, humidity, pressure, altitude)

        # Update live plot
        update_plot()

    except Exception as e:
        print(f"[Plotter] Failed to parse data: {data_line}\nError: {e}")
