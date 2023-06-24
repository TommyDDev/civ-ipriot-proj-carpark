import paho.mqtt.client as paho
import json
from config_parser import parse_config, get_config


class ConfigHelper:
    def __init__(self, filename):
        self.config = get_config(filename)

    def get_broker_config(self):
        return parse_config(self.config, 'broker')

    def get_parking_lot_config(self):
        return parse_config(self.config, 'parking_lot')

    def get_sensor_config(self):
        return parse_config(self.config, 'sensor')

    def get_display_config(self):
        return parse_config(self.config, 'display')


class MqttDevice:
    def __init__(self, filename, name, location):
        # Create config helper and extract configurations
        config_helper = ConfigHelper(filename)
        broker_config = config_helper.get_broker_config()
        sensor_config = config_helper.get_sensor_config()
        parking_lot_config = config_helper.get_parking_lot_config()

        # Assign location and sensor from the config
        self.name = name
        self.location = location
        self.status_topic = parking_lot_config['status_topic']

        # Define topic components:
        self.topic_root = broker_config['topic-root']
        self.topic_qualifier = broker_config['topic-qualifier']
        self.sensor_topic = sensor_config['topic']
        self.topic = self._create_topic_string()

        # Configure broker
        self.broker = broker_config['broker']
        self.port = broker_config['port']

        # initialise a paho client and bind it to the object (has-a)
        # Here we are providing the client name as an argument to the paho.Client function
        self.client = paho.Client(self.name)

        # Set up the callback methods
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

        self.client.connect(self.broker, self.port)
        self.message_handlers = {}  # Handlers for different messages


    def _create_topic_string(self):
        return f"{self.topic_root}/{self.location}/{self.name}/{self.topic_qualifier}"

    def publish(self, topic, message):
        self.client.publish(topic, message)

    def subscribe(self, topic):
        self.client.subscribe(topic)
        self.client.loop_start()

    def on_message(self, client, userdata, message):
        print(f"Received message: {message.payload.decode()} on topic {message.topic}")
        payload = json.loads(message.payload.decode())
        handler = self.message_handlers.get(message.topic)
        if handler:
            handler(payload)
        else:
            print(f"No handler for topic {message.topic}")

    def process_message(self, message, topic):
        pass  # Now empty, messages are handled in on_message

    def add_message_handler(self, topic, handler):
        def _message_handler(client, userdata, message):
            payload = json.loads(message.payload)
            handler(payload)

        self.client.message_callback_add(topic, _message_handler)

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")

    def on_disconnect(self, client, userdata, rc):
        print("Disconnected from the broker")
