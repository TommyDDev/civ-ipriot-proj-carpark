import unittest
from unittest.mock import patch, MagicMock
from car_park_display import CarParkDisplay


class TestCarParkDisplay(unittest.TestCase):

    @patch('car_park_display.MqttDevice')
    @patch('car_park_display.WindowedDisplay')
    @patch('car_park_display.ConfigHelper')
    def test_init(self, mock_config_helper, mock_windowed_display, mock_mqtt_device):
        mock_config_helper.return_value.get_broker_config.return_value = {}
        mock_config_helper.return_value.get_parking_lot_config.return_value = {}
        mock_config_helper.return_value.get_display_config.return_value = {'name': 'test_name', 'location': 'test_location'}

        mock_mqtt_device.return_value = MagicMock()
        mock_windowed_display.return_value = MagicMock()

        car_park_display = CarParkDisplay('filename')

        mock_config_helper.assert_called_once_with('filename')
        mock_config_helper.return_value.get_broker_config.assert_called_once()
        mock_config_helper.return_value.get_parking_lot_config.assert_called_once()
        mock_config_helper.return_value.get_display_config.assert_called_once()

        mock_mqtt_device.assert_called_once()
        mock_windowed_display.assert_called_once()

        self.assertIsNotNone(car_park_display.message_queue)
        self.assertIsNotNone(car_park_display.last_received_values)


if __name__ == '__main__':
    unittest.main()
