import paho.mqtt.client as mqtt

MQTT_HOST = "localhost"
MQTT_PORT = 1883
MQTT_KEEP_ALIVE = 300

MQTT_CLIENT_NAME = "buzz-on"
MQTT_TOPIC = "test/buzz"

client = mqtt.Client(MQTT_CLIENT_NAME)
client.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEP_ALIVE)

client.subscribe(MQTT_TOPIC)


def on_message_callback(client, userdata, message):
	message_data = str(message.payload.decode("UTF-8"))
	print(f"Recieved: {message_data}")
	print(f"Topic: {message.topic}")
	print(f"QoS: {message.qos}")
	print(f"Retain: {message.retain}")


client.on_message = on_message_callback

print(f"{MQTT_CLIENT_NAME} is listening on port {MQTT_PORT} for messages with the topic {MQTT_TOPIC}")

client.loop_forever()
