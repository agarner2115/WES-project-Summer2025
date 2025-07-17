# Transmitter
import time
import serial
from shared_resources import data_queue, ai_data_queue, stop_event
from bme280Data import BME_running, read_bme280, calculate_altitude

# Uncomment suitable line for your Pi and comment the other which is not required 
'''For Raspberry Pi 4 & 3'''
lora = serial.Serial(port='/dev/ttyS0', baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)

def loraTX_running(stop_event):
    try:
        while not stop_event.is_set():
                message_sent = False
                
                if not ai_data_queue.empty():
                        ai_data_to_send = ai_data_queue.get()
                        b = bytes(ai_data_to_send, 'utf-8')
                        lora.write(b)
                        print(f"[LoRa TX] Sent AI Data: {ai_data_to_send}")
                        message_sent = True
                        
                elif not data_queue.empty():
                        sensor_data_obj = data_queue.get()
                        print("SENDING:", {sensor_data_obj})

                        data_to_send = (
                                f"Temperature: {sensor_data_obj.temperature:.2f}°C, "
                                f"Pressure: {sensor_data_obj.pressure:.2f} hPa, "
                                f"Humidity: {sensor_data_obj.humidity:.2f}%, "
                                f"Altitude: {sensor_data_obj.altitude:.2f} m"
                        )
             
                        #Format the data as a string
                        b = bytes(data_to_send, 'utf-8')  #Convert string into bytes
                        lora.write(b)  #Send the data to the other LoRa
                        print(f"Sent BME280 Data: {data_to_send}")
                        message_sent = True
                if not message_sent:
                        time.sleep(1)

    except Exception as e:
        print(f"[LoRa TX] Error: {e}")

if __name__ == "__main__":
        local_stop_event = threading.Event()
        try:
                loraTX_running(local_stop_event)
        except KeyboardInterrupt:
                print("Main script received KeyboardInterrupt.")
                local_stop_event.set()
        print("Transmitter script finished.")
