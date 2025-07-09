import threading
import os
import sys
from queue import Empty
import csv
import time

#Shared data queue
data_queue = queue.Queue()

#Initialize I2C (do this once, globally)
i2c_lock = threading.Lock() # Lock for I2C communication

#Import functions from other modules
from shared_resources import data_queue
from bme280Data import BME_running
from lora_transmitter import loraTX_running
from object_detection import camera_running

CSV_FILENAME = 'bme280_log.csv'

def log_to_csv(data):
    file_exists = os.path.isfile(CSV_FILENAME)
    with open(CSV_FILENAME, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Timestamp', 'Temperature (°C)', 'Humidity (%)', 'Pressure (hPa)', 'Altitude (m)'])
        writer.writerow([
            data.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            f"{data.temperature:.2f}",
            f"{data.humidity:.2f}",
            f"{data.pressure:.2f}",
            f"{data.altitude:.2f}"
        ])

def csv_logger(stop_event):
    try:
        while not stop_event.is_set():
            try:
                data = data_queue.get(timeout=1)
                log_to_csv(data)
            except Empty:
                continue
    except Exception as e:
        print(f"[CSV Logger] Error: {e}")

def main():
    #Create threads for each task
    bme_thread = threading.Thread(target=BME_running, args=(stop_event,), name="BME280 Thread")
    loraTX_thread = threading.Thread(target=loraTX_running, args=(stop_event,), name="LoRa TX Thread")
    camera_thread = threading.Thread(target=camera_running, args=(stop_event,), name="Camera Thread")
    logger_thread = threading.Thread(target=csv_logger, args=(stop_event,), name="CSV Logger Thread")

    #Start threads
    bme_thread.start()
    lora_tx_thread.start()
    camera_thread.start()
    logger_thread.start()

    try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Stopping system...")
            stop_event.set()
    
    #Wait for threads to complete
    bme_thread.join()
    lora_tx_thread.join()
    camera_thread.join()
    print("System shutdown complete.")

if __name__ == "__main__":
    main()
