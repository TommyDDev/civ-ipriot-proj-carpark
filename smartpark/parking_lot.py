import json
import time
from mqtt_device import ConfigHelper, MqttDevice
from datetime import datetime
from constants import ENTER_EVENT, EXIT_EVENT


class ParkingLot:
    def __init__(self, filename):
        # Create the config helper
        config_helper = ConfigHelper(filename)

        # Extract broker, parking_lot and sensor configuration
        parking_lot_config = config_helper.get_parking_lot_config()
        sensor_config = config_helper.get_sensor_config()

        # Assign name, location, total spaces, temperature and sensor from the config
        self.name = parking_lot_config['name']
        self.location = parking_lot_config['location']
        self.total_spaces = parking_lot_config['total_spaces']
        self.available_spaces = self.total_spaces
        self.temperature = None
        self.sensor_topic = sensor_config['topic']
        self.status_topic = parking_lot_config['status_topic']

        # Create the MQTT client
        self.mqtt_client = MqttDevice(filename, self.name, self.location)

        self.mqtt_client.subscribe(self.sensor_topic)
        self.mqtt_client.add_message_handler(self.sensor_topic, self.on_message)

        # Start the MQTT client loop
        self.mqtt_client.client.loop_start()

    def on_message(self, payload):
        try:
            self.process_event(payload)  # replace the existing if/else with this
            self.temperature = payload['temperature']
        except Exception as e:
            print(f"Error processing message: {e}")

    def process_event(self, data):
        if data['event'] == EXIT_EVENT:
            self.car_exit()
        elif data['event'] == ENTER_EVENT:
            self.car_enter()
        else:
            print(f"Unknown event: {data['event']}")

    def car_enter(self):
        if self.available_spaces <= 0:
            print("No available spaces.")
        else:
            self.available_spaces -= 1
            self.publish_update()

    def car_exit(self):
        if self.available_spaces >= self.total_spaces:
            print("Car park empty")
        else:
            self.available_spaces += 1
        self.publish_update()

    def publish_update(self):
        # Create a message with the current state
        current_time = datetime.now().strftime('%H:%M')  # Format the datetime as string
        status_update = {
            "Time": current_time,
            "Location": self.location,
            "Available Spaces": self.available_spaces,
            "Temperature": self.temperature
        }
        # Convert the status_update to a JSON string
        status_update_json = json.dumps(status_update)
        print(f'Publishing message: {status_update_json}')  # Add this line
        topic = f"{self.mqtt_client.topic_root}/{self.location}/{self.status_topic}"
        self.mqtt_client.publish(topic, status_update_json)


if __name__ == '__main__':
    try:
        # Create a ParkingLot instance with the configuration
        parking_lot = ParkingLot("config.toml")
        print(" Car park initialized")

        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Graceful shutdown on Ctrl+C
        print(" Car park shutting down")
