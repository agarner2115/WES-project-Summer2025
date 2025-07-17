import time
import serial
import threading
from shared_resources import data_queue, ai_data_queue, stop_event

# Setup serial port (adjust device if needed)
lora = serial.Serial(
    port='/dev/ttyS0',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

def loraTX_running(stop_event):
    print(f"[LoRa TX] Starting. Serial port open: {lora.is_open}")
    try:
        while not stop_event.is_set():
            message_sent = False
            print(f"[DEBUG TX] data_queue size: {data_queue.qsize()}")
            print(f"[DEBUG TX] ai_data_queue size: {ai_data_queue.qsize()}")
            print(f"[TX] data_queue id: {id(data_queue)}")


            # Send AI data if available
            if not ai_data_queue.empty():
                ai_data_to_send = ai_data_queue.get()
                msg = ai_data_to_send + '\n'  # Append newline
                lora.write(msg.encode('utf-8'))
                print(f"[LoRa TX] Sent AI Data: {ai_data_to_send}")
                message_sent = True

            # Otherwise send sensor data if available

            elif not data_queue.empty():
                sensor_data_obj = data_queue.get()
                data_to_send = (
                    f"Temperature: {sensor_data_obj.temperature:.2f}°C, "
                    f"Pressure: {sensor_data_obj.pressure:.2f} hPa, "
                    f"Humidity: {sensor_data_obj.humidity:.2f}%, "
                    f"Altitude: {sensor_data_obj.altitude:.2f} m\n"
                )
                lora.write(data_to_send.encode('utf-8'))
                print(f"[LoRa TX] Sent BME280 Data: {data_to_send.strip()}")
                message_sent = True

            # If no data, wait a bit before checking again
            if not message_sent:
                time.sleep(1)

    except Exception as e:
        print(f"[LoRa TX] Error: {e}")
    finally:
        if lora.is_open:
            lora.close()
            print("[LoRa TX] Serial port closed.")

if __name__ == "__main__":
    local_stop_event = threading.Event()
    try:
        loraTX_running(local_stop_event)
    except KeyboardInterrupt:
        print("[LoRa TX] KeyboardInterrupt received, stopping.")
        local_stop_event.set()
