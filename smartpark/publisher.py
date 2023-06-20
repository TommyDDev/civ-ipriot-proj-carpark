import time
from datetime import datetime
import paho.mqtt.client as mqtt

MQTT_HOST = "localhost"
MQTT_PORT = 1883
MQTT_KEEP_ALIVE = 300

MQTT_CLIENT_NAME = "buzz-off"
MQTT_TOPIC = "test/buzz"

client = mqtt.Client(MQTT_CLIENT_NAME)
client.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEP_ALIVE)

print(f"Sending message to MQTT broker {MQTT_HOST} on port {MQTT_PORT}")
print(f"with the topic {MQTT_TOPIC}...")

message_to_send = "Hello..."

while True:
    time.sleep(5)
    now = datetime.now()
    client.publish(MQTT_TOPIC, message_to_send)
