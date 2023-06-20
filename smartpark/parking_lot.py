from config_parser import parse_config, get_config
from mqtt_device import MqttDevice
from datetime import datetime


class ParkingLot:
    def __init__(self, config):
        self.location = config['location']['name']
        self.total_spaces = config['location']['total_spaces']
        self.available_spaces = self.total_spaces
        self.temperature = None

        # Create the MQTT client
        self.mqtt_client = MqttDevice(config['mqtt'])
        self.mqtt_client.subscribe('sensor')
        self.mqtt_client.on_message = self.on_message

    def on_message(self, client, userdata, message):
        payload = message.payload.decode()
        if 'exit' in payload:
            self.car_exit()
        elif 'enter' in payload:
            self.car_enter()
        # Update temperature from payload
        temperature_str = payload.split(',')[-1]
        self.temperature = float(temperature_str)

    def car_enter(self):
        if self.available_spaces <= 0:
            print("No available spaces.")
        else:
            self.available_spaces -= 1
            self.publish_update(f"{self.available_spaces} spaces available.")


    def car_exit(self):
        if self.available_spaces >= self.total_spaces:
            print("Car park empty")
        else:
            self.available_spaces += 1
        self.publish_update(f"{self.available_spaces} spaces available.")


    def publish_update(self):
        # Create a message with the current state
        current_time = datetime.now().strftime('%H:%M')  # Format the datetime as string
        status_update = (
            f"Time: {current_time}, "
            f"Location: {self.location}, "
            f"Available Spaces: {self.available_spaces}, "
            f"Temperature: {self.temperature}"
            )
        self.mqtt_client.publish('display', status_update)


if __name__ == '__main__':
    # Read the config file
    filename = "config.toml"
    config = parse_config(get_config(filename))

    # Create a ParkingLot instance with the configuration
    parking_lot = ParkingLot(config)
    print("Carpark initialized")
    print("Carpark initialized")
