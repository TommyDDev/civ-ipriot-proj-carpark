import json
import time
import threading
import queue
import datetime
from windowed_display import WindowedDisplay
from mqtt_device import MqttDevice, ConfigHelper


class CarParkDisplay:
    fields = ['Available Spaces', 'Temperature', 'At']

    def __init__(self, filename: str):
        self.message_queue = queue.Queue()
        self.window = WindowedDisplay('Moondalup', CarParkDisplay.fields)
        self.mqtt_client = None
        self.mqtt_thread = None
        self.main_thread = None

        self._init(filename)

        self.gui_updater()

        self.mqtt_thread = threading.Thread(target=self.start_mqtt,
                                            args=(filename, self.display_config['name'],
                                                  self.display_config['location']))
        self.mqtt_thread.start()

    def _init(self, filename: str):
        config_helper = ConfigHelper(filename)

        self.broker_config = config_helper.get_broker_config()
        self.parking_lot_config = config_helper.get_parking_lot_config()
        self.display_config = config_helper.get_display_config()

        self.last_received_values = {
            'Available Spaces': '000',
            'Temperature': '00℃',
            'At': '00:00'
        }

    def start_gui(self):
        self.window.window.protocol("WM_DELETE_WINDOW", self.on_close_window)
        self.window.show()

    def on_close_window(self):
        print("Window close signal received, stopping program...")
        self.stop_program()

    def stop_program(self):
        if self.mqtt_client:
            self.mqtt_client.client.loop_stop()
            self.mqtt_client.client.disconnect()
        self.window.window.quit()

    def start_mqtt(self, filename, name, location):
        self.mqtt_client = MqttDevice(filename, name, location)
        topic = f"{self.mqtt_client.topic_root}/{self.mqtt_client.location}/status"
        self.mqtt_client.client.on_message = self.on_message_callback
        self.mqtt_client.client.on_disconnect = self.on_disconnect_callback
        self.mqtt_client.subscribe(topic)

        self.mqtt_client.client.loop_start()

    def on_disconnect_callback(self, client, userdata, rc):
        if rc != 0:
            print("Unexpected MQTT disconnection. Attempting to reconnect.")
            time.sleep(5)
            self.mqtt_client.reconnect()

    def on_message_callback(self, client, userdata, message):
        print(f"Received a message: {message.payload}")
        print(f"Received message: {message.payload.decode('UTF-8')}")
        try:
            message_payload = str(message.payload.decode("UTF-8"))
            data = json.loads(message_payload)
            if 'event' not in data:
                self.message_queue.put(data)
            else:
                print("Received message with 'event' field")
        except Exception as e:
            print(f"Error processing message: {e}")

    def gui_updater(self):
        def check_queue():
            if not self.message_queue.empty():
                message = self.message_queue.get()
                self.update_gui_with_message(message)
            self.window.window.after(100, check_queue)

        check_queue()

    def update_gui_with_message(self, message):
        print(f'Parsed data: {message}')

        if 'Available Spaces' in message:
            self.last_received_values['Available Spaces'] = f'{int(message["Available Spaces"]):03d}'
        if 'Temperature' in message and message['Temperature'] is not None:
            self.last_received_values['Temperature'] = f'{int(message["Temperature"]):02d}℃'
        else:
            self.last_received_values['Temperature'] = 'N/A'

        self.last_received_values['At'] = datetime.datetime.now().strftime("%H:%M")

        print(f'Updating display with values: {self.last_received_values}')
        self.window.update(self.last_received_values)


if __name__ == '__main__':
    filename = "config.toml"
    car_park_display = CarParkDisplay(filename)
    car_park_display.start_gui()
