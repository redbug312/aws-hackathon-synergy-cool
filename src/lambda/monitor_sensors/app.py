import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class Sensor:
    def __init__(self, temperature: float, relative_humidity: float):
        self.temperature = temperature
        self.relative_humidity = relative_humidity

    def to_dict(self):
        return {
            'temperature': self.temperature,
            'relative_humidity': self.relative_humidity,
        }


def bad_request(message: str):
    return {
        'statusCode': 400,
        'body': json.dumps({
            'error': message,
        }),
    }


def lambda_handler(event, context):
    path_parameters = event.get('pathParameters', {})
    sensor_id = path_parameters.get('sensor_id', None)
    logger.info(f'API queries the sensor {sensor_id}')

    if session_id is None:
        return bad_request('missing path parameter session_id')

    response = Sensor(30.0, 50.0).to_dict()
    logger.info(f'API replies the sensor data {response}')

    return {
        'statusCode': 200,
        'body': json.dumps(response),
    }
