import tkinter as tk
import json
import random
from constants import ENTER_EVENT, EXIT_EVENT
from mqtt_device import MqttDevice, ConfigHelper


class CarDetector:
    def __init__(self, filename):
        config_helper = ConfigHelper(filename)

        broker_config = config_helper.get_broker_config()
        sensor_config = config_helper.get_sensor_config()
        parking_lot_config = config_helper.get_parking_lot_config()

        self.mqtt_client = MqttDevice(filename, sensor_config['name'], parking_lot_config['location'])
        self.sensor_topic = sensor_config['topic']

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
        return random.randint(18, 22)

    def incoming_car(self):
        self.publish_event(ENTER_EVENT)

    def outgoing_car(self):
        self.publish_event(EXIT_EVENT)

    def publish_event(self, event):
        data = {'event': event, 'temperature': self.temperature}
        message = json.dumps(data)
        print(f'Publishing message: {message}')
        self.mqtt_client.publish(self.sensor_topic, message)


if __name__ == '__main__':
    car_detector = None
    config_filename = "config.toml"
    try:
        car_detector = CarDetector(config_filename)
        car_detector.mqtt_client.client.loop_start()
        while True:
            pass
    except KeyboardInterrupt:
        print("Exiting due to keyboard interrupt")
        if car_detector:
            car_detector.mqtt_client.client.loop_stop()
    except Exception as e:
        print(f"Exiting due to error: {e}")
        if car_detector:
            car_detector.mqtt_client.client.loop_stop()
