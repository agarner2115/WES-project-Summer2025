import matplotlib.pyplot as plt
from datetime import datetime
import time
import csv
import os

# Data buffers
timestamps, temp_values, humidity_values, pressure_values, altitude_values = [], [], [], [], []

# CSV files
bme_csv = "bme280_data_log_400.csv"
ai_csv = "ai_detection_log.csv"

# Create CSV files with headers if they don't exist
if not os.path.exists(bme_csv):
    with open(bme_csv, 'w', newline='') as f:
        csv.writer(f).writerow(["Timestamp", "Temperature (°C)", "Humidity (%)", "Pressure (hPa)", "Altitude (m)"])

if not os.path.exists(ai_csv):
    with open(ai_csv, 'w', newline='') as f:
        csv.writer(f).writerow(["Timestamp", "Detected Object", "Confidence"])

# Setup live plotting
plt.ion()
fig, axs = plt.subplots(4, 1, figsize=(10, 10), sharex=True)
fig.suptitle("Live BME280 Data")

labels = ['Temperature (°C)', 'Humidity (%)', 'Pressure (hPa)', 'Altitude (m)']
for ax, label in zip(axs, labels):
    ax.set_ylabel(label)
axs[-1].set_xlabel('Time')

def update_plot():
    for ax, values, label in zip(axs, [temp_values, humidity_values, pressure_values, altitude_values], labels):
        ax.clear()
        #Plot the line
        ax.plot(timestamps, values, label=label, color='tab:blue', linewidth=3)
        #Plot the dots
        ax.scatter(timestamps, values, color="tab:pink", s=30) 
        ax.set_ylabel(label)
        ax.legend(loc='upper left')
        ax.grid(True)
    fig.autofmt_xdate(rotation=45)
    plt.pause(0.1)	#Allow the plot to update

def log_to_csv(timestamp, temp, humidity, pressure, altitude):
    with open(bme_csv, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp.strftime("%Y-%m-%d %H:%M:%S"), temp, humidity, pressure, altitude])

def parse_and_plot(data_line: str):
    try:
        parts = data_line.split(',')
        # Support both "Temperature: xx°C" and raw csv format
        if "Temperature" in parts[0]:
            temp = float(parts[0].split(':')[1].replace('°C', '').strip())
            pressure = float(parts[1].split(':')[1].replace('hPa', '').strip())
            humidity = float(parts[2].split(':')[1].replace('%', '').strip())
            altitude = float(parts[3].split(':')[1].replace('m', '').strip())
        else:
            temp, pressure, humidity, altitude = map(float, map(str.strip, parts))

        timestamp = datetime.now()
        timestamps.append(timestamp)
        temp_values.append(temp)
        humidity_values.append(humidity)
        pressure_values.append(pressure)
        altitude_values.append(altitude)

        # Limit data length for performance
        max_points = 50
        if len(timestamps) > max_points:
            timestamps.pop(0)
            temp_values.pop(0)
            humidity_values.pop(0)
            pressure_values.pop(0)
            altitude_values.pop(0)

        # Update plot
        update_plot()
        
        # Log to CSV
        log_to_csv(timestamp, temp, humidity, pressure, altitude)


    except Exception as e:
        print(f"[Plotter] Error parsing/plotting data: {e} | Input: '{data_line}'")

def log_ai_detection_to_csv(timestamp, detected_object, confidence):
    with open(ai_csv, 'a', newline='') as f:
        csv.writer(f).writerow([timestamp.strftime("%Y-%m-%d %H:%M:%S"), detected_object, confidence])

def handle_ai_detection(ai_message_string: str):
    try:
        print(f"[AI Detection] Received message: {ai_message_string}")  # Debug: Show received message
        
        # Remove the "detected_images/" prefix
        content = ai_message_string.replace("detected_images/", "").strip()
        
        # Split the content to get the filename
        parts = content.split('_')  # Split by underscore
        
        if len(parts) < 4:  # Ensure there are enough parts
            raise ValueError("Incomplete AI detection data")

        # Extract detected object (second part) and confidence (fourth part)
        detected_object = parts[1]  # e.g., "cat"
        
        # Confidence is the number before .jpg, so we split it at '.' and take the first part
        confidence = float(parts[3].split('.')[0])  # e.g., "56" (before the .jpg)

        # Get live timestamp
        timestamp = datetime.now()
        
        print(f"[AI Detection] Detected '{detected_object}' with confidence {confidence}")
        log_ai_detection_to_csv(timestamp, detected_object, confidence)  # Log with current timestamp

    except Exception as e:
        print(f"[AI Detection Error] {e} in message '{ai_message_string}'")
