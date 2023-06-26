import unittest
import json
from unittest.mock import MagicMock, Mock, patch
from mqtt_device import MqttDevice, ConfigHelper
from parking_lot import ParkingLot
from constants import ENTER_EVENT, EXIT_EVENT


class TestMqttDevice(unittest.TestCase):
    def setUp(self):
        self.filename = 'test.toml'
        self.name = 'test_device'
        self.location = 'test_location'
        self.config = {
            'broker': 'test_broker',
            'port': 1234,
            'topic-root': 'test_topic_root',
            'topic-qualifier': 'test_topic_qualifier',
        }

        self.parking_lot_config = {
            'name': 'Moondalup City Square Parking',
            'location': 'Moondalup',
            'total_spaces': 192,
            'status_topic': 'status'
        }

        self.sensor_config = {'topic': 'test_sensor_topic'}

        with patch('tomli.load') as mock_tomli_load:
            mock_tomli_load.return_value = {
                'broker': self.config,
                'sensor': self.sensor_config,
                'parking_lot': self.parking_lot_config,
            }
            with patch('mqtt_device.paho.Client') as MockMqttClient:
                self.mqtt_device = MqttDevice(self.filename, self.name, self.location)

        self.mqtt_device.client.reconnect = MagicMock()


    def test_initialization(self):
        self.assertIsInstance(self.mqtt_device.client, MagicMock)
        self.assertEqual(self.mqtt_device.client.on_connect, self.mqtt_device.on_connect)
        self.assertEqual(self.mqtt_device.client.on_disconnect, self.mqtt_device.on_disconnect_callback)
        self.assertEqual(self.mqtt_device.client.on_message, self.mqtt_device.on_message)
        self.mqtt_device.client.connect.assert_called_once_with(self.config['broker'], self.config['port'])

    def test_publish(self):
        self.mqtt_device.publish('test_topic', 'test_message')
        self.mqtt_device.client.publish.assert_called_once_with('test_topic', 'test_message')

    def test_subscribe(self):
        self.mqtt_device.subscribe('test_topic')
        self.mqtt_device.client.subscribe.assert_called_once_with('test_topic')
        self.mqtt_device.client.loop_start.assert_called_once()

    def test_add_message_handler(self):
        mock_handler = Mock()
        self.mqtt_device.add_message_handler('test_topic', mock_handler)

        self.assertEqual(self.mqtt_device.client.message_callback_add.call_count, 1)

        # Get the args with which it was called
        args, kwargs = self.mqtt_device.client.message_callback_add.call_args

        # The first argument should be the topic
        self.assertEqual(args[0], 'test_topic')

        # The second argument should be a function (the wrapped handler)
        self.assertTrue(callable(args[1]))

        # Now, we test if the wrapped function behaves as expected
        mock_payload = MagicMock()
        mock_payload.decode.return_value = json.dumps({"key": "value"})
        mock_mqtt_msg = Mock()
        mock_mqtt_msg.payload = mock_payload.decode()
        args[1](None, None, mock_mqtt_msg)  # Call the wrapped function

        # The handler should be called with the dictionary resulting from parsing the JSON string
        mock_handler.assert_called_once_with({"key": "value"})

    def test_on_disconnect_callback(self):
        self.mqtt_device.on_disconnect_callback(None, None, None)
        self.mqtt_device.client.reconnect.assert_called_once()


class TestConfigHelper(unittest.TestCase):
    def setUp(self):
        self.filename = 'test.toml'
        self.config = {
            'broker': {
                'broker': '127.0.0.1',
                'port': 1883,
                'topic-root': 'carpark',
                'topic-qualifier': 'controller'
            },
            'parking_lot': {
                'name': 'Moondalup City Square Parking',
                'location': 'Moondalup',
                'total_spaces': 192,
                'status_topic': 'status'
            },
            'sensor': {
                'name': 'parking_lot_sensor',
                'topic': 'sensor'
            },
            'display': {
                'name': 'parking_lot_display',
                'location': 'Moondalup'
            }
        }

        with patch('tomli.load') as mock_tomli_load:
            mock_tomli_load.return_value = self.config
            self.config_helper = ConfigHelper(self.filename)


    def test_get_broker_config(self):
        broker_config = self.config_helper.get_broker_config()
        self.assertEqual(broker_config, self.config['broker'])

    def test_get_parking_lot_config(self):
        parking_lot_config = self.config_helper.get_parking_lot_config()
        self.assertEqual(parking_lot_config, self.config['parking_lot'])

    def test_get_sensor_config(self):
        sensor_config = self.config_helper.get_sensor_config()
        self.assertEqual(sensor_config, self.config['sensor'])

    def test_get_display_config(self):
        display_config = self.config_helper.get_display_config()
        self.assertEqual(display_config, self.config['display'])



class TestParkingLot(unittest.TestCase):
    def setUp(self):
        self.filename = 'test.toml'

        with patch('parking_lot.ConfigHelper') as mock_config_helper, \
                patch('parking_lot.MqttDevice') as mock_mqtt_device:
            mock_config_helper.return_value.get_parking_lot_config.return_value = {
                'name': 'test_name',
                'location': 'test_location',
                'total_spaces': 10,
                'status_topic': 'test_status_topic'
            }
            mock_config_helper.return_value.get_sensor_config.return_value = {
                'topic': 'test_sensor_topic'
            }
            mock_mqtt_device.return_value = MagicMock()

            self.parking_lot = ParkingLot(self.filename)


    def test_process_event(self):
        enter_event_data = {'event': ENTER_EVENT}
        self.parking_lot.process_event(enter_event_data)
        self.assertEqual(self.parking_lot.available_spaces, self.parking_lot.total_spaces - 1)

        exit_event_data = {'event': EXIT_EVENT}
        self.parking_lot.process_event(exit_event_data)
        self.assertEqual(self.parking_lot.available_spaces, self.parking_lot.total_spaces)

    @patch('json.dumps')
    def test_publish_update(self, mock_json_dumps):
        self.parking_lot.publish_update()
        self.parking_lot.mqtt_client.publish.assert_called_once()
        mock_json_dumps.assert_called_once()


if __name__ == '__main__':
    unittest.main()
