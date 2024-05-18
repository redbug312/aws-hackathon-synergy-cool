import base64
import boto3
from decimal import Decimal
import json
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

dynamodb = boto3.resource('dynamodb')
SENSOR_DATABASE_TABLE = os.environ.get('SENSOR_DATABASE_TABLE')
table = dynamodb.Table(SENSOR_DATABASE_TABLE)


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


def handle_api_event(event):
    logger.debug(f'RESTful API triggered event {event}')
    path_parameters = event.get('pathParameters', {})
    sensor_id = path_parameters.get('sensor_id', None)
    logger.info(f'API queries the sensor {sensor_id}')

    if sensor_id is None:
        return bad_request('missing path parameter session_id')

    response = Sensor(30.0, 50.0).to_dict()
    logger.info(f'API replies the sensor data {response}')

    return {
        'statusCode': 200,
        'body': json.dumps(response),
    }


def handle_kinesis_event(event):
    logger.debug(f'Kinesis stream triggered event {event}')
    assert len(event['Records']) > 0

    record = event['Records'][-1]
    data = base64.b64decode(record['kinesis']['data']).decode('utf-8')
    payload = json.loads(data, parse_float=Decimal)
    logger.info(f'Kinesis pushed payload {payload}')

    key = {
        "id": str(payload["sensor_id"]),
    }
    attributes = {
        "temperature": {
            "Value": payload["temperature"],
            "Action": "PUT"
        },
        "humidity": {
            "Value": payload["humidity"],
            "Action": "PUT"
        },
        "timestamp": {
            "Value": payload["timestamp"],
            "Action": "PUT"
        }
    }
    table.update_item(Key=key, AttributeUpdates=attributes)

    return {
        'statusCode': 200,
        'body': 'records uploaded to database',
    }


def lambda_handler(event, context):
    if 'httpMethod' in event:
        return handle_api_event(event)
    elif 'Records' in event and 'kinesis' in event['Records'][0]:
        return handle_kinesis_event(event)
    else:
        return bad_request("unknown event source")
