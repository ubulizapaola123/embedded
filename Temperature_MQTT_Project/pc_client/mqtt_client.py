import serial
import time
# pyrefly: ignore [missing-import]
import paho.mqtt.client as mqtt

# ==========================================
# CONFIGURATION
# ==========================================
# Trade Code: SPE
SERIAL_PORT = 'COM8'         # IMPORTANT: Change this to match your Arduino's COM port in Device Manager!
BAUD_RATE = 9600             # Must match the Serial.begin() in Arduino code

# MQTT Communication Names & Details
MQTT_BROKER = "157.173.101.159"
MQTT_PORT = 24077

MQTT_USERNAME = "emg77"
MQTT_PASSWORD = "emg77"

MQTT_TOPIC = "spe/uwase_teta_paola/temperature"

mqtt_client = mqtt.Client()

mqtt_client.username_pw_set(
    MQTT_USERNAME,
    MQTT_PASSWORD
)

mqtt_client.on_connect = on_connect
mqtt_client.on_publish = on_publish

mqtt_client.connect(
    MQTT_BROKER,
    MQTT_PORT,
    60
)

mqtt_client.loop_start()

# ==========================================
# MQTT CALLBACKS
# ==========================================
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[MQTT] Successfully connected to broker at {MQTT_BROKER}")
    else:
        print(f"[MQTT] Failed to connect, return code {rc}")

def on_publish(client, userdata, mid):
    # This callback fires when a message is successfully sent to the broker
    pass 

# ==========================================
# SETUP MQTT CLIENT
# ==========================================
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_publish = on_publish

try:
    print("[SYSTEM] Connecting to MQTT broker...")
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start() # Start the background thread for network traffic
except Exception as e:
    print(f"[ERROR] Could not connect to MQTT broker: {e}")
    exit(1)

# ==========================================
# SETUP SERIAL CONNECTION
# ==========================================
try:
    print(f"[SYSTEM] Opening Serial port {SERIAL_PORT}...")
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2) # Give the Arduino 2 seconds to reset after opening the serial port
except Exception as e:
    print(f"[ERROR] Could not open Serial port: {e}")
    print("[HINT] Did you change SERIAL_PORT to match your Arduino (e.g., COM3, COM4)?")
    print("[HINT] Make sure the Arduino IDE Serial Monitor is CLOSED.")
    mqtt_client.loop_stop()
    exit(1)

print("\n[SYSTEM] Setup complete. Waiting for incoming Arduino data...\n")
print("-" * 50)

# ==========================================
# MAIN LOOP: Read Serial -> Publish MQTT -> Display Real-time
# ==========================================
try:
    while True:
        # Check if there is data waiting to be read from the Arduino
        if ser.in_waiting > 0:
            # Read the line, decode the bytes to a string, and strip extra whitespace/newlines
            line = ser.readline().decode('utf-8').strip()
            
            if line:
                try:
                    # Convert the string to a float to ensure it's valid temperature data
                    temperature = float(line)
                    
                    # 1. Display incoming values in real time on PC console
                    print(f"[{time.strftime('%H:%M:%S')}] Received: {temperature} °C | Publishing to '{MQTT_TOPIC}'...")
                    
                    # 2. Publish to MQTT broker
                    mqtt_client.publish(MQTT_TOPIC, str(temperature))
                    
                except ValueError:
                    # If the data isn't a clean number (e.g., startup noise), ignore it
                    print(f"[WARNING] Received unparseable data from Serial: {line}")
                    
        # Small sleep to prevent 100% CPU usage
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n[SYSTEM] Ctrl+C detected. Shutting down gracefully...")
finally:
    # Cleanup resources
    ser.close()
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
    print("[SYSTEM] Disconnected.")
