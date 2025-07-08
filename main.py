import threading
import os
import sys
import queue
import time

#Shared data queue
data_queue = queue.Queue()

#Initialize I2C (do this once, globally)
i2c_lock = threading.Lock() # Lock for I2C communication

#Import functions from other modules
from bme280Data import read_bme280, calculate_altitude, BME_running
from lora_transmitter import loraTX_running
from object_detection import camera_running

def main():
    #Create threads for each task
    #bme_thread = threading.Thread(target=BME_running, args=(data_queue,), name="BME280 Thread")
    bme_thread = threading.Thread(target=BME_running, name="BME280 Thread")
    lora_tx_thread = threading.Thread(target=loraTX_running, name="LoRa Transmitter Thread")
    camera_thread = threading.Thread(target=camera_running, name="Camera Thread")

    #Start threads
    bme_thread.start()
    lora_tx_thread.start()
    camera_thread.start()

    #Wait for threads to complete
    bme_thread.join()
    lora_tx_thread.join()
    camera_thread.join()

if __name__ == "__main__":
    main()
