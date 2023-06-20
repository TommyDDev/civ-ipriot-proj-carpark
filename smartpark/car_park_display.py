import random
import threading
import time
import paho.mqtt.client as mqtt
from windowed_display import WindowedDisplay


class CarParkDisplay:
    """Provides a simple display of the car park status. This is a skeleton only. The class is designed to be customizable without requiring and understanding of tkinter or threading."""
    # determines what fields appear in the UI
    fields = ['Available bays', 'Temperature', 'At']

    def __init__(self):
        self.window = WindowedDisplay(
            'Moondalup', CarParkDisplay.fields)
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.connect(self.MQTT_HOST, self.MQTT_PORT)
        self.mqtt_client.subscribe(self.MQTT_TOPIC)
        self.mqtt_client.on_message = self.on_message_callback
        updater = threading.Thread(target=self.check_updates)
        updater.daemon = True
        updater.start()
        self.window.show()

    def on_message_callback(self, client, userdata, message):
        message_data = str(message.payload.decode("UTF-8"))
        # TODO: Parse the message_data to get values for available bays, temperature, and time
        # For now, we'll assume that message_data is a string of the format "available_bays,temperature,time"
        available_bays, temperature, time = message_data.split(',')
        field_values = dict(zip(CarParkDisplay.fields, [
            f'{int(available_bays):03d}',
            f'{int(temperature):02d}℃',
            time]))
        self.window.update(field_values)

    def check_updates(self):
        # TODO: This is where you should manage the MQTT subscription
        while True:
            # NOTE: Dictionary keys *must* be the same as the class fields
            field_values = dict(zip(CarParkDisplay.fields, [
                f'{random.randint(0, 150):03d}',
                f'{random.randint(0, 45):02d}℃',
                time.strftime("%H:%M:%S")]))
            # Pretending to wait on updates from MQTT
            time.sleep(random.randint(1, 10))
            # When you get an update, refresh the display.
            self.window.update(field_values)


if __name__ == '__main__':
    CarParkDisplay()
