import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as mdates
import csv
import os
import re



#Data Storage
timestamps = []
temp_values = []
humidity_values = []
pressure_values = []
altitude_values = []

#CSV Setup for BME280
csv_filename = "bme280_data_log_400.csv"
if not os.path.exists(csv_filename):
	with open(csv_filename, mode='w', newline='') as file:
		writer = csv.writer(file)
		writer.writerow(["Timestamp", "Temperature (°C)", "Humidity (%)", "Pressure (hPa)", "Altitude (m)"])
#CSV Setup for AI Detection
ai_csv_filename = "ai_detection_log.csv"
if not os.path.exists(ai_csv_filename):
	with open(ai_csv_filename, mode='w', newline='') as file:
		writer = csv.writer(file)
		writer.writerow(["Timestamp", "Detected Object", "Confidence"])
	
def log_to_csv(timestamp, temp, humidity, pressure, altitude):
	with open(csv_filename, mode='a', newline="") as file:
		writer = csv.writer(file)
		writer.writerow([timestamp.strftime("%Y-%m-%d %H:%M:%S"), temp, humidity, pressure, altitude])

def log_ai_detection_to_csv(timestamp, detected_object, confidence):
	with open(ai_csv_filename, mode='a', newline='') as file:
		writer = csv.writer(file)
		writer.writerow([timestamp.strftime("%Y-%m-%d %H:%M:%S"), detected_object, confidence])

#Live Plot Setup
plt.ion()
fig, axs = plt.subplots(4, 1, sharex=True, figsize=(10, 10))
fig.suptitle('Real-Time BME280 Sensor Readings')

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
		ax.plot(timestamps, values, label=label, color='tab:blue')
		ax.legend(loc = 'upper left')
		ax.set_ylabel(label)
		ax.grid(True)
		
	axs[-1].set_xlabel('Time')
	fig.autofmt_xdate(rotation=45)
	plt.pause(0.1)
	
def parse_and_plot(data_line: str):
	try:
		parts = data_line.split(',')
		
		if len(parts) < 4:
			raise ValueError("Incomplete Data: Expected 4 parts, got {len(parts)} from '{data_line}'")
		
		temp = float(parts[0].split(':')[1].replace('°C', '').strip())
		pressure = float(parts[1].split(':')[1].replace('hPa', '').strip())
		humidity = float(parts[2].split(':')[1].replace('%', '').strip())
		altitude = float(parts[3].split(':')[1].replace('m', '').strip())
		
		timestamp = datetime.now()
		
		#Store and trim history
		timestamps.append(timestamp)
		temp_values.append(temp)
		humidity_values.append(humidity)
		pressure_values.append(pressure)
		altitude_values.append(altitude)
		
		#Limit history to the latest 50 points
		N = 50
		if len(timestamps) > N:
			timestamps.pop(0)
			temp_values.pop(0)
			humidity_values.pop(0)
			pressure_values.pop(0)
			altitude_values.pop(0)
			
		#Log to CSV
		log_to_csv(timestamp, temp, humidity, pressure, altitude)
		
		#Update live plot
		update_plot()
	except ValueError as ve:
		print(f"[Plotter] Data parsing error: {ve} for input '{data_line}'")
	except IndexError as ie:
		print(f"[Plotter] Data format error (missing colon or part): {ie} for input '{data_line}'")	
	except Exception as e:
		print(f"[Plotter] An unexpected error occurred during parsing and plotting: {e} for input '{data_line}'")

def handle_ai_detection(ai_message_string: str):
	try:
		content = ai_message_string.replace("AI_DETECTION: ", "").strip()
		parts = content.split(', ')
		
		if len(parts) < 2:
			raise ValueError(f"Incomplete AI Detection: Expected 2 parts, go {len(parts)} from '{ai_message_string}'")
		
		detected_object = parts[0].replace("Object: ", "").strip()
		confidence_str = parts[1].replace("Confidence: ", "").strip()
		confidence = float(confidence_str)
		
		timestamp = datetime.now()
		
		print(f"[AI Detector] Detected: '{detected_object}' with Confidence: {confidence:.2f} at {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
		log_ai_detection_to_csv(timestamp, detected_object, confidence)
		
	except ValueError as ve:
		print(f"[AI Detector] Parsing error: {ve} for input '{ai_message}'")
	except IndexError as ie:
		print(f"[AI Detector] Format error (missing parts: {ie} for input '{ai_message}'")
	except Exception as e:
		print(f"[AI Detector] An unexpected error: {e} for input '{ai_message}'")
