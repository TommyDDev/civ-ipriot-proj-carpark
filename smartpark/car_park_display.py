import json
import threading
import queue
import datetime
from windowed_display import WindowedDisplay
from mqtt_device import MqttDevice, ConfigHelper
from config_parser import get_config

class CarParkDisplay:
    """Provides a simple display of the car park status. The class is designed to be customizable without requiring an understanding of tkinter or threading."""
    # determines what fields appear in the UI
    fields = ['Available Spaces', 'Temperature', 'At']

    def __init__(self, filename):
        self.message_queue = queue.Queue()
        self.window = WindowedDisplay('Moondalup', CarParkDisplay.fields)

        # Create the config helper
        config_helper = ConfigHelper(filename)

        # Extract broker and parking lot configuration
        broker_config = config_helper.get_broker_config()
        parking_lot_config = config_helper.get_parking_lot_config()
        display_config = config_helper.get_display_config()

        # Create and connect the MQTT client
        self.mqtt_client = MqttDevice(filename, display_config['name'], display_config['location'])

        topic = f"{self.mqtt_client.topic_root}/{self.mqtt_client.location}/status"
        self.mqtt_client.client.on_message = self.on_message_callback
        self.mqtt_client.subscribe(topic)

        # Initialize last received field values
        self.last_received_values = {
            'Available Spaces': '000',
            'Temperature': '00℃',
            'At': '00:00'
        }

        # Start the MQTT client loop
        self.mqtt_client.client.loop_start()

        self.window.show()

        # Create a thread that will update the GUI with new messages
        self.gui_updater_thread = threading.Thread(target=self.gui_updater, daemon=True)
        self.gui_updater_thread.start()

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
        while True:
            # Get a new message from the queue
            message = self.message_queue.get()

            print(f'Parsed data: {message}')

            if 'Available Spaces' in message:
                self.last_received_values['Available Spaces'] = f'{int(message["Available Spaces"]):03d}'
            if 'Temperature' in message and message['Temperature'] is not None:
                self.last_received_values['Temperature'] = f'{int(message["Temperature"]):02d}℃'
            else:
                self.last_received_values['Temperature'] = 'N/A'

            # Update the time every time a message is received
            self.last_received_values['At'] = datetime.datetime.now().strftime("%H:%M")

            # Update the display with the field_values
            print(f'Updating display with values: {self.last_received_values}')
            self.window.update(self.last_received_values)


if __name__ == '__main__':
    car_park_display = None  # Initialize car_park_display
    try:
        # Read the config file
        filename = "config.toml"
        config = get_config(filename)
        car_park_display = CarParkDisplay(config)  # Create an instance of CarParkDisplay
    finally:
        # Stop the loop before the program ends
        if car_park_display is not None:  # Check if car_park_display is not None
            car_park_display.mqtt_client.client.loop_stop()
