import tkinter as tk
import paho.mqtt.client as mqtt
import json
import random
from constants import ENTER_EVENT, EXIT_EVENT
from mqtt_device import MqttDevice, ConfigHelper
from config_parser import parse_config, get_config


class CarDetector:
    """Provides a couple of simple buttons that can be used to represent a sensor detecting a car. This is a skeleton
    only."""

    def __init__(self, filename):
        # Create the config helper
        config_helper = ConfigHelper(filename)

        # Extract broker, sensor, and parking lot configuration
        broker_config = config_helper.get_broker_config()
        sensor_config = config_helper.get_sensor_config()
        parking_lot_config = config_helper.get_parking_lot_config()  # New line

        # Create and connect the MQTT client, using the location from the parking lot config
        self.mqtt_client = MqttDevice(filename, sensor_config['name'], parking_lot_config['location'])
        self.sensor_topic = sensor_config['topic']

        # Start the MQTT client loop
        self.mqtt_client.client.loop_start()

        self.root = tk.Tk()
        self.root.title("Car Detector ULTRA")

        self.btn_incoming_car = tk.Button(
            self.root, text='🚘 Incoming Car', font=('Arial', 50), cursor='right_side', command=self.incoming_car)
        self.btn_incoming_car.pack(padx=10, pady=5)
        self.btn_outgoing_car = tk.Button(
            self.root, text='Outgoing Car 🚘', font=('Arial', 50), cursor='bottom_left_corner',
            command=self.outgoing_car)
        self.btn_outgoing_car.pack(padx=10, pady=5)

        print('sensor initialised')

        self.root.mainloop()

    @property
    def temperature(self):
        """Returns the current temperature"""
        return random.randint(18, 22)

    def incoming_car(self):
        self.publish_event(ENTER_EVENT)

    def outgoing_car(self):
        self.publish_event(EXIT_EVENT)

    def publish_event(self, event):
        # Create a dictionary representing the car entering and the current temperature
        data = {'event': event, 'temperature': self.temperature}
        # Convert the dictionary to a JSON string
        message = json.dumps(data)
        print(f'Publishing message: {message}')
        # Publish the message
        self.mqtt_client.publish(self.sensor_topic, message)


if __name__ == '__main__':
    car_detector = None
    config_filename = "config.toml"
    try:
        car_detector = CarDetector(config_filename)  # Create an instance of CarDetector
        car_detector.mqtt_client.client.loop_start()  # Start the loop
        while True:
            pass  # Keep the program running
    except KeyboardInterrupt:
        print("Exiting due to keyboard interrupt")
        if car_detector:
            car_detector.mqtt_client.client.loop_stop()  # Stop the loop
    except Exception as e:
        print(f"Exiting due to error: {e}")
        if car_detector:
            car_detector.mqtt_client.client.loop_stop()  # Stop the loop
